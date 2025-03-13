from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ShortURLSchema(BaseModel):
    short_url: HttpUrl = Field(..., max_length=2083)

    model_config = ConfigDict(from_attributes=True)


class OriginalURLSchema(BaseModel):
    original_url: HttpUrl = Field(..., max_length=2083)

    model_config = ConfigDict(from_attributes=True)
