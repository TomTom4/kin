from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_hello_world():
    response = client.get("/")
    assert response.status_code == 200


class TestAppointments:

    def test_get_all_appointments_with_no_appointments(self):
        response = client.get("/appointments")
        assert response.status_code == 200
        assert response.json() == {"appointments": []}

