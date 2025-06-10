from src.models.chat_history_model import ChatHistory

class ChatHistoryRepository:
  _instance = None

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self, repository: ChatHistory | None = None):
    if not hasattr(self, "intialized"):
      self.repository = repository or ChatHistory()
      self.intialized = True

  async def create(self, **dto):
    return await self.repository.create(**dto)
  
  async def find_many(self, collection_id: str, offset: int, limit: int):
    query = self.repository.filter(collection_id=collection_id)
    data = await query.order_by('-created_at').offset(offset).limit(limit).values("id", "user_message", "chat_response", "created_at")
    total = await query.count()
    return {
      "data": data,
      "total": total
    }