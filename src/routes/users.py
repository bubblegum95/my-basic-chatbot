from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from src.middlewares.jwt_middleware import get_current_user
from src.repositories.users_repository import UsersRepository
from src.schemas.create_user_dto import CreateUserDto
from src.schemas.sign_in_dto import SignInDto
from src.services.auth_service import AuthService
from src.services.users_service import UsersService


users = APIRouter(
  prefix= "/users", 
  tags=["users"], 
  responses={404: {"description": "Not Found"}}
)

def get_auth_service() -> AuthService: 
  auth_service = AuthService()
  return auth_service

def get_users_service() -> UsersService:
  repository = UsersRepository()
  auth_service = get_auth_service()
  users_service = UsersService(repository=repository, auth_service=auth_service)
  return users_service

@users.post("/sign-up")
async def sign_up(dto: CreateUserDto, service: UsersService = Depends(get_users_service)):
  try:
    email_exist = await service.find_email(dto.email)

    if email_exist: 
      raise Exception("해당 이메일은 이미 사용중입니다.")
    
    password_hash = service.hash_password(dto.password)
    decoded_hash = password_hash.decode()
    user_accout = await service.create_one(name=dto.name, email=dto.email, password_hash=decoded_hash)
    
    return {
      "status_code": 201, 
      "email": user_accout.email
    }
  except Exception as error:
    raise HTTPException(
      detail={
        "error": str(error)},
      status_code=400,
    )
  
@users.post("/sign-in")
async def sign_in(dto: SignInDto, service: UsersService = Depends(get_users_service)):
  try: 
    exist_user = await service.find_one_by_email(email=dto.email)
    if not exist_user: 
      raise Exception("해당 계정이 존재하지 않습니다.")
    
    pw = dto.password.encode()
    hpw = exist_user.password_hash.encode()
    print(pw, hpw)
    compared = service.compare_password(pw=pw, hpw=hpw)
    if not compared:
      raise Exception("비밀번호가 일치하지 않습니다.")
    
    user_id = str(exist_user.id)
    access_token = await service.create_token(user_id=user_id)
    refresh_token = await service.create_token(user_id=user_id, refresh=True)
    if not access_token or not refresh_token: 
      raise Exception("토큰을 생성할 수 없습니다.")
    
    updated = await service.modify_token(id=user_id, refresh_token=refresh_token)

    return JSONResponse(
      content={
        "message": "로그인 완료",
        "data": {
          "token": access_token,
          "result": updated
        }
      },
      status_code=200
    )
  except Exception as error:
    raise HTTPException(
      detail={
        "error": str(error)},
      status_code=400,
    )
  
@users.get('/')
async def get_my_info(user_id: str = Depends(get_current_user)):
  return {
    "user_id": user_id,
  }

    