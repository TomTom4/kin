from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from app.exceptions import InvalidDateAndTimeError, OverlappingAppointmentError
from app.main import AppointmentController
from app.models import User


class TestCreatingAppointments:

    @pytest.mark.asyncio
    async def test_create_an_appointment(self):
        controller = AppointmentController()
        patient = User(id=uuid4(), firstname="Jane", lastname="Doe")
        therapist = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        at = datetime.now() + timedelta(minutes=1)
        appointments = await controller.create_appointment(at, patient, therapist)
        assert appointments.id
        assert appointments.start_at == at
        assert appointments.patient_id == patient.id
        assert appointments.therapist_id == therapist.id

    @pytest.mark.asyncio
    async def test_create_appointment_in_the_past(self):
        controller = AppointmentController()
        patient = User(id=uuid4(), firstname="Jane", lastname="Doe")
        therapist = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        at = datetime.now() - timedelta(days=1)
        with pytest.raises(InvalidDateAndTimeError):
            await controller.create_appointment(at, patient, therapist)

    @pytest.mark.asyncio
    async def test_appointments_cannot_overlap(self):
        controller = AppointmentController()
        patient = User(id=uuid4(), firstname="Jane", lastname="Doe")
        therapist = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        at = datetime.now() + timedelta(minutes=1)
        await controller.create_appointment(at, patient, therapist)
        with pytest.raises(OverlappingAppointmentError):
            await controller.create_appointment(at, patient, therapist)


class TestGetAppointments:

    @pytest.mark.asyncio
    async def test_appointments_are_saved(self):
        controller = AppointmentController()
        patient = User(id=uuid4(), firstname="Jane", lastname="Doe")
        therapist = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        temp = []

        for i in range(4):
            at = datetime.now() + timedelta(days=i + 1)
            temp.append(await controller.create_appointment(at, patient, therapist))

        assert len(controller.appointments) == 4
        assert temp == controller.appointments

    @pytest.mark.asyncio
    async def test_get_all_appointments_when_there_is_none(self):
        controller = AppointmentController()
        assert await controller.get_all_appointments() == controller.appointments

    @pytest.mark.asyncio
    async def test_get_all_appointments_when_there_is_one(self):
        controller = AppointmentController()
        patient = User(id=uuid4(), firstname="Jane", lastname="Doe")
        therapist = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        at = datetime.now() + timedelta(minutes=1)
        appointment = await controller.create_appointment(at, patient, therapist)
        assert await controller.get_all_appointments() == controller.appointments
        assert await controller.get_all_appointments() == [appointment]

    @pytest.mark.asyncio
    async def test_get_all_appointments_when_there_is_many(self):
        controller = AppointmentController()
        patient = User(id=uuid4(), firstname="Jane", lastname="Doe")
        therapist = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        at = datetime.now() + timedelta(days=1)
        appointments = []
        for i in range(3):
            appointments.append(
                await controller.create_appointment(
                    at + timedelta(hours=i), patient, therapist
                )
            )
        assert await controller.get_all_appointments() == controller.appointments
        assert await controller.get_all_appointments() == appointments

    @pytest.mark.asyncio
    async def test_get_appointments_filtered_by_patient_id(self):
        controller = AppointmentController()
        patient_1 = User(id=uuid4(), firstname="Jane", lastname="Doe")
        patient_2 = User(id=uuid4(), firstname="Jasmin", lastname="Doe")
        therapist_1 = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        therapist_2 = User(id=uuid4(), firstname="John", lastname="Dolittle")
        at = datetime.now() + timedelta(days=1)
        for i in range(3):
            await controller.create_appointment(
                at + timedelta(hours=i), patient_1, therapist_1
            )
            await controller.create_appointment(
                at + timedelta(hours=i), patient_2, therapist_2
            )

        appointments = await controller.get_all_appointments(patient_id=patient_1.id)
        assert len(appointments) == 3
        for an_appointment in appointments:
            assert an_appointment.patient_id == patient_1.id

    @pytest.mark.asyncio
    async def test_get_appointments_filtered_by_therapist_id(self):
        controller = AppointmentController()
        patient_1 = User(id=uuid4(), firstname="Jane", lastname="Doe")
        patient_2 = User(id=uuid4(), firstname="Jasmin", lastname="Doe")
        therapist_1 = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        therapist_2 = User(id=uuid4(), firstname="John", lastname="Dolittle")
        at = datetime.now() + timedelta(days=1)
        for i in range(3):
            await controller.create_appointment(
                at + timedelta(hours=i), patient_1, therapist_1
            )
            await controller.create_appointment(
                at + timedelta(hours=i), patient_2, therapist_2
            )

        appointments = await controller.get_all_appointments(
            therapist_id=therapist_1.id
        )
        assert len(appointments) == 3
        for an_appointment in appointments:
            assert an_appointment.therapist_id == therapist_1.id

    @pytest.mark.asyncio
    async def test_get_appointments_filtered_by_date(self):
        controller = AppointmentController()
        patient_1 = User(id=uuid4(), firstname="Jane", lastname="Doe")
        patient_2 = User(id=uuid4(), firstname="Jasmin", lastname="Doe")
        therapist_1 = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        therapist_2 = User(id=uuid4(), firstname="John", lastname="Dolittle")
        at = datetime.now() + timedelta(days=1)
        await controller.create_appointment(at, patient_1, therapist_1)
        await controller.create_appointment(at, patient_2, therapist_2)
        for i in range(3):
            await controller.create_appointment(
                at + timedelta(days=i + 1), patient_2, therapist_2
            )
        appointments = await controller.get_all_appointments(day=at.date())
        assert len(appointments) == 2
        for an_appointment in appointments:
            assert an_appointment.start_at.date() == at.date()

    @pytest.mark.asyncio
    async def test_get_all_appointments_filtered_by_multiple_filters(self):
        controller = AppointmentController()
        patient_1 = User(id=uuid4(), firstname="Jane", lastname="Doe")
        patient_2 = User(id=uuid4(), firstname="Jasmin", lastname="Doe")
        therapist_1 = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        therapist_2 = User(id=uuid4(), firstname="John", lastname="Dolittle")
        at = datetime.now() + timedelta(days=1)
        await controller.create_appointment(at, patient_1, therapist_2)
        await controller.create_appointment(at, patient_2, therapist_1)
        for i in range(3):
            await controller.create_appointment(
                at + timedelta(days=i + 1), patient_2, therapist_2
            )
        appointments = await controller.get_all_appointments(
            patient_id=patient_1.id, therapist_id=therapist_1.id
        )
        assert len(appointments) == 0

        appointments = await controller.get_all_appointments(
            patient_id=patient_1.id, day=at.date()
        )
        assert len(appointments) == 1
        assert appointments[0].therapist_id == therapist_2.id
        assert appointments[0].patient_id == patient_1.id

        appointments = await controller.get_all_appointments(
            therapist_id=therapist_2.id, day=at.date()
        )
        assert len(appointments) == 1
        assert appointments[0].therapist_id == therapist_2.id
        assert appointments[0].patient_id == patient_1.id
