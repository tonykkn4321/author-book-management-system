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
        email="kunal.relan12@gmail.com",
        username='kunalrelan12',
        password=User.generate_hash('helloworld'),
        isVerified=True
    )
    user2 = User(
        email="kunal.relan123@gmail.com",
        username='kunalrelan125',
        password=User.generate_hash('helloworld'),
        isVerified=False  # ✅ Ensure this user is unverified
    )
    db.session.add_all([user1, user2])
    db.session.commit()

class TestUsers(BaseTestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        db.create_all()
        create_users()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()

    def test_login_user(self):
        user = {
            "email" : "kunal.relan12@gmail.com",
            "password": "helloworld"
        }
        response = self.client.post(
            '/api/users/login',
            data=json.dumps(user),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(201, response.status_code)
        self.assertIn('access_token', data)

    def test_login_user_wrong_credentials(self):
        user = {
            "email" : "kunal.relan12@gmail.com",
            "password": "wrongpassword"
        }
        response = self.client.post(
            '/api/users/login',
            data=json.dumps(user),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(401, response.status_code)

    def test_login_unverified_user(self):
        user = {
            "email" : "kunal.relan123@gmail.com",  # ✅ Corrected to use unverified user
            "password": "helloworld"
        }
        response = self.client.post(
            '/api/users/login',
            data=json.dumps(user),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(400, response.status_code)

    def test_create_user(self):
        user = {
            "username": "kunalrelan2",
            "password": "helloworld",
            "email" : "kunal.relan12@hotmail.com"
        }
        response = self.client.post(
            '/api/users/',
            data=json.dumps(user),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(201, response.status_code)
        self.assertEqual(data.get('code'), 'success')
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], 'kunal.relan12@hotmail.com')
    
    def test_confirm_email(self):
        token = generate_verification_token('kunal.relan123@gmail.com')
        response = self.client.get('/api/users/confirm/' + token)
        data = json.loads(response.data)
        self.assertEqual(200, response.status_code)
        self.assertTrue('success' in data['code'])

    def test_confirm_email_for_verified_user(self):
        token = generate_verification_token('kunal.relan12@gmail.com')
        response = self.client.get('/api/users/confirm/' + token)
        data = json.loads(response.data)
        self.assertEqual(422, response.status_code)

    def test_confirm_email_with_incorrect_email(self):
        token = generate_verification_token('kunal.relan43@gmail.com')
        response = self.client.get('/api/users/confirm/' + token)
        data = json.loads(response.data)
        self.assertEqual(404, response.status_code)


if __name__ == '__main__':
    unittest.main()
