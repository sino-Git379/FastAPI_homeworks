from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from pydantic import BaseModel, ConfigDict, field_validator


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AppointmentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    patient_id: int
    doctor_id: int
    start_at: datetime
    duration_minutes: Literal[15, 30, 45, 60]
    reason: str | None = None

    @field_validator("start_at")
    @classmethod
    def validate_start_at(cls, v: datetime) -> datetime:
        now = datetime.now(timezone.utc)
        v_utc = v if v.tzinfo is not None else v.replace(tzinfo=timezone.utc)
        if v_utc <= now:
            raise ValueError("Appointment start time must be in the future")
        return v


class AppointmentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    doctor_id: int | None = None
    start_at: datetime | None = None
    duration_minutes: Literal[15, 30, 45, 60] | None = None
    reason: str | None = None

    @field_validator("start_at")
    @classmethod
    def validate_start_at(cls, v: datetime | None) -> datetime | None:
        if v is not None:
            now = datetime.now(timezone.utc)
            v_utc = v if v.tzinfo is not None else v.replace(tzinfo=timezone.utc)
            if v_utc <= now:
                raise ValueError("Appointment start time must be in the future")
        return v


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    start_at: datetime
    duration_minutes: int
    status: AppointmentStatus
    reason: str | None = None
