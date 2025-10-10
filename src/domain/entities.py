from datetime import datetime

from pydantic import UUID4, BaseModel


class Events(BaseModel):
    id: UUID4
    caregiver_id: UUID4
    patient_id: UUID4
    start_at: datetime
    end_at: datetime
    treatment: str


class User(BaseModel):
    id: UUID4
    firstname: str
    lastname: str
    email: str
    cellphone: str
