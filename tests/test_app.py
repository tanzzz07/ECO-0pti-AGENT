import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"

sys.path.insert(0, str(BACKEND))
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-only-jwt-secret-with-at-least-32-bytes",
)
os.environ.setdefault("HUGGINGFACEHUB_API_TOKEN", "test-placeholder-token")

from main import app, db  # noqa: E402


class AppSmokeTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def test_ping_reports_healthy(self):
        response = self.client.get("/ping")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})
        response.close()

    def test_root_serves_login_page_and_assets_exist(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'id="login-form"', response.data)
        self.assertTrue((ROOT / "frontend" / "style.css").is_file())
        self.assertTrue((ROOT / "frontend" / "FullLogo_NoBuffer.jpg").is_file())
        response.close()

    def test_user_can_register_and_login(self):
        credentials = {
            "username": "ci-user",
            "email": "ci-user@example.com",
            "password": "correct-horse-battery-staple",
        }

        register_response = self.client.post("/register", json=credentials)
        login_response = self.client.post(
            "/login",
            json={
                "email": credentials["email"],
                "password": credentials["password"],
            },
        )
        payload = login_response.get_json()

        self.assertEqual(register_response.status_code, 201)
        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(payload["access_token"])
        self.assertEqual(payload["username"], credentials["username"])
        self.assertEqual(payload["role"], "user")
        register_response.close()
        login_response.close()

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            "/login",
            json={"email": "missing@example.com", "password": "incorrect"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"error": "Invalid credentials"})
        response.close()

    def test_register_rejects_duplicate_username(self):
        user1 = {
            "username": "shared-username",
            "email": "user1@example.com",
            "password": "password123",
        }
        user2 = {
            "username": "shared-username",
            "email": "user2@example.com",
            "password": "password123",
        }
        res1 = self.client.post("/register", json=user1)
        res2 = self.client.post("/register", json=user2)

        self.assertEqual(res1.status_code, 201)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(res2.get_json(), {"error": "Username already taken"})
        res1.close()
        res2.close()

    def test_login_is_case_insensitive_and_trimmed(self):
        credentials = {
            "username": "case-test",
            "email": "Case.Test@Example.com",
            "password": "secret-password",
        }
        self.client.post("/register", json=credentials)
        login_res = self.client.post(
            "/login",
            json={
                "email": "  case.test@example.com  ",
                "password": "secret-password",
            },
        )
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(login_res.get_json()["access_token"])
        login_res.close()


if __name__ == "__main__":
    unittest.main()
