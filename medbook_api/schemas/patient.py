from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class PatientBase(BaseModel):
    full_name: str = Field(min_length=3, max_length=100)
    phone: str = Field(min_length=1)
    email: EmailStr | None = None
    birth_date: date | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Phone cannot be empty")
        return trimmed

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("Birth date cannot be in the future")
        return v


class PatientCreate(PatientBase):
    model_config = ConfigDict(extra="forbid")


class PatientReplace(PatientBase):
    model_config = ConfigDict(extra="forbid")


class PatientUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: str | None = Field(default=None, min_length=3, max_length=100)
    phone: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = None
    birth_date: date | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Phone cannot be empty")
            return trimmed
        return v

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("Birth date cannot be in the future")
        return v


class PatientResponse(PatientBase):
    id: int
