import datetime
from operator import itemgetter
import os
import re
import shutil
from fastapi import APIRouter, Depends, Form, Query, UploadFile, HTTPException
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from src.middlewares.jwt_middleware import get_current_user
from src.schemas.history_query_dto import HistoryQueryDto
from src.schemas.req_to_ai_dto import ReqToAiDto
from src.services.collections_service import CollectionsService, get_collections_service
from langchain_community.document_loaders import PyPDFLoader
from typing import Annotated, Iterable
from langchain_core.documents import Document
from dotenv import load_dotenv
from src.services.ai_service import AIService, get_ai_service
from src.models.collections_model import Collections
from tortoise.transactions import in_transaction
from src.models.users_model import Users
from src.models.documents_model import Documents
from src.models.chat_history_model import ChatHistory
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from src.services.chat_history_service import ChatHistoryService, get_chat_history_service
from src.services.users_service import get_users_service, UsersService
from src.schemas.query_dto import QueryDto


load_dotenv()

chat = APIRouter(
  prefix= "/chat", 
  tags=["collections"], 
  responses={404: {"description": "Not Found"}}
)

async def upload_pdf(file: UploadFile) -> str | None:
  os.makedirs("files", exist_ok=True)  # 폴더 없으면 생성

  with open(f"files/{file.filename}", "wb") as dest_file: 
    stream_obj = file.file
    shutil.copyfileobj(stream_obj, dest_file)

  filename = file.filename
  return filename

def py_load_file(path: str) -> list[Document]: # text 
  loader = PyPDFLoader(path)
  pages = loader.load()
  return pages

def tokenaize_text(data: Iterable): # 토큰 수 기준 텍스트 분할
  splitter = CharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=600,
    chunk_overlap=200,
    encoding_name='cl100k_base'
  )
  docs = splitter.split_documents(data)
  page = []
  for doc in docs:
    content = doc.page_content
    page.append(content)
  return page

def split_recursive(data: list[Document]) -> list[list[str]]: # 재귀적 텍스트 분할
  splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500,
    chunk_overlap  = 100,
    length_function = len,
  )
  docs = []
  for doc in data:
    content = doc.page_content
    text = splitter.split_text(content)
    docs.append(text)
  return docs

def flatten(nested: list[list[str]]):
  return [item for sublist in nested for item in sublist]

def sanitize_collection_name(name: str) -> str:
  name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
  return name.strip("_")

def format_docs(docs):
  return '\n\n'.join([d.page_content for d in docs])

def create_multi_query_retriever(retriever, llm):
  return MultiQueryRetriever.from_llm(
    retriever=retriever,
    llm=llm
  )
  
def create_prompt_template():
  # Prompt
  template = '''Answer the question based only on the following context:
  {context}

  Question: {question}
  '''
  prompt = ChatPromptTemplate.from_template(template)
  return prompt

@chat.post("/new-chat")
async def start_chat(
  file: UploadFile,
  query: str = Form(..., description="사용자 질문", example="사용자 질문"),
  user_id: str = Depends(get_current_user), 
  ai_service: AIService = Depends(get_ai_service),
):
  try: 
    if not user_id: 
      raise Exception("토큰이 없습니다.")
  
    filename = await upload_pdf(file)
    if not filename: 
      raise Exception("파일을 업로드 할 수 없습니다.")
  
    path = f"files/{filename}"
    file_contents = py_load_file(path)
    raw_name = f"user-{user_id}"
    collection_name = sanitize_collection_name(raw_name)
    print(f"collection name: {collection_name}")

    tokens = split_recursive(file_contents) # 토큰화
    flatten_tokens = flatten(tokens)
    vectorstore = await ai_service.create_vectorstore(flatten_tokens, collection_name) # 임베딩 및 저장소 생성
    retriever = vectorstore.as_retriever(
      search_type="mmr",
      search_kwargs={'k': 1, "lambda_mult": 0.5, "fetch_k": 5}
    ) 
    retriever_from_llm = create_multi_query_retriever(retriever, ai_service.llm)
    prompt = create_prompt_template()
    llm = ai_service.llm
    chain = (
      {'context': retriever_from_llm | format_docs, 'question': RunnablePassthrough()}
      | prompt
      | llm
      | StrOutputParser()
    )

    response = chain.invoke(query)
    print(response)
    
    async with in_transaction() as connection:
      user = await Users.filter(id=user_id).first()
      if not user: 
        raise Exception("사용자가 존재하지 않습니다.")
      
      collection = await Collections.create(user=user, name=collection_name, topic=query, using_db=connection)
      document = await Documents.create(collection=collection, path=path, using_db=connection)
      history = await ChatHistory.create(collection=collection, user_message=query, chat_response=response, using_db=connection)

    return {
      "status_code": 201,
      "data": {
        "collection": collection,
        "history": history, 
      },
    }
  except Exception as error:
    raise HTTPException(
      status_code=400,
      detail={
        "error": str(error)
      }
    )
  
