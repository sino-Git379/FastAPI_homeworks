from datetime import date, datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, status
from data.storage import (
    appointments_list,
    doctors_list,
    patients_list,
    get_next_appointment_id,
)
from schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentStatus,
)

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def check_intervals_overlap(start1: datetime, dur1: int, start2: datetime, dur2: int) -> bool:
    s1 = to_utc(start1)
    e1 = s1 + timedelta(minutes=dur1)
    s2 = to_utc(start2)
    e2 = s2 + timedelta(minutes=dur2)
    return s1 < e2 and s2 < e1


def find_appointment_or_404(appointment_id: int) -> dict:
    for app in appointments_list:
        if app["id"] == appointment_id:
            return app
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Appointment with id {appointment_id} not found",
    )


def get_doctor_or_validate(doctor_id: int) -> dict:
    for doc in doctors_list:
        if doc["id"] == doctor_id:
            if not doc.get("is_active", True):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Doctor with id {doctor_id} is inactive and cannot accept appointments",
                )
            return doc
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Doctor with id {doctor_id} not found",
    )


def check_patient_exists(patient_id: int) -> None:
    for patient in patients_list:
        if patient["id"] == patient_id:
            return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Patient with id {patient_id} not found",
    )


def check_doctor_availability(
    doctor_id: int,
    start_at: datetime,
    duration_minutes: int,
    exclude_appointment_id: int | None = None,
) -> None:
    for existing in appointments_list:
        if exclude_appointment_id is not None and existing["id"] == exclude_appointment_id:
            continue
        if existing["doctor_id"] == doctor_id and existing["status"] == AppointmentStatus.SCHEDULED.value:
            if check_intervals_overlap(
                start_at,
                duration_minutes,
                existing["start_at"],
                existing["duration_minutes"],
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Doctor already has an active appointment during this time",
                )


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(data: AppointmentCreate):
    check_patient_exists(data.patient_id)
    get_doctor_or_validate(data.doctor_id)

    check_doctor_availability(
        doctor_id=data.doctor_id,
        start_at=data.start_at,
        duration_minutes=data.duration_minutes,
    )

    new_appointment = {
        "id": get_next_appointment_id(),
        "patient_id": data.patient_id,
        "doctor_id": data.doctor_id,
        "start_at": data.start_at,
        "duration_minutes": data.duration_minutes,
        "status": AppointmentStatus.SCHEDULED.value,
        "reason": data.reason,
    }
    appointments_list.append(new_appointment)
    return new_appointment


@router.get("", response_model=list[AppointmentResponse])
def get_appointments(
    doctor_id: int | None = None,
    patient_id: int | None = None,
    status: str | None = None,
    date: date | None = None,
):
    filtered = []
    for app in appointments_list:
        if doctor_id is not None and app["doctor_id"] != doctor_id:
            continue
        if patient_id is not None and app["patient_id"] != patient_id:
            continue
        if status is not None and app["status"] != status:
            continue
        if date is not None:
            app_start = app["start_at"]
            if app_start.date() != date and to_utc(app_start).date() != date:
                continue
        filtered.append(app)
    return filtered


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int):
    return find_appointment_or_404(appointment_id)


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(appointment_id: int, data: AppointmentUpdate):
    app = find_appointment_or_404(appointment_id)

    if app["status"] != AppointmentStatus.SCHEDULED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot edit appointment with status '{app['status']}'. Only 'scheduled' appointments can be updated.",
        )

    update_data = data.model_dump(exclude_unset=True)

    target_doctor_id = update_data.get("doctor_id", app["doctor_id"])
    target_start_at = update_data.get("start_at", app["start_at"])
    target_duration = update_data.get("duration_minutes", app["duration_minutes"])

    if "doctor_id" in update_data:
        get_doctor_or_validate(target_doctor_id)

    if any(k in update_data for k in ("doctor_id", "start_at", "duration_minutes")):
        check_doctor_availability(
            doctor_id=target_doctor_id,
            start_at=target_start_at,
            duration_minutes=target_duration,
            exclude_appointment_id=appointment_id,
        )

    app.update(update_data)
    return app


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(appointment_id: int):
    app = find_appointment_or_404(appointment_id)

    if app["status"] == AppointmentStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Appointment is already cancelled",
        )
    if app["status"] == AppointmentStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot cancel completed appointment",
        )

    app["status"] = AppointmentStatus.CANCELLED.value
    return app


@router.patch("/{appointment_id}/complete", response_model=AppointmentResponse)
def complete_appointment(appointment_id: int):
    app = find_appointment_or_404(appointment_id)

    if app["status"] == AppointmentStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Appointment is already completed",
        )
    if app["status"] == AppointmentStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot complete cancelled appointment",
        )

    now = datetime.now(timezone.utc)
    app_end = to_utc(app["start_at"]) + timedelta(minutes=app["duration_minutes"])
    if now < app_end:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot complete appointment before it has ended",
        )

    app["status"] = AppointmentStatus.COMPLETED.value
    return app
