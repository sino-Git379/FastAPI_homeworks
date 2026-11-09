from fastapi import FastAPI
from routers import specializations, doctors, patients, appointments

app = FastAPI(
    title="MedBook API",
    description="REST API для онлайн-записи к врачам (хранение данных в памяти)",
    version="1.0.0",
)

app.include_router(specializations.router, prefix="/api/v1")
app.include_router(doctors.router, prefix="/api/v1")
app.include_router(patients.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "Welcome to MedBook API",
        "docs": "/docs",
        "version": "1.0.0",
    }
