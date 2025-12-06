from datetime import datetime, timedelta
from hashlib import sha3_512
from secrets import choice
from string import ascii_letters, digits

from pydantic import UUID4, BaseModel, EmailStr, Field, field_validator

from app.exceptions import InvalidDateAndTimeError, OverlappingAppointmentError


class KinModel(BaseModel):
    id: UUID4


class User(KinModel):
    firstname: str
    lastname: str
    email: EmailStr
    password_hash: bytes
    salt: str

    @staticmethod
    async def generate_salt() -> str:
        alphabet = ascii_letters + digits
        return "".join([choice(alphabet) for _ in range(32)])

    @staticmethod
    async def hash_password(salted_password: str) -> bytes:
        hashed_salted_password: bytes = sha3_512(salted_password.encode()).digest()
        return hashed_salted_password


class Appointment(KinModel):
    title: str
    start_at: datetime
    duration: timedelta = Field(default_factory=lambda: timedelta(minutes=30))
    patient_id: UUID4
    therapist_id: UUID4

    @field_validator("start_at")
    @classmethod
    def validate_start_at(cls, value: datetime) -> datetime:
        if value < datetime.now():
            raise InvalidDateAndTimeError
        return value

    def is_not_overlapping_with(self, another_appointment: Appointment) -> None:
        if (
            (
                self.patient_id == another_appointment.patient_id
                or self.therapist_id == another_appointment.therapist_id
            )
            and another_appointment.start_at
            <= self.start_at
            <= another_appointment.start_at + another_appointment.duration
        ):
            raise OverlappingAppointmentError
