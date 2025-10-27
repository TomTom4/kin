from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from app.main import (
    AppointmentController,
    InvalidDateAndTimeError,
    OverlappingAppointmentError,
)
from app.models import User


class TestCreatingAppointments:

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


class TestGetAppointments:

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

    def test_get_appointments_filtered_by_patient_id(self):
        controller = AppointmentController()
        patient_1 = User(id=uuid4(), firstname="Jane", lastname="Doe")
        patient_2 = User(id=uuid4(), firstname="Jasmin", lastname="Doe")
        therapist_1 = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        therapist_2 = User(id=uuid4(), firstname="John", lastname="Dolittle")
        at = datetime.now() + timedelta(days=1)
        for i in range(3):
            controller.create_appointment(
                at + timedelta(hours=i), patient_1, therapist_1
            )
            controller.create_appointment(
                at + timedelta(hours=i), patient_2, therapist_2
            )

        appointments = controller.get_all_appointments(patient_id=patient_1.id)
        assert len(appointments) == 3
        for an_appointment in appointments:
            assert an_appointment.patient_id == patient_1.id

    def test_get_appointments_filtered_by_therapist_id(self):
        controller = AppointmentController()
        patient_1 = User(id=uuid4(), firstname="Jane", lastname="Doe")
        patient_2 = User(id=uuid4(), firstname="Jasmin", lastname="Doe")
        therapist_1 = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        therapist_2 = User(id=uuid4(), firstname="John", lastname="Dolittle")
        at = datetime.now() + timedelta(days=1)
        for i in range(3):
            controller.create_appointment(
                at + timedelta(hours=i), patient_1, therapist_1
            )
            controller.create_appointment(
                at + timedelta(hours=i), patient_2, therapist_2
            )

        appointments = controller.get_all_appointments(therapist_id=therapist_1.id)
        assert len(appointments) == 3
        for an_appointment in appointments:
            assert an_appointment.therapist_id == therapist_1.id

    def test_get_appointments_filtered_by_date(self):
        controller = AppointmentController()
        patient_1 = User(id=uuid4(), firstname="Jane", lastname="Doe")
        patient_2 = User(id=uuid4(), firstname="Jasmin", lastname="Doe")
        therapist_1 = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        therapist_2 = User(id=uuid4(), firstname="John", lastname="Dolittle")
        at = datetime.now() + timedelta(days=1)
        controller.create_appointment(at, patient_1, therapist_1)
        controller.create_appointment(at, patient_2, therapist_2)
        for i in range(3):
            controller.create_appointment(
                at + timedelta(days=i + 1), patient_2, therapist_2
            )
        appointments = controller.get_all_appointments(day=at.date())
        assert len(appointments) == 2
        for an_appointment in appointments:
            assert an_appointment.start_at.date() == at.date()

    def test_get_all_appointments_filtered_by_multiple_filters(self):
        controller = AppointmentController()
        patient_1 = User(id=uuid4(), firstname="Jane", lastname="Doe")
        patient_2 = User(id=uuid4(), firstname="Jasmin", lastname="Doe")
        therapist_1 = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        therapist_2 = User(id=uuid4(), firstname="John", lastname="Dolittle")
        at = datetime.now() + timedelta(days=1)
        controller.create_appointment(at, patient_1, therapist_2)
        controller.create_appointment(at, patient_2, therapist_1)
        for i in range(3):
            controller.create_appointment(
                at + timedelta(days=i + 1), patient_2, therapist_2
            )
        appointments = controller.get_all_appointments(
            patient_id=patient_1.id, therapist_id=therapist_1.id
        )
        assert len(appointments) == 0

        appointments = controller.get_all_appointments(
            patient_id=patient_1.id, day=at.date()
        )
        assert len(appointments) == 1
        assert appointments[0].therapist_id == therapist_2.id
        assert appointments[0].patient_id == patient_1.id
