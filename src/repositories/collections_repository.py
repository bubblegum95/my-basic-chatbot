from src.models.collections_model import Collections

class CollectionsRepository: 
  _instance = None

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self, repository = Collections):
    if not hasattr(self, "initialized"):
      self.repository = repository
      self.initialized = True
  
  async def create(self, **dto): 
    try:
      return await self.repository.create(**dto)
    except Exception as Error:
      return None