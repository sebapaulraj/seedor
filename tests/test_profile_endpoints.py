"""
Tests for profile endpoints:
- PUT /seedor/1.0/profile/update
- GET /seedor/1.0/profile/seedor/{id}

These tests focus on authentication and input validation. DB-dependent tests are marked as skipped because the test environment
may not have the application's database tables initialized.
"""

import pytest
from starlette.testclient import TestClient
from app.main import app
from app.api.auth import create_access_token
import base64

client = TestClient(app)

# Helpers
def get_basic_auth_headers():
    # credentials come from server.dev.properties
    credentials = base64.b64encode(b"seedordevuser:SeedorDev#1234").decode()
    return {"Authorization": f"Basic {credentials}"}


def create_bearer_token(userid: str = "testuser", profileId: str = "testprofile", email: str = "test@example.com"):
    payload = {"userid": userid, "profileId": profileId, "email": email}
    return create_access_token(payload)


# ------------------ profile update tests ------------------
class TestProfileUpdate:
    def test_profile_update_no_auth(self):
        response = client.put(
            "/seedor/1.0/profile/update",
            json={
                "seedorId": "sid123",
                    "preferedName": "Joe",
                    "firstName": "Joe",
                    "middleName": "Mid",
                    "lastName": "Smith",
                    "phone": "1234567890",
                    "countryCode": "+01",
                    "countryName": "USA",
                    "profileType": "basic"
            }
        )
        assert response.status_code == 401

    def test_profile_update_invalid_token(self):
        response = client.put(
            "/seedor/1.0/profile/update",
            headers={"Authorization": "Bearer invalidtoken"},
            json={
                "seedorId": "sid123",
                    "preferedName": "Joe",
                    "firstName": "Joe",
                    "middleName": "Mid",
                    "lastName": "Smith",
                    "phone": "1234567890",
                    "countryCode": "+01",
                    "countryName": "USA",
                    "profileType": "basic"
            }
        )
        assert response.status_code == 401

    def test_profile_update_invalid_payload(self):
        # missing required fields will cause validation error (min_length)
        token = create_bearer_token()
        response = client.put(
            "/seedor/1.0/profile/update",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "seedorId": "s",
                "preferedName": "J",
                # missing most fields
            }
        )
        assert response.status_code == 422

    @pytest.mark.skip(reason="Requires DB and existing profile record")
    def test_profile_update_success(self):
        token = create_bearer_token(userid="existinguser", profileId="existingprofile", email="existing@example.com")
        response = client.put(
            "/seedor/1.0/profile/update",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "seedorId": "sid123",
                "preferedName": "Joe",
                "firstName": "Joe",
                "middleName": "Mid",
                "lastName": "Smith",
                "phone": "1234567890",
                "countryCode": "+01",
                "countryName": "USA",
                "profileType": "basic"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("statuscode") == "SUCCESS"


# ------------------ validate seedor id tests ------------------
class TestValidateSeedorId:
    def test_validate_seedor_no_auth(self):
        response = client.get("/seedor/1.0/profile/seedor/testid")
        assert response.status_code == 401

    def test_validate_seedor_invalid_token(self):
        response = client.get("/seedor/1.0/profile/seedor/testid", headers={"Authorization": "Bearer bad"})
        assert response.status_code == 401

    def test_validate_seedor_id_too_short(self):
        token = create_bearer_token()
        response = client.get("/seedor/1.0/profile/seedor/ab", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 422

    @pytest.mark.skip(reason="Requires DB to check uniqueness")
    def test_validate_seedor_success_available(self):
        token = create_bearer_token()
        response = client.get("/seedor/1.0/profile/seedor/uniqueid123", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data.get("statuscode") == "SUCCESS"
