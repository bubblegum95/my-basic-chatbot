from pydantic import BaseModel, Field


class CreateUserDto(BaseModel):
  name: str = Field(..., description="이름")
  email: str = Field(..., description="이메일")
  password: str = Field(..., description="비밀번호")


  class Config:
    json_schema_extra = {
      "example" : {
        "name": "홍길동",
        "email": "user@email.com",
        "price": "Example123!"
      }
    }
