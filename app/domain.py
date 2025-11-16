from datetime import datetime, timedelta

from pydantic import UUID4, BaseModel, EmailStr, Field, field_validator

from app.exceptions import InvalidDateAndTimeError, OverlappingAppointmentError


class KinModel(BaseModel):
    id: UUID4


class User(KinModel):
    firstname: str
    lastname: str
    email: EmailStr
    password_hash: str


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

    def is_not_overlapping_with(self, another_appointment) -> None:
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
