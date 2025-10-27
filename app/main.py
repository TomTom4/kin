from datetime import date, datetime, timedelta
from uuid import UUID, uuid4

from fastapi import FastAPI

from app.exceptions import InvalidDateAndTimeError, OverlappingAppointmentError
from app.models import Appointment, User

app = FastAPI()


class AppointmentController:

    def __init__(self) -> None:
        self.appointments: list[Appointment] = []

    def create_appointment(
        self,
        at: datetime,
        patient: User,
        therapist: User,
        duration: timedelta = timedelta(minutes=30),
    ) -> Appointment:
        if at < datetime.now():
            raise InvalidDateAndTimeError
        for an_appointment in self.appointments:
            if (
                (
                    an_appointment.patient_id == patient.id
                    or an_appointment.therapist_id == therapist.id
                )
                and an_appointment.start_at
                <= at
                <= an_appointment.start_at + an_appointment.duration
            ):
                raise OverlappingAppointmentError
        appointment = Appointment(
            id=uuid4(),
            title=f"{patient.firstname} {patient.lastname}",
            start_at=at,
            duration=duration,
            patient_id=patient.id,
            therapist_id=therapist.id,
        )
        self.appointments.append(appointment)
        return appointment

    def get_all_appointments(
        self,
        patient_id: UUID | None = None,
        therapist_id: UUID | None = None,
        day: date | None = None,
    ):
        appointments = self.appointments
        if therapist_id:
            appointments = list(
                filter(lambda x: x.therapist_id == therapist_id, appointments)
            )

        if patient_id:
            appointments = list(
                filter(lambda x: x.patient_id == patient_id, appointments)
            )
        if day:
            appointments = list(
                filter(lambda x: x.start_at.date() == day, appointments)
            )

        return appointments


@app.get("/")
def read_root():
    return {"Hello": "World"}
