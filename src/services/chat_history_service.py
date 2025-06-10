from src.repositories.chat_history_repository import ChatHistoryRepository

class ChatHistoryService:
  _instance = None

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self, repository: ChatHistoryRepository | None = None):
    if not hasattr(self, "initialized"):
      self.repository = repository or ChatHistoryRepository()
      self.initialized = True

  async def create(self, **dto):
    return await self.repository.create(**dto)
  
  async def find_many(self, collection_id: str, offset: int, limit: int): 
    return await self.repository.find_many(collection_id, offset, limit)
  
def get_chat_history_service():
  return ChatHistoryService()