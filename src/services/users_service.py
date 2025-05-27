import bcrypt
from src.repositories.users_repository import UsersRepository
from src.services.auth_service import AuthService


class UsersService: 
  _instance = None

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self, repository: UsersRepository, auth_service: AuthService):
    if not hasattr(self, "initialized"):
      self.initialized = True
      self.repository = repository or UsersRepository()
      self.auth_service = auth_service or AuthService()

  def hash_password(self, pw: str):
    return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
  
  async def find_email(self, email: str):
    return await self.repository.find_email(email=email)
  
  async def create_one(self, **dto):
    return await self.repository.create(dto=dto)
  
  async def find_one_by_email(self, email: str):
    return await self.repository.find_one_by_email(email=email)
  
  async def find_one_by_id(self, id: str):
    return await self.repository.find_one_by_id(id=id)