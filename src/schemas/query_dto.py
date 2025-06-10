from typing import Literal
from pydantic import BaseModel, Field


class QueryDto(BaseModel):
  page: int = Field(..., ge=1, examples=[1])
  limit: int = Field(..., ge=10, le=50, examples=[10])
  order_by: Literal["created_at", "updated_at"] = "updated_at"