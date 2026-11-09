# In-memory storage for MedBook API

specializations_list = []
doctors_list = []
patients_list = []
appointments_list = []

# ID counters (not reused after deletion)
specialization_next_id = 0
doctor_next_id = 0
patient_next_id = 0
appointment_next_id = 0


def get_next_specialization_id() -> int:
    global specialization_next_id
    specialization_next_id += 1
    return specialization_next_id


def get_next_doctor_id() -> int:
    global doctor_next_id
    doctor_next_id += 1
    return doctor_next_id


def get_next_patient_id() -> int:
    global patient_next_id
    patient_next_id += 1
    return patient_next_id


def get_next_appointment_id() -> int:
    global appointment_next_id
    appointment_next_id += 1
    return appointment_next_id
