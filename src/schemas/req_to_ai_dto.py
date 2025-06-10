from pydantic import BaseModel, Field


class ReqToAiDto(BaseModel):
  user_message: str = Field(..., description="사용자 질문", examples=["파일 내용을 정리해줘."])