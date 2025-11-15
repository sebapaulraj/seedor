import os
import pytest
from app.db.db import SessionLocal
from app.db.usermodel import Profile, User
from app.db.addressmodel import Address
from app.api.auth import hash_password


@pytest.fixture(scope="session")
def integration():
    """
    Opt-in integration fixture.
    - If RUN_INTEGRATION is not set to 1 (or true), the fixture will skip tests that require DB.
    - If enabled, seeds minimal Profile and Address rows and yields control to tests.
    - Cleans up created rows on teardown.
    """
    run_flag = os.getenv("RUN_INTEGRATION", "0").lower()
    if run_flag not in ("1", "true", "yes"):
        pytest.skip("Integration tests skipped (set RUN_INTEGRATION=1 to enable)")

    db = SessionLocal()
    try:
        # Clean any leftover test rows from previous runs (safe for dev env)
        db.query(Address).filter(Address.addressId.like("TESTSEEDOR%") ).delete(synchronize_session=False)
        db.query(Profile).filter(Profile.idprofile == "testprofile").delete(synchronize_session=False)
        db.query(Profile).filter(Profile.authIduser == "testuser").delete(synchronize_session=False)
        db.query(User).filter(User.iduser == "testuser").delete(synchronize_session=False)
        db.commit()

        # Seed or update a minimal user (Profile.authIduser FK references user.iduser)
        existing_user = db.query(User).filter(User.iduser == "testuser").one_or_none()
        if existing_user is None:
            user = User(
                iduser="testuser",
                name="Test User",
                email="test@example.com",
                password=hash_password("password123"),
                is_active=True,
                createdBy="test",
                updatedBy="test",
            )
            db.add(user)
            db.commit()
        else:
            # update non-sensitive fields
            existing_user.email = "test@example.com"
            existing_user.name = "Test User"
            existing_user.updatedBy = "test"
            db.commit()

        # Seed or update a minimal profile matching tests' default token payload
        existing_profile = db.query(Profile).filter(Profile.authIduser == "testuser").one_or_none()
        if existing_profile is None:
            profile = Profile(
                idprofile="testprofile",
                authIduser="testuser",
                seedorId="TESTSEEDOR",
                isValidSeedorId=True,
                preferedName="TestUser",
                firstName="T",
                middleName="",
                lastName="User",
                email="test@example.com",
                phone="123456",
                countryCode="CC",
                countryName="Country",
                profileType="user",
                createdBy="test",
                updatedBy="test",
            )
            db.add(profile)
            db.commit()
        else:
            existing_profile.seedorId = "TESTSEEDOR"
            existing_profile.isValidSeedorId = True
            existing_profile.preferedName = "TestUser"
            existing_profile.email = "test@example.com"
            existing_profile.updatedBy = "test"
            db.commit()

        # Seed a minimal address for delete/update/get tests
        address = Address(
            idUser="testuser",
            addressId="TESTSEEDOR/AD/1",
            isActive=True,
            label="Home",
            primaryAddress=True,
            street="123 Test St",
            area="Area",
            city="City",
            stateorProvince="State",
            postalCode="00000",
            country="Country",
            createdBy="test",
            updatedBy="test",
        )
        db.add(address)
        db.commit()

        yield

    finally:
        try:
            # Remove seeded rows (match by our test identifiers)
            db.query(Address).filter(Address.addressId.like("TESTSEEDOR%")).delete(synchronize_session=False)
            db.query(Profile).filter(Profile.idprofile == "testprofile").delete(synchronize_session=False)
            # remove user created for FK
            db.query(User).filter(User.iduser == "testuser").delete(synchronize_session=False)
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
