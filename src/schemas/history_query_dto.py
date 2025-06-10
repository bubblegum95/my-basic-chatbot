from typing import Literal
from pydantic import BaseModel, Field


class HistoryQueryDto(BaseModel):
  collection_id: str = Field(..., description="컬렉션/주제 id")
  page: int = Field(..., ge=1)
  limit: int = Field(..., ge=10, le=50)
  order_by: Literal["created_at", "updated_at"] = "created_at"