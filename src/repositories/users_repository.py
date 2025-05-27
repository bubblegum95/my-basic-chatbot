import bcrypt
from src.models.users_model import Users
from src.schemas.create_user_dto import CreateUserDto


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
  
  async def create(self, **dto):
    return await self.repository.create(**dto)

  async def find_email(self, email: str):
    return await self.repository.filter(email=email).exists()
  
  async def find_one_by_email(self, email: str):
    return await self.repository.filter(email=email).get()
  
  async def find_one_by_id(self, id: str):
    return await self.repository.filter(id=id).get()