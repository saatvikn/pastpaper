from pydantic import BaseModel, ConfigDict, Field


class CourseCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=200)
