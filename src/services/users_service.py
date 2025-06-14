import bcrypt
from src.repositories.users_repository import UsersRepository
from src.services.auth_service import AuthService, get_auth_service


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

  async def create_token(self, user_id: str, refresh: bool = False):
    return await self.auth_service.create_token(user_id=user_id, refresh=refresh)
  
  async def verify_token(self, token: str):
    return await self.auth_service.verify_token(token=token)
  
  def hash_password(self, pw: str) -> bytes:
    return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
  
  def compare_password(self, pw: bytes, hpw: bytes): 
    return bcrypt.checkpw(pw, hpw)
  
  async def find_email(self, email: str):
    return await self.repository.find_email(email=email)
  
  async def create_one(self, **dto):
    return await self.repository.create(**dto)
  
  async def find_one_by_email(self, email: str):
    return await self.repository.find_one_by_email(email=email)
  
  async def find_one_by_id(self, id: str):
    return await self.repository.find_one_by_id(id=id)
  
  async def modify_token(self, id: str, refresh_token: str):
    return await self.repository.modify_token(id=id, refresh_token=refresh_token)
  
def get_users_service() -> UsersService:
  repository = UsersRepository()
  auth_service = get_auth_service()
  users_service = UsersService(repository=repository, auth_service=auth_service)
  return users_service