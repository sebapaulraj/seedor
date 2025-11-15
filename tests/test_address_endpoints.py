"""
Tests for address endpoints:
- POST /seedor/1.0/address/add
- PUT  /seedor/1.0/address/update
- GET  /seedor/1.0/address/{id}
- GET  /seedor/1.0/address
- DELETE /seedor/1.0/address/id

These tests focus on authentication and input validation. DB-dependent success tests are skipped.
"""

import pytest
from starlette.testclient import TestClient
from app.main import app
from app.api.auth import create_access_token
import base64

client = TestClient(app)

# Helpers

def get_basic_auth_headers():
    credentials = base64.b64encode(b"seedordevuser:SeedorDev#1234").decode()
    return {"Authorization": f"Basic {credentials}"}


def create_bearer_token(userid: str = "testuser", profileId: str = "testprofile", email: str = "test@example.com"):
    payload = {"userid": userid, "profileId": profileId, "email": email}
    return create_access_token(payload)


# Sample valid payload for AddressNewIN
VALID_ADDRESS_PAYLOAD = {
    "label": "Home",
    "street": "123 Main St",
    "area": "Central",
    "city": "Metropolis",
    "stateorProvince": "State",
    "postalCode": "12345",
    "country": "Wonderland"
}

# ------------------- Add Address -------------------
class TestAddAddress:
    def test_add_no_auth(self):
        response = client.post("/seedor/1.0/address/add", json=VALID_ADDRESS_PAYLOAD)
        # body is valid, so function should try to read the bearer token and return 401
        assert response.status_code == 401

    def test_add_invalid_token(self):
        response = client.post("/seedor/1.0/address/add", headers={"Authorization": "Bearer bad"}, json=VALID_ADDRESS_PAYLOAD)
        assert response.status_code == 401

    def test_add_missing_fields(self):
        token = create_bearer_token()
        payload = {"label": "Home"}  # missing required fields
        response = client.post("/seedor/1.0/address/add", headers={"Authorization": f"Bearer {token}"}, json=payload)
        assert response.status_code == 422

    def test_add_success(self, integration):
        token = create_bearer_token(userid="testuser", profileId="testprofile", email="test@example.com")
        response = client.post("/seedor/1.0/address/add", headers={"Authorization": f"Bearer {token}"}, json=VALID_ADDRESS_PAYLOAD)
        assert response.status_code == 200
        data = response.json()
        assert data.get("statuscode") == "SUCCESS"


# ------------------- Update Address -------------------
class TestUpdateAddress:
    def test_update_no_auth(self):
        payload = {"idaddress": "someid", "label": "New label", "primaryAddress": True}
        response = client.put("/seedor/1.0/address/update", json=payload)
        assert response.status_code == 401

    def test_update_invalid_token(self):
        payload = {"idaddress": "someid", "label": "New label", "primaryAddress": True}
        response = client.put("/seedor/1.0/address/update", headers={"Authorization": "Bearer bad"}, json=payload)
        assert response.status_code == 401

    def test_update_missing_id(self):
        token = create_bearer_token()
        payload = {"label": "New label", "primaryAddress": True}
        response = client.put("/seedor/1.0/address/update", headers={"Authorization": f"Bearer {token}"}, json=payload)
        assert response.status_code == 422

    def test_update_success(self, integration):
        token = create_bearer_token(userid="testuser", profileId="testprofile")
        # use seeded addressId to retrieve idaddress via GET then update
        # The API expects idaddress (primary key) for update; our seeded address has an auto-generated idaddress
        # We'll query the GET by addressId to obtain idaddress before calling update
        get_resp = client.get(f"/seedor/1.0/address/TESTSEEDOR/AD/1", headers={"Authorization": f"Bearer {token}"})
        assert get_resp.status_code == 200
        list_addr = get_resp.json().get("listAddress")
        assert list_addr and len(list_addr) >= 1
        idaddress = list_addr[0].get("idaddress")
        payload = {"idaddress": idaddress, "label": "Updated", "primaryAddress": False}
        response = client.put("/seedor/1.0/address/update", headers={"Authorization": f"Bearer {token}"}, json=payload)
        assert response.status_code == 200
        assert response.json().get("statuscode") == "SUCCESS"


# ------------------- Get Address by Id -------------------
class TestGetAddressById:
    def test_get_by_id_no_auth(self):
        response = client.get("/seedor/1.0/address/some/address/id")
        assert response.status_code == 401

    def test_get_by_id_invalid_token(self):
        response = client.get("/seedor/1.0/address/some/address/id", headers={"Authorization": "Bearer bad"})
        assert response.status_code == 401

    def test_get_by_id_too_short(self):
        token = create_bearer_token()
        response = client.get("/seedor/1.0/address/ab", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 422

    def test_get_by_id_success(self, integration):
        token = create_bearer_token(userid="testuser", profileId="testprofile")
        response = client.get("/seedor/1.0/address/TESTSEEDOR/AD/1", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json().get("statuscode") == "SUCCESS"


# ------------------- Get All Addresses -------------------
class TestGetAllAddresses:
    def test_get_all_no_auth(self):
        response = client.get("/seedor/1.0/address")
        assert response.status_code == 401

    def test_get_all_invalid_token(self):
        response = client.get("/seedor/1.0/address", headers={"Authorization": "Bearer bad"})
        assert response.status_code == 401

    def test_get_all_success(self, integration):
        token = create_bearer_token(userid="testuser", profileId="testprofile")
        response = client.get("/seedor/1.0/address", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json().get("statuscode") == "SUCCESS"


# ------------------- Delete Address -------------------
class TestDeleteAddress:
    def test_delete_no_auth(self):
        response = client.request("DELETE", "/seedor/1.0/address/id", json={"idaddress": "addr1"})
        # body valid but no auth -> should be 401
        assert response.status_code == 401

    def test_delete_invalid_token(self):
        response = client.request("DELETE", "/seedor/1.0/address/id", headers={"Authorization": "Bearer bad"}, json={"idaddress": "addr1"})
        assert response.status_code == 401

    def test_delete_missing_body(self):
        token = create_bearer_token()
        response = client.delete("/seedor/1.0/address/id", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 422

    def test_delete_success(self, integration):
        token = create_bearer_token(userid="testuser", profileId="testprofile")
        # fetch idaddress for seeded address
        get_resp = client.get(f"/seedor/1.0/address/TESTSEEDOR/AD/1", headers={"Authorization": f"Bearer {token}"})
        assert get_resp.status_code == 200
        list_addr = get_resp.json().get("listAddress")
        assert list_addr and len(list_addr) >= 1
        idaddress = list_addr[0].get("idaddress")
        response = client.request("DELETE", "/seedor/1.0/address/id", headers={"Authorization": f"Bearer {token}"}, json={"idaddress": idaddress})
        assert response.status_code == 200
        assert response.json().get("statuscode") == "SUCCESS"
