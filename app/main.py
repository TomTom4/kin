from typing import Annotated, AsyncGenerator
from uuid import UUID

from fastapi import Depends, FastAPI, Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import UUID4, BaseModel

from app.domain import Appointment
from app.service import AppointmentController
from app.service import UserService as UserController

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class AppointmentsResponse(BaseModel):
    appointments: list[Appointment]


class LoginData(BaseModel):
    username: str
    password: str


class SignupData(BaseModel):
    email: str
    firstname: str
    lastname: str
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
async def get_all_appointments(
    service: AppointmentService, token: Annotated[str, Depends(oauth2_scheme)]
) -> AppointmentsResponse:
    return AppointmentsResponse(appointments=await service.get_all_appointments())


@app.post("/signup")
async def signup(data: SignupData, service: UserService) -> SignupResponse:
    user_id: UUID = await service.create_user(
        data.firstname, data.lastname, data.email, data.password
    )
    return SignupResponse(user_id=user_id)


@app.post("/login")
async def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    service: UserService,
) -> dict[str, str]:
    access_token: str = await service.authenticate_user(username, password)
    payload: dict[str, str] = dict(access_token=access_token, token_type="bearer")
    return payload
