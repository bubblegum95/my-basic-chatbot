import datetime
from src.models.collections_model import Collections
from typing import Any, Literal

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
    
  async def find_many(self, user_id: str, offset: int, limit: int, order_by: Literal["created_at", "updated_at"]) -> dict[str, Any]:
    query = self.repository.filter(user_id=user_id)
    data = await query.order_by(f'-{order_by}').offset(offset).limit(limit).values('id', 'name', 'created_at', 'updated_at')
    total = await query.count()
    return {
      "data": data,
      "total": total
    }
  
  async def find_one(self, id: str):
    return await self.repository.get(id=id).prefetch_related("user")
  
  async def modify_updated(self, id: str):
    now = datetime.datetime.now()
    return await self.repository.filter(id=id).update(updated_at=now)
