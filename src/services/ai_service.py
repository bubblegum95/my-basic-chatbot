import getpass
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

class AIService:
  _instance = None

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self):
    if not hasattr(self, "initialized"):
      load_dotenv()
      if not os.environ.get("OPENAI_API_KEY"): 
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")  

      self.embedding_model = OpenAIEmbeddings()
      self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
      self.initalized = True
  
  async def create_vectorstore(self, texts: list[str], collection_name: str) -> Chroma:
    db = Chroma.from_texts(
      texts=texts, 
      embedding=self.embedding_model,
      collection_name=collection_name,
      persist_directory = './db/chromadb', # 벡터 문서 저장 위치
      collection_metadata = {'hnsw:space': 'cosine'}, # l2 is the default
    )
    
    return db
  