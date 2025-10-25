from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from app.main import (
    AppointmentController,
    InvalidDateAndTimeError,
    OverlappingAppointmentError,
)
from app.models import User


class TestAppointments:

    def test_create_an_appointment(self):
        controller = AppointmentController()
        patient = User(id=uuid4(), firstname="Jane", lastname="Doe")
        therapist = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        at = datetime.now() + timedelta(minutes=1)
        appointments = controller.create_appointment(at, patient, therapist)
        assert appointments.id
        assert appointments.start_at == at
        assert appointments.patient_id == patient.id
        assert appointments.therapist_id == therapist.id

    def test_create_appointment_in_the_past(self):
        controller = AppointmentController()
        patient = User(id=uuid4(), firstname="Jane", lastname="Doe")
        therapist = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        at = datetime.now() - timedelta(days=1)
        with pytest.raises(InvalidDateAndTimeError):
            controller.create_appointment(at, patient, therapist)

    def test_appointments_cannot_overlap(self):
        controller = AppointmentController()
        patient = User(id=uuid4(), firstname="Jane", lastname="Doe")
        therapist = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        at = datetime.now() + timedelta(minutes=1)
        controller.create_appointment(at, patient, therapist)
        with pytest.raises(OverlappingAppointmentError):
            controller.create_appointment(at, patient, therapist)

    def test_appointments_are_saved(self):
        controller = AppointmentController()
        patient = User(id=uuid4(), firstname="Jane", lastname="Doe")
        therapist = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        temp = []

        for i in range(4):
            at = datetime.now() + timedelta(days=i + 1)
            temp.append(controller.create_appointment(at, patient, therapist))

        assert len(controller.appointments) == 4
        assert temp == controller.appointments

    def test_get_all_appointments_when_there_is_none(self):
        controller = AppointmentController()
        assert controller.get_all_appointments() == controller.appointments

    def test_get_all_appointments_when_there_is_one(self):
        controller = AppointmentController()
        patient = User(id=uuid4(), firstname="Jane", lastname="Doe")
        therapist = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        at = datetime.now() + timedelta(minutes=1)
        appointment = controller.create_appointment(at, patient, therapist)
        assert controller.get_all_appointments() == controller.appointments
        assert controller.get_all_appointments() == [appointment]

    def test_get_all_appointments_when_there_is_many(self):
        controller = AppointmentController()
        patient = User(id=uuid4(), firstname="Jane", lastname="Doe")
        therapist = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        at = datetime.now() + timedelta(days=1)
        appointments = []
        for i in range(3):
            appointments.append(
                controller.create_appointment(
                    at + timedelta(hours=i), patient, therapist
                )
            )
        assert controller.get_all_appointments() == controller.appointments
        assert controller.get_all_appointments() == appointments
