import datetime
import uuid
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.domain import Appointment
from app.main import app, get_appointment_service, get_user_service, oauth2_scheme
from app.service import AppointmentController
from app.service import UserService as UserController


@pytest.fixture
def controlled_appointment_service() -> AppointmentController:
    return AppointmentController()


@pytest.fixture
def controlled_user_service() -> UserController:
    return UserController()


@pytest.fixture
def override_app(
    controlled_appointment_service: AppointmentController,
    controlled_user_service: UserController,
) -> Generator[FastAPI, None, None]:
    app.dependency_overrides[get_appointment_service] = (
        lambda: controlled_appointment_service
    )
    app.dependency_overrides[get_user_service] = lambda: controlled_user_service
    try:
        yield app
    finally:
        app.dependency_overrides = {}


@pytest.fixture
def client(override_app: FastAPI) -> TestClient:
    client = TestClient(override_app)
    return client


@pytest.fixture
def authenticated_client(override_app: FastAPI) -> TestClient:
    override_app.dependency_overrides[oauth2_scheme] = lambda _: "token.token.token"
    return TestClient(override_app)


class TestAppointments:

    def test_get_all_appointments_with_no_appointments(
        self, authenticated_client: TestClient
    ) -> None:
        breakpoint()
        response = authenticated_client.get("/appointments")
        assert response.status_code == 200
        assert response.json() == {"appointments": []}

    def test_get_all_appointments_with_one_appointment(
        self,
        authenticated_client: TestClient,
        controlled_appointment_service: AppointmentController,
    ) -> None:
        appointment: Appointment = Appointment(
            id=uuid.uuid4(),
            title="test",
            start_at=datetime.datetime.now() + datetime.timedelta(days=1),
            patient_id=uuid.uuid4(),
            therapist_id=uuid.uuid4(),
        )
        controlled_appointment_service.appointments.append(appointment)
        response = authenticated_client.get("/appointments")
        assert response.status_code == 200
        appointments = response.json()["appointments"]
        assert len(appointments) == 1

    def test_get_all_appointments_with_many_appointment(
        self,
        authenticated_client: TestClient,
        controlled_appointment_service: AppointmentController,
    ) -> None:
        appointment: Appointment = Appointment(
            id=uuid.uuid4(),
            title="test",
            start_at=datetime.datetime.now() + datetime.timedelta(days=1),
            patient_id=uuid.uuid4(),
            therapist_id=uuid.uuid4(),
        )
        controlled_appointment_service.appointments.append(appointment)
        controlled_appointment_service.appointments.append(appointment)
        response = authenticated_client.get("/appointments")
        assert response.status_code == 200
        appointments = response.json()["appointments"]
        assert len(appointments) > 1


class TestUser:

    def test_create_user(
        self,
        client: TestClient,
        controlled_user_service: UserController,
    ) -> None:
        data: dict[str, str] = dict(
            firstname="test", lastname="test", email="test@test.com", password="test"
        )
        response = client.post("/signup", json=data)
        assert response.json()["user_id"]
        assert len(controlled_user_service.users) == 1
        saved_user = controlled_user_service.users[0]
        assert saved_user.firstname == data["firstname"]
        assert saved_user.lastname == data["lastname"]
        assert saved_user.email == data["email"]
        assert saved_user.password_hash != data["password"].encode()

    @pytest.mark.asyncio
    async def test_login(
        self,
        client: TestClient,
        controlled_user_service: UserController,
    ) -> None:

        data: dict[str, str] = dict(
            firstname="test", lastname="test", email="test@test.com", password="test"
        )
        await controlled_user_service.create_user(
            data["firstname"], data["lastname"], data["email"], data["password"]
        )
        response = client.post(
            "/login", data=dict(username="test@test.com", password="test")
        )
        assert response.status_code == 200
        assert isinstance(response.text, str)
        assert len(response.text.split(".")) == 3
