from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import FastAPI

from app.models import Appointment, User

app = FastAPI()


class AppointmentController:

    def create_appointment(
        self,
        at: datetime,
        patient: User,
        therapist: User,
        duration: timedelta = timedelta(minutes=30),
    ):
        return Appointment(
            id=uuid4(),
            title=f"{patient.firstname} {patient.lastname}",
            start_at=at,
            duration=duration,
            patient_id=patient.id,
            therapist_id=therapist.id,
        )


@app.get("/")
def read_root():
    return {"Hello": "World"}
