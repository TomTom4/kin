from datetime import datetime, timedelta

from pydantic import UUID4, BaseModel


class KinModel(BaseModel):
    id: UUID4


class User(KinModel):
    firstname: str
    lastname: str


class Appointment(KinModel):
    title: str
    start_at: datetime
    duration: timedelta
    patient_id: UUID4
    therapist_id: UUID4
