from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel

from app.domain import Appointment
from app.service import AppointmentController

app = FastAPI()


class AppointmentsResponse(BaseModel):
    appointments: list[Appointment]


appointment_service = AppointmentController()


async def get_appointment_service():
    yield appointment_service


AppointmentService = Annotated[AppointmentController, Depends(get_appointment_service)]


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/appointments")
async def get_all_appointments(service: AppointmentService) -> AppointmentsResponse:
    return AppointmentsResponse(appointments=await service.get_all_appointments())
