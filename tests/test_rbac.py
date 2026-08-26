import unittest
import json
import time
import sys
import os

sys.path.append('.')
from backend.main import app, create_token, decode_token
from backend.database.connection import SessionLocal
from backend.database.models import User

class TestRBACAndAuth(unittest.TestCase):
    def setUp(self):
        # Create Flask test client
        self.app = app
        self.client = self.app.test_client()
        self.app.testing = True
        
        # Insert a set of test users with different roles for authentication tests
        self.db = SessionLocal()
        
        # Clean up existing test users if they exist
        self.db.query(User).filter(User.email.like("test_%@muleshield.psb")).delete(synchronize_session=False)
        self.db.commit()
        
        # Create test users
        from werkzeug.security import generate_password_hash
        pwd_hash = generate_password_hash("password123")
        
        self.test_admin = User(email="test_admin@muleshield.psb", password_hash=pwd_hash, role="ADMIN")
        self.test_analyst = User(email="test_analyst@muleshield.psb", password_hash=pwd_hash, role="ANALYST")
        self.test_investigator = User(email="test_investigator@muleshield.psb", password_hash=pwd_hash, role="INVESTIGATOR")
        self.test_viewer = User(email="test_viewer@muleshield.psb", password_hash=pwd_hash, role="VIEWER")
        
        self.db.add_all([self.test_admin, self.test_analyst, self.test_investigator, self.test_viewer])
        self.db.commit()

    def tearDown(self):
        # Clean up database test entries
        self.db.query(User).filter(User.email.like("test_%@muleshield.psb")).delete(synchronize_session=False)
        self.db.commit()
        self.db.close()

    def test_valid_login(self):
        payload = {
            "email": "test_analyst@muleshield.psb",
            "password": "password123"
        }
        res = self.client.post("/api/auth/login", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("token", data)
        self.assertEqual(data["email"], "test_analyst@muleshield.psb")
        self.assertEqual(data["role"], "ANALYST")

    def test_invalid_login(self):
        payload = {
            "email": "test_analyst@muleshield.psb",
            "password": "wrongpassword"
        }
        res = self.client.post("/api/auth/login", json=payload)
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertIn("error", data)

    def test_signup_role_restriction(self):
        # Admin role signup should be rejected
        payload = {
            "email": "test_fake_admin@muleshield.psb",
            "password": "password123",
            "role": "ADMIN"
        }
        res = self.client.post("/api/auth/signup", json=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Self-registration is only allowed", res.get_json()["error"])

        # Analyst role signup should succeed
        payload = {
            "email": "test_new_analyst@muleshield.psb",
            "password": "password123",
            "role": "ANALYST"
        }
        res = self.client.post("/api/auth/signup", json=payload)
        self.assertEqual(res.status_code, 200)

    def test_auth_rate_limiting(self):
        from backend.main import auth_limiter
        auth_limiter.requests = {} # reset
        
        payload = {
            "email": "test_analyst@muleshield.psb",
            "password": "wrongpassword"
        }
        
        # Hit login endpoint 10 times
        for _ in range(10):
            res = self.client.post("/api/auth/login", json=payload)
            self.assertEqual(res.status_code, 401)
            
        # The 11th request should be blocked by rate limiting
        res = self.client.post("/api/auth/login", json=payload)
        self.assertEqual(res.status_code, 429)
        self.assertIn("Too many requests", res.get_json()["error"])
        
        # Reset limiter for subsequent tests
        auth_limiter.requests = {}

    def test_logout(self):
        token = create_token("test_analyst@muleshield.psb", "ANALYST")
        headers = {"Authorization": f"Bearer {token}"}
        res = self.client.post("/api/auth/logout", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["message"], "Logged out successfully")

    def test_unauthorized_api(self):
        # No header
        res = self.client.get("/api/cases")
        self.assertEqual(res.status_code, 401)
        
        # Invalid header
        res = self.client.get("/api/cases", headers={"Authorization": "Bearer garbage-token"})
        self.assertEqual(res.status_code, 401)

    def test_expired_session(self):
        # Generate an expired token
        import base64
        import hmac
        import hashlib
        from backend.main import JWT_SECRET_KEY
        
        exp = int(time.time()) - 3600 # 1 hour in the past
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {"email": "test_analyst@muleshield.psb", "role": "ANALYST", "exp": exp}
        
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        sig = hmac.new(JWT_SECRET_KEY, f"{header_b64}.{payload_b64}".encode(), hashlib.sha256).hexdigest()
        expired_token = f"{header_b64}.{payload_b64}.{sig}"
        
        res = self.client.get("/api/cases", headers={"Authorization": f"Bearer {expired_token}"})
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid or expired session token", res.get_json()["error"])

    def test_role_permissions_viewer(self):
        # Viewer token
        token = create_token("test_viewer@muleshield.psb", "VIEWER")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Viewer CAN read cases
        res = self.client.get("/api/cases", headers=headers)
        self.assertEqual(res.status_code, 200)
        
        # Viewer CANNOT update status
        res = self.client.post("/api/cases/9001/status", headers=headers, json={"status": "CLOSED"})
        self.assertEqual(res.status_code, 403)
        
        # Viewer CANNOT add notes
        res = self.client.post("/api/cases/9001/notes", headers=headers, json={"note": "Test Note"})
        self.assertEqual(res.status_code, 403)
        
        # Viewer CANNOT execute CBS freeze
        res = self.client.post("/api/cases/9001/cbs-freeze", headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_role_permissions_analyst(self):
        # Analyst token
        token = create_token("test_analyst@muleshield.psb", "ANALYST")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Analyst CAN read cases
        res = self.client.get("/api/cases", headers=headers)
        self.assertEqual(res.status_code, 200)
        
        # Analyst CAN add notes
        res = self.client.post("/api/cases/9001/notes", headers=headers, json={"note": "Test Note"})
        self.assertEqual(res.status_code, 200)
        
        # Analyst CANNOT update status (restricted to ADMIN and INVESTIGATOR)
        res = self.client.post("/api/cases/9001/status", headers=headers, json={"status": "CLOSED"})
        self.assertEqual(res.status_code, 403)
        
        # Analyst CANNOT freeze (restricted to ADMIN and INVESTIGATOR)
        res = self.client.post("/api/cases/9001/cbs-freeze", headers=headers)
        self.assertEqual(res.status_code, 403)
        
        # Analyst CANNOT view system audit logs (restricted to ADMIN)
        res = self.client.get("/api/audit-logs", headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_role_permissions_investigator(self):
        # Investigator token
        token = create_token("test_investigator@muleshield.psb", "INVESTIGATOR")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Investigator CAN read cases
        res = self.client.get("/api/cases", headers=headers)
        self.assertEqual(res.status_code, 200)
        
        # Investigator CAN update status
        res = self.client.post("/api/cases/9001/status", headers=headers, json={"status": "CLOSED"})
        self.assertEqual(res.status_code, 200)
        
        # Investigator CAN freeze
        res = self.client.post("/api/cases/9001/cbs-freeze", headers=headers)
        self.assertEqual(res.status_code, 200)
        
        # Investigator CANNOT predict raw metrics (restricted to ADMIN and ANALYST)
        res = self.client.post("/api/predict", headers=headers, json={"account_features": {}})
        self.assertEqual(res.status_code, 403)

    def test_role_permissions_admin(self):
        # Admin token
        token = create_token("test_admin@muleshield.psb", "ADMIN")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Admin CAN access everything
        res = self.client.get("/api/cases", headers=headers)
        self.assertEqual(res.status_code, 200)
        
        res = self.client.get("/api/audit-logs", headers=headers)
        self.assertEqual(res.status_code, 200)
        
        res = self.client.post("/api/admin/users", headers=headers, json={
            "email": "test_new_user@muleshield.psb",
            "password": "newpassword123",
            "role": "ANALYST"
        })
        self.assertEqual(res.status_code, 200)

if __name__ == "__main__":
    unittest.main()
