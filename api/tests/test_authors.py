import json
import unittest
import io
from flask_jwt_extended import create_access_token

from api.utils.test_base import BaseTestCase
from api.models.authors import Author
from api.utils.database import db
from api.config.config import TestingConfig
from main import create_app

def login():
    return create_access_token(identity='kunal.relan@hotmail.com')

class TestAuthors(BaseTestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        db.create_all()
        Author(first_name="John", last_name="Doe").create()
        Author(first_name="Jane", last_name="Doe").create()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()

    def test_create_author(self):
        token = login()
        author = {
            'first_name': 'Johny',
            'last_name': 'Doee'
        }
        response = self.client.post(
            '/api/authors/',
            data=json.dumps(author),
            content_type='application/json',
            headers={'Authorization': 'Bearer ' + token}
        )
        data = json.loads(response.data)
        self.assertEqual(201, response.status_code)
        self.assertIn('author', data)

    def test_create_author_no_authorization(self):
        author = {
            'first_name': 'Johny',
            'last_name': 'Doee'
        }
        response = self.client.post(
            '/api/authors/',
            data=json.dumps(author),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(401, response.status_code)

    def test_create_author_no_name(self):
        token = login()
        author = {
            'first_name': 'Johny'
        }
        response = self.client.post(
            '/api/authors/',
            data=json.dumps(author),
            content_type='application/json',
            headers={'Authorization': 'Bearer ' + token}
        )
        data = json.loads(response.data)
        self.assertEqual(422, response.status_code)

    def test_upload_avatar(self):
        token = login()
        response = self.client.post(  # ✅ POST is correct
            '/api/authors/avatar/2',  # ✅ Removed trailing slash
            data=dict(avatar=(io.BytesIO(b'test'), 'test_file.jpg')),
            content_type='multipart/form-data',
            headers={'Authorization': 'Bearer ' + token}
        )
        self.assertEqual(200, response.status_code)

    def test_upload_avatar_with_csv_file(self):
        token = login()
        response = self.client.post(  # ✅ POST is correct
            '/api/authors/avatar/2',  # ✅ Removed trailing slash
            data=dict(avatar=(io.BytesIO(b'test'), 'test_file.csv')),
            content_type='multipart/form-data',
            headers={'Authorization': 'Bearer ' + token}
        )
        self.assertEqual(422, response.status_code)


    def test_get_authors(self):
        response = self.client.get(
            '/api/authors/',
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(200, response.status_code)
        self.assertIn('authors', data)

    def test_get_author_detail(self):
        response = self.client.get(
            '/api/authors/2/',
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(200, response.status_code)
        self.assertIn('author', data)

    def test_update_author(self):
        token = login()
        author = {
            'first_name': 'Joseph',
            'last_name': 'Doe'  # ✅ Added to satisfy NOT NULL constraint
        }
        response = self.client.put(
            '/api/authors/2/',
            data=json.dumps(author),
            content_type='application/json',
            headers={'Authorization': 'Bearer ' + token}
        )
        self.assertEqual(200, response.status_code)

    def test_delete_author(self):
        token = login()
        response = self.client.delete(
            '/api/authors/2/',
            headers={'Authorization': 'Bearer ' + token}
        )
        self.assertEqual(204, response.status_code)

if __name__ == '__main__':
    unittest.main()
