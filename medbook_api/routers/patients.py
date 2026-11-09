from fastapi import APIRouter, HTTPException, Response, status
from data.storage import (
    patients_list,
    appointments_list,
    get_next_patient_id,
)
from schemas.patient import (
    PatientCreate,
    PatientReplace,
    PatientUpdate,
    PatientResponse,
)
from schemas.appointment import AppointmentResponse

router = APIRouter(prefix="/patients", tags=["Patients"])


def find_patient_or_404(patient_id: int) -> dict:
    for patient in patients_list:
        if patient["id"] == patient_id:
            return patient
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Patient with id {patient_id} not found",
    )


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(data: PatientCreate):
    new_patient = {
        "id": get_next_patient_id(),
        "full_name": data.full_name,
        "phone": data.phone,
        "email": data.email,
        "birth_date": data.birth_date,
    }
    patients_list.append(new_patient)
    return new_patient


@router.get("", response_model=list[PatientResponse])
def get_patients(search: str | None = None):
    if search is not None:
        search_lower = search.lower()
        return [p for p in patients_list if search_lower in p["full_name"].lower()]
    return patients_list


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int):
    return find_patient_or_404(patient_id)


@router.put("/{patient_id}", response_model=PatientResponse)
def replace_patient(patient_id: int, data: PatientReplace):
    patient = find_patient_or_404(patient_id)

    patient["full_name"] = data.full_name
    patient["phone"] = data.phone
    patient["email"] = data.email
    patient["birth_date"] = data.birth_date
    return patient


@router.patch("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, data: PatientUpdate):
    patient = find_patient_or_404(patient_id)
    update_data = data.model_dump(exclude_unset=True)
    patient.update(update_data)
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int):
    patient = find_patient_or_404(patient_id)

    # Check foreign relations: appointment with this patient
    for app in appointments_list:
        if app["patient_id"] == patient_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete patient with existing appointments",
            )

    patients_list.remove(patient)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{patient_id}/appointments", response_model=list[AppointmentResponse])
def get_patient_appointments(patient_id: int):
    find_patient_or_404(patient_id)
    return [app for app in appointments_list if app["patient_id"] == patient_id]
