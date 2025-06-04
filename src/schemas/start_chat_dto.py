from pydantic import BaseModel, Field


class StartChatDto(BaseModel):
  query: str = Field(..., description="사용자 질문", examples=["사용자 질문"])