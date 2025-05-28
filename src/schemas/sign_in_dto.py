from pydantic import BaseModel, Field


class SignInDto(BaseModel):
  email: str = Field(..., description="이메일")
  password: str = Field(..., description="비밀번호")

  class Config:
    json_schema_extra = {
      "example": {
        "email": "user@email.com",
        "password": "Example123!",
      }
    }