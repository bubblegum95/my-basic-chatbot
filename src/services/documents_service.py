from src.repositories.documents_repository import DocumentsRepository

class DocumentsService:
  _instance = None

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self, repository: DocumentsRepository):
    if not hasattr(self, "initialized"):
      self.repository = repository
      self.initialized = True
  
  async def create(self, **dto):
    return await self.repository.create(**dto)
  
  async def find_one(self, id: str):
    return await self.repository.find_one(id)
  

def get_document_service():
  repository = DocumentsRepository()
  return DocumentsService(repository)