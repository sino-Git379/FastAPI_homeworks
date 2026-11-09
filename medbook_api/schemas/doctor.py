from pydantic import BaseModel, ConfigDict, Field


class DoctorBase(BaseModel):
    full_name: str = Field(min_length=3, max_length=100)
    specialization_id: int
    experience_years: int = Field(ge=0)
    consultation_price: float = Field(gt=0)
    is_active: bool = True


class DoctorCreate(DoctorBase):
    model_config = ConfigDict(extra="forbid")


class DoctorReplace(DoctorBase):
    model_config = ConfigDict(extra="forbid")


class DoctorUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: str | None = Field(default=None, min_length=3, max_length=100)
    specialization_id: int | None = None
    experience_years: int | None = Field(default=None, ge=0)
    consultation_price: float | None = Field(default=None, gt=0)
    is_active: bool | None = None


class DoctorResponse(DoctorBase):
    id: int
