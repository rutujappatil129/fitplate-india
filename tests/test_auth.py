import unittest
import sys
import os
import gc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import auth
import database

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.test_db = str(Path(__file__).resolve().parent / "test_auth.db")
        database.init_db(self.test_db)

    def tearDown(self):
        gc.collect()
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except OSError:
                pass

    def test_password_hashing_and_verification(self):
        pwd = "SecurePassword@123"
        h1, s1 = auth.hash_password(pwd)
        h2, s2 = auth.hash_password(pwd)
        # Salts must be unique
        self.assertNotEqual(s1, s2)
        self.assertNotEqual(h1, h2)
        # Verification succeeds
        self.assertTrue(auth.verify_password(pwd, h1, s1))
        self.assertTrue(auth.verify_password(pwd, h2, s2))
        # Wrong password fails
        self.assertFalse(auth.verify_password("WrongPassword", h1, s1))

    def test_validate_registration_inputs(self):
        # Valid input
        valid, _ = auth.validate_registration_inputs("aarav@example.com", "mypassword1", "mypassword1", "Aarav Sharma")
        self.assertTrue(valid)

        # Invalid email
        valid, err = auth.validate_registration_inputs("invalid-email", "mypassword1", "mypassword1", "Aarav")
        self.assertFalse(valid)
        self.assertIn("valid email", err)

        # Mismatched passwords (both >= 6 chars)
        valid, err = auth.validate_registration_inputs("aarav@example.com", "pass123", "pass456", "Aarav")
        self.assertFalse(valid)
        self.assertIn("do not match", err)

        # Short password
        valid, err = auth.validate_registration_inputs("aarav@example.com", "123", "123", "Aarav")
        self.assertFalse(valid)
        self.assertIn("at least 6 characters", err)

    def test_register_and_authenticate_flow(self):
        email = "priya@example.in"
        pwd = "StrongPassword99"
        name = "Priya Patel"

        ok, msg, uid = auth.register_user(email, pwd, pwd, name, db_path=self.test_db)
        self.assertTrue(ok)
        self.assertIsNotNone(uid)

        # Duplicate register fails
        ok_dup, msg_dup, _ = auth.register_user(email, pwd, pwd, name, db_path=self.test_db)
        self.assertFalse(ok_dup)
        self.assertIn("already exists", msg_dup)

        # Authenticate successfully
        auth_ok, _, user_data = auth.authenticate_user(email, pwd, db_path=self.test_db)
        self.assertTrue(auth_ok)
        self.assertEqual(user_data["email"], email)
        self.assertEqual(user_data["full_name"], name)

        # Bad password
        bad_auth, _, _ = auth.authenticate_user(email, "WrongPassword", db_path=self.test_db)
        self.assertFalse(bad_auth)

if __name__ == "__main__":
    unittest.main()
