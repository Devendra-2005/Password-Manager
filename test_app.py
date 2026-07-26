import os
import unittest
import sqlite3
from auth import generate_salt, hash_password, verify_password, evaluate_password_strength
from database import DatabaseManager
from password_generator import generate_password

TEST_DB_NAME = "test_password_manager.db"

class TestSecureVaultBackend(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_DB_NAME):
            os.remove(TEST_DB_NAME)
        self.db = DatabaseManager(TEST_DB_NAME)

    def tearDown(self):
        if os.path.exists(TEST_DB_NAME):
            os.remove(TEST_DB_NAME)

    def test_auth_hashing(self):
        pwd = "MySecretMasterPassword123!"
        salt = generate_salt()
        pwd_hash = hash_password(pwd, salt)

        self.assertTrue(verify_password(pwd, pwd_hash, salt))
        self.assertFalse(verify_password("WrongPassword", pwd_hash, salt))

    def test_master_password_flow(self):
        self.assertFalse(self.db.has_master_password())
        
        # Set master password
        self.db.set_master_password("VaultMaster2026!")
        self.assertTrue(self.db.has_master_password())

        # Verify master password
        self.assertTrue(self.db.verify_master_password("VaultMaster2026!"))
        self.assertFalse(self.db.verify_master_password("WrongVaultMaster"))

    def test_credential_crud(self):
        # 1. Add Credential
        success, msg = self.db.add_credential("Google", "user@gmail.com", "SecretPass1!", "Work", "Primary email account")
        self.assertTrue(success)

        # 2. Duplicate Detection
        dup_success, dup_msg = self.db.add_credential("google", "USER@GMAIL.COM", "AnotherPass", "Other", "")
        self.assertFalse(dup_success)
        self.assertIn("already exists", dup_msg)

        # 3. Search Credential
        results = self.db.search_credentials("google")
        self.assertEqual(len(results), 1)
        cred_id = results[0]["id"]
        self.assertEqual(results[0]["website"], "Google")
        self.assertEqual(results[0]["category"], "Work")

        # 4. Update Credential
        upd_success, upd_msg = self.db.update_credential(cred_id, "Google Workspace", "user@gmail.com", "NewSecretPass123!", "Work", "Updated notes")
        self.assertTrue(upd_success)

        updated_row = self.db.get_credential_by_id(cred_id)
        self.assertEqual(updated_row["website"], "Google Workspace")
        self.assertEqual(updated_row["password"], "NewSecretPass123!")

        # 5. Delete Credential
        del_success = self.db.delete_credential(cred_id)
        self.assertTrue(del_success)

        self.assertEqual(len(self.db.search_credentials("Google")), 0)

    def test_password_generator(self):
        pwd = generate_password(length=20, use_upper=True, use_lower=True, use_digits=True, use_symbols=True)
        self.assertEqual(len(pwd), 20)
        self.assertTrue(any(c.isupper() for c in pwd))
        self.assertTrue(any(c.islower() for c in pwd))
        self.assertTrue(any(c.isdigit() for c in pwd))

    def test_password_strength_evaluator(self):
        score_weak, label_weak, _ = evaluate_password_strength("123")
        self.assertEqual(label_weak, "Weak")

        score_strong, label_strong, _ = evaluate_password_strength("SuperS3cur3P@ssw0rd2026!")
        self.assertIn(label_strong, ["Strong", "Very Strong"])


if __name__ == "__main__":
    unittest.main()
