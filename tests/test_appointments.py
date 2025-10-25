from datetime import datetime
from uuid import uuid4

from app.main import AppointmentController
from app.models import User


class TestAppointments:

    def test_create_an_appointment(self):
        controller = AppointmentController()
        patient = User(id=uuid4(), firstname="Jane", lastname="Doe")
        therapist = User(id=uuid4(), firstname="Stuart", lastname="Dolittle")
        at = datetime.now()
        appointments = controller.create_appointment(at, patient, therapist)
        assert appointments.id
        assert appointments.start_at == at
        assert appointments.patient_id == patient.id
        assert appointments.therapist_id == therapist.id
