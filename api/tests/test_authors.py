import json
import unittest
import io
from flask_jwt_extended import create_access_token

from api.utils.test_base import BaseTestCase
from api.models.authors import Author
from api.models.books import Book
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
        self.seed_authors_and_books()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()

    def seed_authors_and_books(self):
        self.author1 = Author(first_name="John", last_name="Doe").create()
        Book(title="Test Book 1", year=1976, author_id=self.author1.id).create()
        Book(title="Test Book 2", year=1992, author_id=self.author1.id).create()

        self.author2 = Author(first_name="Jane", last_name="Doe").create()
        Book(title="Test Book 3", year=1986, author_id=self.author2.id).create()
        Book(title="Test Book 4", year=1992, author_id=self.author2.id).create()

    # ---------- Author Tests ----------

    def test_create_author(self):
        token = login()
        author = {'first_name': 'Johny', 'last_name': 'Doee'}
        response = self.client.post(
            '/api/authors/',
            data=json.dumps(author),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        data = json.loads(response.data)
        self.assertEqual(201, response.status_code)
        self.assertIn('author', data)

    def test_create_author_no_authorization(self):
        author = {'first_name': 'Johny', 'last_name': 'Doee'}
        response = self.client.post(
            '/api/authors/',
            data=json.dumps(author),
            content_type='application/json'
        )
        self.assertEqual(401, response.status_code)

    def test_create_author_no_name(self):
        token = login()
        author = {'first_name': 'Johny'}
        response = self.client.post(
            '/api/authors/',
            data=json.dumps(author),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(422, response.status_code)

    def test_upload_avatar(self):
        token = login()
        response = self.client.post(
            f'/api/authors/avatar/{self.author2.id}/',
            data=dict(avatar=(io.BytesIO(b'test'), 'test_file.jpg')),
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(200, response.status_code)

    def test_upload_avatar_with_csv_file(self):
        token = login()
        response = self.client.post(
            f'/api/authors/avatar/{self.author2.id}/',
            data=dict(avatar=(io.BytesIO(b'test'), 'test_file.csv')),
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(422, response.status_code)

    def test_get_authors(self):
        response = self.client.get('/api/authors/')
        data = json.loads(response.data)
        self.assertEqual(200, response.status_code)
        self.assertIn('authors', data)

    def test_get_author_detail(self):
        response = self.client.get(f'/api/authors/{self.author2.id}/')
        data = json.loads(response.data)
        self.assertEqual(200, response.status_code)
        self.assertIn('author', data)

    def test_update_author(self):
        token = login()
        author = {'first_name': 'Joseph', 'last_name': 'Doe'}
        response = self.client.put(
            f'/api/authors/{self.author2.id}/',
            data=json.dumps(author),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(200, response.status_code)

    def test_delete_author(self):
        token = login()
        response = self.client.delete(
            f'/api/authors/{self.author2.id}/',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(204, response.status_code)

    # ---------- Book Tests ----------

    def test_create_book(self):
        token = login()
        book = {
            'title': 'Alice in Wonderland',
            'year': 1982,
            'author_id': self.author2.id
        }
        response = self.client.post(
            '/api/books/',
            data=json.dumps(book),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        data = json.loads(response.data)
        self.assertEqual(201, response.status_code)
        self.assertIn('book', data)

    def test_create_book_no_author(self):
        token = login()
        book = {'title': 'Alice in Wonderland', 'year': 1982}
        response = self.client.post(
            '/api/books/',
            data=json.dumps(book),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(422, response.status_code)

    def test_create_book_no_authorization(self):
        book = {
            'title': 'Alice in Wonderland',
            'year': 1982,
            'author_id': self.author2.id
        }
        response = self.client.post(
            '/api/books/',
            data=json.dumps(book),
            content_type='application/json'
        )
        self.assertEqual(401, response.status_code)

    def test_get_books(self):
        response = self.client.get('/api/books/')
        data = json.loads(response.data)
        self.assertEqual(200, response.status_code)
        self.assertIn('books', data)

    def test_get_book_details(self):
        book = Book(title='Alice', year=1982, author_id=self.author2.id).create()
        response = self.client.get(f'/api/books/{book.id}/')
        data = json.loads(response.data)
        self.assertEqual(200, response.status_code)
        self.assertIn('book', data)

    def test_update_book(self):
        token = login()
        book = Book(title='Alice', year=1982, author_id=self.author2.id).create()
        update_data = {'title': 'Alice Updated', 'year': 1992}
        response = self.client.put(
            f'/api/books/{book.id}/',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(200, response.status_code)

    def test_delete_book(self):
        token = login()
        book = Book(title='Alice', year=1982, author_id=self.author2.id).create()
        response = self.client.delete(
            f'/api/books/{book.id}/',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(204, response.status_code)

if __name__ == '__main__':
    unittest.main()
