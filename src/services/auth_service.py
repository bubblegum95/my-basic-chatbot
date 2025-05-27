from datetime import datetime, timedelta
import jwt
from starlette.config import Config


class AuthService: 
  _instance = None

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self):
    if not hasattr(self, "initialized"):
      config = Config('.env')
      
      self.jwt_secret = config("JWT_SECRET")
      self.jwt_algorithm = "HS256"
      self.access_token_expiry = timedelta(minutes=15)
      self.refresh_token_expiry = timedelta(days=7)
      self.initialized = True

  async def create_token(self, user_id: str, refresh: bool = False):
    expiry = datetime.now() + (self.refresh_token_expiry if refresh else self.access_token_expiry)
    payload = {
      "id" : user_id,
      "exp" : expiry,
    }
    token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    return token