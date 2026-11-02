from typing import Literal
from pydantic import BaseModel, Field


class PaperCreate(BaseModel):
    course_id: int = Field(gt=0)
    year: int = Field(ge=1900, le=2100)
    exam_type: Literal["midsem", "comprehensive"]