@chat.post("/collection_id")
async def request_to_ai(
  collection_id: str,
  dto: ReqToAiDto,
  user_id: str = Depends(get_current_user),
  collection_service: CollectionsService = Depends(get_collections_service),
  ai_service: AIService = Depends(get_ai_service)
): 
  try: 
    selected_collection = await collection_service.find_one(collection_id)
    if not selected_collection or str(selected_collection.user.id) != user_id : 
      raise Exception("해당 컬렉션을 조회할 수 없습니다.")
    
    collection_name = selected_collection.name
    vectorstore = await ai_service.find_vectorstore(collection_name)
    retriever = vectorstore.as_retriever(
      search_type="mmr",
      search_kwargs={'k': 5, "lambda_mult": 0.5, "fetch_k": 10}
    )
    retriever_from_llm = create_multi_query_retriever(retriever, ai_service.llm)
    prompt = create_prompt_template()
    llm = ai_service.llm
    chain = (
      {'context': retriever_from_llm | format_docs, 'question': RunnablePassthrough()}
      | prompt
      | llm
      | StrOutputParser()
    )

    response = chain.invoke(dto.user_message)
    print(response)
    async with in_transaction() as connection:
      updated_collection = await Collections.filter(id=selected_collection.id).update(updated_at=datetime.datetime.now())
      history = await ChatHistory.create(collection=selected_collection, user_message=dto.user_message, chat_response=response, using_db=connection)
      
    return {
      "status_code": 201,
      "data": {
        "collection": updated_collection,
        "history": history
      }
    }
  except Exception as error:
    raise HTTPException(
      status_code=400,
      detail={
        "error": str(error)
      }
    )

  
@chat.get("/")
async def find_my_chat_lists(
  query: Annotated[QueryDto, Query()],
  user_id: str = Depends(get_current_user),
  service: CollectionsService = Depends(get_collections_service)
):
  try:
    offset = query.limit * (query.page - 1)
    result = await service.find_many(user_id, offset, query.limit, order_by="created_at")
    d, t = itemgetter('data', 'total')(result)
  
    return {
      "status_code": 200,
      "data": {
        "items": d,
        "total": t,
      } 
    }
  except Exception as error: 
    raise HTTPException(
      status_code=400,
      detail={
        "error": str(error)
      }
    )
  
@chat.get('/collection_id')
async def get_collection_message(
  query: Annotated[HistoryQueryDto, Query()],
  user_id: str = Depends(get_current_user),
  chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
  user_service: UsersService = Depends(get_users_service)
): 
  try:
    offset = query.limit * (query.page - 1)
    previous_user = await user_service.find_one_by_id(id=user_id)
    if not previous_user: 
      raise Exception("사용자가 존재하지 않습니다.")
    
    history_data = await chat_history_service.find_many(query.collection_id, offset, query.limit)
    d, t = itemgetter("data", "total")(history_data)

    return {
      "status_code": 200, 
      "data": {
        "items": d,
        "total": t,
      }
    }
  except Exception as error: 
    raise HTTPException(
      status_code=400,
      detail={
        error: str(error)
      }
    )