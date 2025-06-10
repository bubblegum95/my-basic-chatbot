from typing import Literal
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
  
  async def find_many(self, user_id: str, offset: int, limit: int, order_by: Literal["created_at", "updated_at"]):
    return await self.repository.find_many(user_id, offset, limit, order_by)
  
  async def find_one(self, id: str):
    return await self.repository.find_one(id)

  async def modify_updated(self, id: str):
    return await self.repository.modify_updated(id)

def get_collections_service(): 
  repository = CollectionsRepository()
  service = CollectionsService(repository)
  return service