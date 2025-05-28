from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_401_UNAUTHORIZED
from src.services.auth_service import AuthService


auth_service = AuthService()
bearer_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
  token = credentials.credentials
  user_id = await auth_service.verify_token(token)

  if user_id is None:
    raise HTTPException(
      status_code=HTTP_401_UNAUTHORIZED,
      detail="Invalid or expired token",
      headers={"WWW-Authenticate": "Bearer"},
    )
  return user_id