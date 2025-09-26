import unittest
import tempfile
import os

from main import create_app
from api.utils.database import db
from api.config.config import TestingConfig

class BaseTestCase(unittest.TestCase):
    """A base test case"""

    def setUp(self):
        self.test_db_file = tempfile.mkstemp()[1]
        TestingConfig.SQLALCHEMY_DATABASE_URI = 'sqlite:///' + self.test_db_file
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        os.remove(self.test_db_file)
