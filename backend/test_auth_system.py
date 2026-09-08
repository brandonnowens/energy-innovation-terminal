"""Automated tests for authentication, password hashing, JWT tokens, and membership scaffolding."""

import sys
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, SessionLocal
from app.models.user import User, PasswordResetToken

client = TestClient(app)

def run_tests():
    print("--> Initializing database tables...")
    init_db()
    
    db = SessionLocal()
    # Clean up any existing test user
    db.query(PasswordResetToken).delete()
    db.query(User).filter(User.email.in_(["innovator@ny-cleanenergy.org", "testuser@example.com"])).delete()
    db.commit()
    db.close()
    
    print("\n[1] Testing Registration with Minimal Info (Email + Password)...")
    reg_payload = {
        "email": "innovator@ny-cleanenergy.org",
        "password": "SecurePassword123!",
        "full_name": "Dr. Jordan Hayes",
        "organization_name": "Empire CleanTech Labs"
    }
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 200, f"Register failed: {res.status_code} {res.text}"
    data = res.json()
    assert "access_token" in data, "Token missing in registration response"
    assert data["user"]["email"] == "innovator@ny-cleanenergy.org"
    assert data["user"]["tier"] == "free_public_benefit"
    assert data["user"]["public_benefit_access"] is True
    print("  [OK] Minimal registration succeeded. Free Public Benefit full access granted.")
    
    token = data["access_token"]
    
    print("\n[2] Testing Duplicate Registration Prevention...")
    res_dup = client.post("/api/auth/register", json={
        "email": "innovator@ny-cleanenergy.org",
        "password": "AnotherPassword456!"
    })
    assert res_dup.status_code == 400, f"Expected 400 for duplicate email, got: {res_dup.status_code}"
    print("  [OK] Duplicate email safely prevented.")
    
    print("\n[3] Testing Login with Valid Credentials...")
    login_res = client.post("/api/auth/login", json={
        "email": "innovator@ny-cleanenergy.org",
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.status_code} {login_res.text}"
    login_data = login_res.json()
    assert "access_token" in login_data
    assert login_data["user"]["full_name"] == "Dr. Jordan Hayes"
    print("  [OK] Login verified with hash matching.")
    
    print("\n[4] Testing Login with Invalid Password...")
    bad_login = client.post("/api/auth/login", json={
        "email": "innovator@ny-cleanenergy.org",
        "password": "WrongPassword!!!"
    })
    assert bad_login.status_code == 401, f"Expected 401 for wrong password, got: {bad_login.status_code}"
    print("  [OK] Unauthorized rejection on bad password.")
    
    print("\n[5] Testing /api/auth/me Profile & Entitlement Endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200, f"Me failed: {me_res.status_code} {me_res.text}"
    me_data = me_res.json()
    assert me_data["user"]["email"] == "innovator@ny-cleanenergy.org"
    assert me_data["user"]["public_benefit_access"] is True
    print("  [OK] /api/auth/me validated Bearer token payload.")
    
    print("\n[6] Testing Profile Update...")
    upd_res = client.put("/api/auth/me", headers=headers, json={
        "full_name": "Dr. Jordan Hayes, PhD",
        "organization_name": "Empire State Energy Innovation"
    })
    assert upd_res.status_code == 200
    assert upd_res.json()["user"]["full_name"] == "Dr. Jordan Hayes, PhD"
    print("  [OK] Profile update succeeded.")
    
    print("\n[7] Testing Password Change...")
    pwd_res = client.post("/api/auth/change-password", headers=headers, json={
        "current_password": "SecurePassword123!",
        "new_password": "NewUltraSecurePassword999!"
    })
    assert pwd_res.status_code == 200, f"Change password failed: {pwd_res.status_code} {pwd_res.text}"
    
    # Verify login with new password
    new_login = client.post("/api/auth/login", json={
        "email": "innovator@ny-cleanenergy.org",
        "password": "NewUltraSecurePassword999!"
    })
    assert new_login.status_code == 200
    token = new_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("  [OK] Password successfully changed and new password verified.")
    
    print("\n[8] Testing Password Recovery Flow (Forgot / Reset)...")
    forgot_res = client.post("/api/auth/forgot-password", json={"email": "innovator@ny-cleanenergy.org"})
    assert forgot_res.status_code == 200
    reset_token = forgot_res.json()["reset_token"]
    assert reset_token is not None, "Reset token should be returned"
    
    reset_res = client.post("/api/auth/reset-password", json={
        "token": reset_token,
        "new_password": "ResetPasswordRecovered2026!"
    })
    assert reset_res.status_code == 200
    
    # Try logging in with reset password
    recover_login = client.post("/api/auth/login", json={
        "email": "innovator@ny-cleanenergy.org",
        "password": "ResetPasswordRecovered2026!"
    })
    assert recover_login.status_code == 200
    print("  [OK] Password reset token generated, verified, and consumed.")
    
    print("\n[9] Testing Membership Manifest & Tier Scaffolding...")
    mem_res = client.get("/api/auth/membership", headers=headers)
    assert mem_res.status_code == 200
    mem_data = mem_res.json()
    assert mem_data["membership_manifest"]["public_benefit_mode"] is True
    assert len(mem_data["membership_manifest"]["tiers"]) == 3
    print("  [OK] Membership manifest verified with Public Benefit default and Pro/Enterprise scaffolding.")
    
    print("\n=======================================================")
    print("ALL AUTHENTICATION & MEMBERSHIP BACKEND TESTS PASSED! [OK]")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
