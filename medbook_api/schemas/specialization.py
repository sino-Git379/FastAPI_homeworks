from pydantic import BaseModel, ConfigDict, Field


class SpecializationBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None


class SpecializationCreate(SpecializationBase):
    model_config = ConfigDict(extra="forbid")


class SpecializationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None


class SpecializationResponse(SpecializationBase):
    id: int
