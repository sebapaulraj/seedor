"""
Test suite for user-related endpoints
Tests for: register, userName, login, resetPassword

NOTE: These tests require the PostgreSQL database to be running and configured
in server.dev.properties. Tests will interact with the real database.
"""
import pytest
from starlette.testclient import TestClient
from app.main import app
import base64
import uuid

client = TestClient(app)

# Basic Auth Helper
def get_basic_auth_headers():
    """Generate basic auth headers for testing"""
    # Use the actual credentials from server.dev.properties
    credentials = base64.b64encode(b"seedordevuser:SeedorDev#1234").decode()
    return {"Authorization": f"Basic {credentials}"}



# ==================== Register Endpoint Tests ====================

class TestRegisterEndpoint:
    """Test cases for POST /seedor/1.0/auth/register"""

    def test_register_invalid_email(self):
        """Test registration with invalid email format"""
        response = client.post(
            "/seedor/1.0/auth/register",
            headers=get_basic_auth_headers(),
            json={
                "name": "John Doe",
                "email": "invalid-email",
                "password": "SecurePass123"
            }
        )
        assert response.status_code == 422  # Validation error

    def test_register_short_password(self):
        """Test registration with password too short (min 8 chars)"""
        response = client.post(
            "/seedor/1.0/auth/register",
            headers=get_basic_auth_headers(),
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "Short1"
            }
        )
        assert response.status_code == 422  # Validation error

    def test_register_short_name(self):
        """Test registration with name too short (min 3 chars)"""
        response = client.post(
            "/seedor/1.0/auth/register",
            headers=get_basic_auth_headers(),
            json={
                "name": "Jo",
                "email": "john@example.com",
                "password": "SecurePass123"
            }
        )
        assert response.status_code == 422  # Validation error

    def test_register_missing_fields(self):
        """Test registration with missing required fields"""
        response = client.post(
            "/seedor/1.0/auth/register",
            headers=get_basic_auth_headers(),
            json={
                "name": "John Doe"
                # Missing email and password
            }
        )
        assert response.status_code == 422

    def test_register_no_auth_header(self):
        """Test registration without basic auth header"""
        response = client.post(
            "/seedor/1.0/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "SecurePass123"
            }
        )
        assert response.status_code == 401

    def test_register_invalid_auth_header(self):
        """Test registration with invalid basic auth header"""
        response = client.post(
            "/seedor/1.0/auth/register",
            headers={"Authorization": "Bearer invalid"},
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "SecurePass123"
            }
        )
        assert response.status_code == 401

    def test_register_wrong_auth_credentials(self):
        """Test registration with wrong basic auth credentials"""
        wrong_credentials = base64.b64encode(b"wronguser:wrongpass").decode()
        response = client.post(
            "/seedor/1.0/auth/register",
            headers={"Authorization": f"Basic {wrong_credentials}"},
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "SecurePass123"
            }
        )
        assert response.status_code == 401


# ==================== UserName Endpoint Tests ====================

class TestUserNameEndpoint:
    """Test cases for GET /seedor/1.0/auth/user/{email}"""

    def test_get_user_invalid_email_format(self):
        """Test user lookup with invalid email format"""
        response = client.get(
            "/seedor/1.0/auth/user/invalidemail",
            headers=get_basic_auth_headers()
        )
        assert response.status_code == 400
        assert "Invalid email format" in response.json()["detail"]

    def test_get_user_email_too_short(self):
        """Test user lookup with email below minimum length"""
        response = client.get(
            "/seedor/1.0/auth/user/ab",
            headers=get_basic_auth_headers()
        )
        assert response.status_code == 422

    def test_get_user_no_auth_header(self):
        """Test user lookup without basic auth header"""
        response = client.get(
            "/seedor/1.0/auth/user/test@example.com"
        )
        assert response.status_code == 401

    def test_get_user_invalid_auth(self):
        """Test user lookup with invalid auth"""
        wrong_credentials = base64.b64encode(b"wrong:wrong").decode()
        response = client.get(
            "/seedor/1.0/auth/user/test@example.com",
            headers={"Authorization": f"Basic {wrong_credentials}"}
        )
        assert response.status_code == 401

    def test_get_user_with_special_chars_in_email(self):
        """Test user lookup with special characters in email"""
        response = client.get(
            "/seedor/1.0/auth/user/test+tag@example.com",
            headers=get_basic_auth_headers()
        )
        # Should either return 200, 400 (user not found), but NOT 400 for format
        assert response.status_code in [200, 400]


