from fastapi import APIRouter, HTTPException, Response, status
from data.storage import (
    specializations_list,
    doctors_list,
    get_next_specialization_id,
)
from schemas.specialization import (
    SpecializationCreate,
    SpecializationUpdate,
    SpecializationResponse,
)

router = APIRouter(prefix="/specializations", tags=["Specializations"])


def find_specialization_or_404(specialization_id: int) -> dict:
    for spec in specializations_list:
        if spec["id"] == specialization_id:
            return spec
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Specialization with id {specialization_id} not found",
    )


@router.post("", response_model=SpecializationResponse, status_code=status.HTTP_201_CREATED)
def create_specialization(data: SpecializationCreate):
    for spec in specializations_list:
        if spec["name"].strip().lower() == data.name.strip().lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Specialization '{data.name}' already exists",
            )

    new_spec = {
        "id": get_next_specialization_id(),
        "name": data.name.strip(),
        "description": data.description,
    }
    specializations_list.append(new_spec)
    return new_spec


@router.get("", response_model=list[SpecializationResponse])
def get_specializations():
    return specializations_list


@router.get("/{specialization_id}", response_model=SpecializationResponse)
def get_specialization(specialization_id: int):
    return find_specialization_or_404(specialization_id)


@router.patch("/{specialization_id}", response_model=SpecializationResponse)
def update_specialization(specialization_id: int, data: SpecializationUpdate):
    spec = find_specialization_or_404(specialization_id)
    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] is not None:
        new_name = update_data["name"].strip()
        for other in specializations_list:
            if other["id"] != specialization_id and other["name"].strip().lower() == new_name.lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Specialization '{new_name}' already exists",
                )
        update_data["name"] = new_name

    spec.update(update_data)
    return spec


@router.delete("/{specialization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_specialization(specialization_id: int):
    spec = find_specialization_or_404(specialization_id)

    # Check foreign relations: doctor with this specialization
    for doctor in doctors_list:
        if doctor["specialization_id"] == specialization_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete specialization associated with existing doctors",
            )

    specializations_list.remove(spec)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
