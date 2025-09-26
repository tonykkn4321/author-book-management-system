import json
import unittest
from datetime import datetime

from api.utils.test_base import BaseTestCase
from api.models.users import User, db
from api.utils.token import generate_verification_token, confirm_verification_token
from main import create_app
from api.config.config import TestingConfig

def create_users():
    # Clear existing users to avoid duplicates
    db.session.query(User).delete()
    db.session.commit()

    user1 = User(
        email="tonykkn717@gmail.com",
        username='kunalrelan12',
        password=User.generate_hash('helloworld'),
        isVerified=True
    )
    user2 = User(
        email="tonykkn24133@gmail.com",
        username='kunalrelan125',
        password=User.generate_hash('helloworld')
    )
    db.session.add_all([user1, user2])
    db.session.commit()

class TestUsers(BaseTestCase):
    def setUp(self):
        # Initialize app and context
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        # Create tables and seed users
        db.create_all()
        create_users()

    def tearDown(self):
        # Clean up database and context
        db.session.remove()
        db.engine.dispose()  # ✅ Correct way to close SQLite file handles
        db.drop_all()
        self.app_context.pop()

    def test_login_user(self):
        user = {
            "email": "tonykkn717@gmail.com",
            "password": "helloworld"
        }
        response = self.client.post(
            '/api/users/login',
            data=json.dumps(user),
            content_type='application/json'
        )
        data = json.loads(response.data)

        # ✅ Expect 200 OK for login
        self.assertEqual(200, response.status_code)
        self.assertIn('access_token', data)

if __name__ == '__main__':
    unittest.main()
