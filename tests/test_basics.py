import unittest
from flask import current_app
from app import create_app, db
from app.models import get_user,User
from app.api.user_api import validate_user


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
    
    def test_login(self):
        tU = get_user("username","john")
        self.assertTrue(tU and validate_user(tU.username,"1234"))
        
        
        
