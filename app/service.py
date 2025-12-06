from datetime import date, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from joserfc import jwk, jwt

from app.domain import Appointment, User
from app.exceptions import UserDontExistsError, WrongPasswordError


class AppointmentController:

    def __init__(self) -> None:
        self.appointments: list[Appointment] = []

    async def create_appointment(
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

    async def get_all_appointments(
        self,
        patient_id: UUID | None = None,
        therapist_id: UUID | None = None,
        day: date | None = None,
    ) -> list[Appointment]:
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


class UserService:

    def __init__(self) -> None:
        self.secret_key: jwk.OctKey = jwk.import_key(
            "shhhhush_say_nothing_this_is_my_secret_key", "oct"
        )
        self.encoding_algorithm = "HS256"
        self.users: list[User] = []

    async def encode_jwt_token(self, data: dict[str, Any]) -> str:
        return jwt.encode(dict(alg=self.encoding_algorithm), data, self.secret_key)

    async def create_user(
        self, firstname: str, lastname: str, email: str, password: str
    ) -> UUID:
        salt = await User.generate_salt()
        salted_password = salt + password
        password_hash = await User.hash_password(salted_password)

        new_user = User(
            id=uuid4(),
            firstname=firstname,
            lastname=lastname,
            email=email,
            password_hash=password_hash,
            salt=salt,
        )
        self.users.append(new_user)
        return new_user.id

    async def authenticate_user(self, email: str, password: str) -> str:
        authenticated_user: User | None = None
        for a_user in self.users:
            if a_user.email == email:
                authenticated_user = a_user
                break
        if not authenticated_user:
            raise UserDontExistsError
        salted_password = authenticated_user.salt + password
        hashed_given_password = await User.hash_password(salted_password)
        if hashed_given_password == authenticated_user.password_hash:
            return await self.encode_jwt_token(
                authenticated_user.model_dump(mode="json", exclude={"password_hash"})
            )
        raise WrongPasswordError
