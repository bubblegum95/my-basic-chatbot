from src.repositories.collections_repository import CollectionsRepository
from src.models.collections_model import Collections


class CollectionsService: 
  _instance = None

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self, repository: CollectionsRepository | None = None):
    if not hasattr(self, "intialized"):
      self.repository = repository or CollectionsRepository()
      self.initialized = True
  
  async def create(self, **dto) -> Collections | None:
    return await self.repository.create(**dto)
