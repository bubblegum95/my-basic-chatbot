from src.models.users_model import Users


class UsersRepository:
  _instance = None

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self, repository = Users):
    if not hasattr(self, "initialized"):
      self.initialized = True
      self.repository = repository
  
  async def create(self, **dto) -> Users:
    try:
      return await self.repository.create(**dto)
    except Exception as error:
      raise error

  async def find_email(self, email: str):
    return await self.repository.filter(email=email).exists()
  
  async def find_one_by_email(self, email: str) -> Users | None:
    try: 
      return await self.repository.filter(email=email).get()
    except: 
      return None
  
  async def find_one_by_id(self, id: str) -> Users | None:
    try:
      return await self.repository.filter(id=id).get()
    except: 
      return None
  
  async def modify_token(self, id: str, refresh_token: str):
    return await self.repository.filter(id=id).update(refresh_token=refresh_token)