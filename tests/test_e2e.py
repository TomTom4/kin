import datetime
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.domain import Appointment
from app.main import AppointmentController, app, get_appointment_service


@pytest.fixture
def controlled_service():
    return AppointmentController()


@pytest.fixture
def basic_client():
    client = TestClient(app)
    return client


@pytest.fixture
def override_app(controlled_service: AppointmentController):
    app.dependency_overrides[get_appointment_service] = lambda: controlled_service
    try:
        yield app
    finally:
        app.dependency_overrides = {}


@pytest.fixture
def with_controlled_service_client(override_app: FastAPI):
    client = TestClient(override_app)
    return client


@pytest.fixture
def client():
    client = TestClient(app)
    return client


class TestAppointments:

    def test_get_all_appointments_with_no_appointments(self, client: TestClient):
        response = client.get("/appointments")
        assert response.status_code == 200
        assert response.json() == {"appointments": []}

    def test_get_all_appointments_with_one_appointment(
        self,
        with_controlled_service_client: TestClient,
        controlled_service: AppointmentController,
    ):
        appointment: Appointment = Appointment(
            id=uuid.uuid4(),
            title="test",
            start_at=datetime.datetime.now() + datetime.timedelta(days=1),
            patient_id=uuid.uuid4(),
            therapist_id=uuid.uuid4(),
        )
        controlled_service.appointments.append(appointment)
        response = with_controlled_service_client.get("/appointments")
        assert response.status_code == 200
        appointments = response.json()["appointments"]
        assert len(appointments) == 1

    def test_get_all_appointments_with_many_appointment(
        self,
        with_controlled_service_client: TestClient,
        controlled_service: AppointmentController,
    ):
        appointment: Appointment = Appointment(
            id=uuid.uuid4(),
            title="test",
            start_at=datetime.datetime.now() + datetime.timedelta(days=1),
            patient_id=uuid.uuid4(),
            therapist_id=uuid.uuid4(),
        )
        controlled_service.appointments.append(appointment)
        controlled_service.appointments.append(appointment)
        response = with_controlled_service_client.get("/appointments")
        assert response.status_code == 200
        appointments = response.json()["appointments"]
        assert len(appointments) > 1
