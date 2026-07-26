import os
import unittest
import json
from app import app, db
from database import DatabaseManager

TEST_DB = "test_web_password_manager.db"

class TestSecureVaultWebApp(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        
        # Point db manager to test database
        self.db = DatabaseManager(TEST_DB)
        app.config['TESTING'] = True
        self.client = app.test_client()

    def tearDown(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_status_endpoint(self):
        res = self.client.get('/api/status')
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIn('has_master_password', data)

    def test_setup_and_login_flow(self):
        # 1. First-time setup
        res_setup = self.client.post('/api/setup', json={"password": "WebVaultMasterPass123!"})
        self.assertEqual(res_setup.status_code, 200)

        # 2. Add credential (authenticated session)
        res_add = self.client.post('/api/credentials', json={
            "website": "GitHub",
            "username": "octocat",
            "password": "SuperSecretPassword1!",
            "category": "Work",
            "notes": "Dev account"
        })
        self.assertEqual(res_add.status_code, 200)

        # 3. Fetch credentials
        res_list = self.client.get('/api/credentials')
        data_list = json.loads(res_list.data)
        self.assertTrue(data_list['success'])
        self.assertEqual(len(data_list['data']), 1)
        self.assertEqual(data_list['data'][0]['website'], "GitHub")

    def test_password_generator_endpoint(self):
        res = self.client.post('/api/generate-password', json={
            "length": 24,
            "use_upper": True,
            "use_lower": True,
            "use_digits": True,
            "use_symbols": True
        })
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['password']), 24)

    def test_unauthorized_access_protection(self):
        # Clear session
        with self.client.session_transaction() as sess:
            sess.clear()

        res = self.client.get('/api/credentials')
        self.assertEqual(res.status_code, 401)


if __name__ == "__main__":
    unittest.main()
