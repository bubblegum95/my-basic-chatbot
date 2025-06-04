import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from src.middlewares.jwt_middleware import get_current_user
from src.repositories.collections_repository import CollectionsRepository
from src.schemas.start_chat_dto import StartChatDto
from src.services.collections_service import CollectionsService
from langchain_community.document_loaders import PyPDFLoader
from typing import Iterable
from langchain_core.documents import Document
from dotenv import load_dotenv
from src.services.ai_service import AIService
from langchain.chains import RetrievalQA
from src.services.documents_service import DocumentsService
from src.repositories.documents_repository import DocumentsRepository
from src.models.collections_model import Collections
from tortoise.transactions import in_transaction
from src.models.users_model import Users
from src.models.documents_model import Documents
from src.models.chat_history_model import ChatHistory


load_dotenv()

chat = APIRouter(
  prefix= "/chat", 
  tags=["collections"], 
  responses={404: {"description": "Not Found"}}
)

def get_service(): 
  repository = CollectionsRepository()
  service = CollectionsService(repository)
  return service

def get_ai_service():
  return AIService()

def get_document_service():
  repository = DocumentsRepository()
  return DocumentsService(repository)

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
  
@chat.post("/new-chat")
async def start_chat(
  file: UploadFile,
  dto: StartChatDto,
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
    collection_name = f"user_${user_id}_topic_{filename}"
    

    tokens = split_recursive(file_contents)
    vectorstore = await ai_service.create_vector_db(tokens[0], collection_name) # collections_name
    retriever = vectorstore.as_retriever(
      search_type="mmr",
      search_kwargs={'k': 1, "lambda_mult": 0.5, "fetch_k": 5}
    )
    qa = RetrievalQA.from_chain_type(
      llm=ai_service.client,
      retriever=retriever
    )

    answer = qa.run(dto.query) # 사용자 질문
    async with in_transaction() as connection:
      user = await Users.filter(id=user_id).first()
      if not user: 
        raise Exception("사용자가 존재하지 않습니다.")
      
      collection = await Collections.create(user=user, collection_name=collection_name, using_db=connection)
      document = await Documents.create(collection=collection, path=path, using_db=connection)
      history = await ChatHistory.create(collection=collection, user_message=dto.query, chat_response=answer)
      return collection
    
    print(answer)

    return answer
  except Exception as error:
    raise HTTPException(
      status_code=400,
      detail={
        "error": error
      }
    )