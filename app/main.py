from typing import Annotated, AsyncGenerator
from uuid import UUID

from fastapi import Depends, FastAPI
from pydantic import UUID4, BaseModel

from app.domain import Appointment
from app.service import AppointmentController
from app.service import UserService as UserController

app = FastAPI()


class AppointmentsResponse(BaseModel):
    appointments: list[Appointment]


class SignupData(BaseModel):
    firstname: str
    lastname: str
    email: str
    password: str


class SignupResponse(BaseModel):
    user_id: UUID4


appointment_service = AppointmentController()
user_service = UserController()


async def get_appointment_service() -> AsyncGenerator[AppointmentController, None]:
    yield appointment_service


async def get_user_service() -> AsyncGenerator[UserController]:
    yield user_service


AppointmentService = Annotated[AppointmentController, Depends(get_appointment_service)]
UserService = Annotated[UserController, Depends(get_user_service)]


@app.get("/appointments")
async def get_all_appointments(service: AppointmentService) -> AppointmentsResponse:
    return AppointmentsResponse(appointments=await service.get_all_appointments())


@app.post("/signup")
async def signup(data: SignupData, service: UserService) -> SignupResponse:
    user_id: UUID = await service.create_user(
        data.firstname, data.lastname, data.email, data.password
    )
    return SignupResponse(user_id=user_id)
