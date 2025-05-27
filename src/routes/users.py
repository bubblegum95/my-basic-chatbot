from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from src.repositories.users_repository import UsersRepository
from src.schemas.create_user_dto import CreateUserDto
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
    user_accout = await service.create_one(name=dto.name, email=dto.email, password_hash=password_hash)
    
    return JSONResponse(
      content={
        "message": "계정 생성을 완료하였습니다.", 
        "email": user_accout
      },
      status_code=201
    )
  except Exception as error:
    return JSONResponse(
      content={
        "message": "계정을 생성할 수 없습니다.",
        "error": error
      },
      status_code=400,
    )