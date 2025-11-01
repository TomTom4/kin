from datetime import date, datetime, timedelta
from uuid import UUID, uuid4

from fastapi import FastAPI

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
        new_appointment = Appointment(
            id=uuid4(),
            title=f"{patient.firstname} {patient.lastname}",
            start_at=at,
            patient_id=patient.id,
            therapist_id=therapist.id,
        )
        for an_appointment in self.appointments:
            new_appointment.is_not_overlapping_with(an_appointment)

        self.appointments.append(new_appointment)
        return new_appointment

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
