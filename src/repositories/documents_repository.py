from src.models.documents_model import Documents

class DocumentsRepository:
  _instance = None

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance 
  
  def __init__(self, repository: Documents | None = None):
    if not hasattr(self, "initialized"):
      self.repository = repository or Documents()
      self.initialized = True

  async def create(self, **dto) -> Documents:
    return await self.repository.create(**dto)

  async def find_one(self, id: str) -> Documents:
    try:
      document = await self.repository.filter(id=id).first()
      if not document: 
        raise Exception("document를 찾을 수 없습니다.")
      return document
    except Exception as error:
      raise error
  