# ==================== Login Endpoint Tests ====================

class TestLoginEndpoint:
    """Test cases for POST /seedor/1.0/auth/login"""

    def test_login_invalid_email_format(self):
        """Test login with invalid email format"""
        response = client.post(
            "/seedor/1.0/auth/login",
            headers=get_basic_auth_headers(),
            json={
                "email": "invalidemail",
                "password": "SomePassword123"
            }
        )
        assert response.status_code == 422

    def test_login_short_password(self):
        """Test login with password too short"""
        response = client.post(
            "/seedor/1.0/auth/login",
            headers=get_basic_auth_headers(),
            json={
                "email": "test@example.com",
                "password": "Short1"
            }
        )
        assert response.status_code == 422

    def test_login_no_auth_header(self):
        """Test login without basic auth header"""
        response = client.post(
            "/seedor/1.0/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123"
            }
        )
        assert response.status_code == 401

    def test_login_invalid_auth(self):
        """Test login with invalid basic auth"""
        wrong_credentials = base64.b64encode(b"wrong:wrong").decode()
        response = client.post(
            "/seedor/1.0/auth/login",
            headers={"Authorization": f"Basic {wrong_credentials}"},
            json={
                "email": "test@example.com",
                "password": "TestPassword123"
            }
        )
        assert response.status_code == 401

    def test_login_missing_fields(self):
        """Test login with missing required fields"""
        response = client.post(
            "/seedor/1.0/auth/login",
            headers=get_basic_auth_headers(),
            json={
                "email": "test@example.com"
                # Missing password
            }
        )
        assert response.status_code == 422


# ==================== Reset Password Tests ====================

class TestResetPasswordEndpoint:
    """Test cases for password reset endpoints"""

    def test_reset_password_request_invalid_email(self):
        """Test password reset request with invalid email"""
        response = client.get(
            "/seedor/1.0/auth/reset/invalidemail",
            headers=get_basic_auth_headers()
        )
        assert response.status_code == 400

    def test_reset_password_request_no_auth(self):
        """Test password reset request without auth"""
        response = client.get(
            "/seedor/1.0/auth/reset/test@example.com"
        )
        assert response.status_code == 401

    def test_reset_password_request_invalid_auth(self):
        """Test password reset request with invalid auth"""
        wrong_credentials = base64.b64encode(b"wrong:wrong").decode()
        response = client.get(
            "/seedor/1.0/auth/reset/test@example.com",
            headers={"Authorization": f"Basic {wrong_credentials}"}
        )
        assert response.status_code == 401


# ==================== Health Check Tests ====================

class TestHealthEndpoint:
    """Test cases for GET /seedor/1.0/health"""

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/seedor/1.0/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_health_check_no_auth_required(self):
        """Test that health check doesn't require authentication"""
        response = client.get("/seedor/1.0/health")
        assert response.status_code == 200


# ==================== Database Integration Tests ====================

class TestDatabaseIntegration:
    """Integration tests that require database connectivity"""

    @pytest.mark.skip(reason="Requires database setup and data management")
    def test_register_and_login_flow(self):
        """Test complete registration and login flow"""
        email = f"testuser_{uuid.uuid4()}@example.com"
        password = "TestPassword123"
        name = "Test User"

        # Register
        register_response = client.post(
            "/seedor/1.0/auth/register",
            headers=get_basic_auth_headers(),
            json={
                "name": name,
                "email": email,
                "password": password
            }
        )
        
        if register_response.status_code == 200:
            assert register_response.json()["statuscode"] == "SUCCESS"
            
            # Login
            login_response = client.post(
                "/seedor/1.0/auth/login",
                headers=get_basic_auth_headers(),
                json={
                    "email": email,
                    "password": password
                }
            )
            assert login_response.status_code == 200
            assert "X-Access-Token" in login_response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
