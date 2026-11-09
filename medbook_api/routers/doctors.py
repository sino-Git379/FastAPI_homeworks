from fastapi import APIRouter, HTTPException, Response, status
from data.storage import (
    doctors_list,
    specializations_list,
    appointments_list,
    get_next_doctor_id,
)
from schemas.doctor import (
    DoctorCreate,
    DoctorReplace,
    DoctorUpdate,
    DoctorResponse,
)
from schemas.appointment import AppointmentResponse

router = APIRouter(prefix="/doctors", tags=["Doctors"])


def find_doctor_or_404(doctor_id: int) -> dict:
    for doctor in doctors_list:
        if doctor["id"] == doctor_id:
            return doctor
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Doctor with id {doctor_id} not found",
    )


def check_specialization_exists(specialization_id: int) -> None:
    for spec in specializations_list:
        if spec["id"] == specialization_id:
            return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Specialization with id {specialization_id} not found",
    )


@router.post("", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_doctor(data: DoctorCreate):
    check_specialization_exists(data.specialization_id)

    new_doctor = {
        "id": get_next_doctor_id(),
        "full_name": data.full_name,
        "specialization_id": data.specialization_id,
        "experience_years": data.experience_years,
        "consultation_price": data.consultation_price,
        "is_active": data.is_active,
    }
    doctors_list.append(new_doctor)
    return new_doctor


@router.get("", response_model=list[DoctorResponse])
def get_doctors(
    specialization_id: int | None = None,
    is_active: bool | None = None,
    min_experience: int | None = None,
    max_price: float | None = None,
    search: str | None = None,
):
    filtered_doctors = []
    for doc in doctors_list:
        if specialization_id is not None and doc["specialization_id"] != specialization_id:
            continue
        if is_active is not None and doc["is_active"] != is_active:
            continue
        if min_experience is not None and doc["experience_years"] < min_experience:
            continue
        if max_price is not None and doc["consultation_price"] > max_price:
            continue
        if search is not None and search.lower() not in doc["full_name"].lower():
            continue
        filtered_doctors.append(doc)
    return filtered_doctors


@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: int):
    return find_doctor_or_404(doctor_id)


@router.put("/{doctor_id}", response_model=DoctorResponse)
def replace_doctor(doctor_id: int, data: DoctorReplace):
    doc = find_doctor_or_404(doctor_id)
    check_specialization_exists(data.specialization_id)

    doc["full_name"] = data.full_name
    doc["specialization_id"] = data.specialization_id
    doc["experience_years"] = data.experience_years
    doc["consultation_price"] = data.consultation_price
    doc["is_active"] = data.is_active
    return doc


@router.patch("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(doctor_id: int, data: DoctorUpdate):
    doc = find_doctor_or_404(doctor_id)
    update_data = data.model_dump(exclude_unset=True)

    if "specialization_id" in update_data and update_data["specialization_id"] is not None:
        check_specialization_exists(update_data["specialization_id"])

    doc.update(update_data)
    return doc


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(doctor_id: int):
    doc = find_doctor_or_404(doctor_id)

    # Check foreign relations: appointment with this doctor
    for app in appointments_list:
        if app["doctor_id"] == doctor_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete doctor with existing appointments",
            )

    doctors_list.remove(doc)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{doctor_id}/appointments", response_model=list[AppointmentResponse])
def get_doctor_appointments(doctor_id: int):
    find_doctor_or_404(doctor_id)
    return [app for app in appointments_list if app["doctor_id"] == doctor_id]
