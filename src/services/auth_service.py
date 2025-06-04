from datetime import datetime, timedelta
from fastapi import HTTPException
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
      if not config: 
        raise KeyError("토큰 서명이 없습니다.")

      self.jwt_secret = config("JWT_SECRET")
      self.jwt_algorithm = "HS256"
      self.access_token_expiry = timedelta(minutes=15)
      self.refresh_token_expiry = timedelta(days=7)
      self.initialized = True

  async def create_token(self, user_id: str, refresh: bool = False) -> str:
    expiry = datetime.now() + (self.refresh_token_expiry if refresh else self.access_token_expiry)
    payload = {
      "id" : user_id,
      "exp" : expiry,
    }
    token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    return token
  
  async def verify_token(self, token: str) -> str:
    try:
      payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
      user_id = payload["id"]
      return user_id
    except jwt.ExpiredSignatureError:
      raise HTTPException(
        detail={
          "error": "토큰이 만료되었습니다."},
        status_code=400,
      )
    except jwt.InvalidTokenError:
      raise HTTPException(
        detail={
          "error": "잘못된 토큰입니다."
        },
        status_code=400
      )
