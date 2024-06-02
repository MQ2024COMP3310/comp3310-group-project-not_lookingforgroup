# "borrowed" from week10

import unittest
from flask import current_app
from project import create_app, db
from initialise_db import populate_db
from project.models import User,Photo,Comment,Category
from werkzeug.security import check_password_hash


class TestWebApp(unittest.TestCase):
    # Setup the page with the restaurantmenu database
    def setUp(self):
        self.app = create_app()
        self.app.config['WTF_CSRF_ENABLED'] = False  # no CSRF during tests
        self.appctx = self.app.app_context()
        self.appctx.push()
        db.create_all()
        populate_db()
        self.client = self.app.test_client()

    # Drop all database after the test file ran
    def tearDown(self):
        db.drop_all()
        self.appctx.pop()
        self.app = None
        self.appctx = None
        self.client = None

    def test_app(self):
        assert self.app is not None
        assert current_app == self.app

    def test_homepage_redirect(self):
        response = self.client.get('/', follow_redirects = True)
        assert response.status_code == 200

    def test_registration_form(self):
        response = self.client.get('/signup')
        assert response.status_code == 200

    def test_register_user(self):
        response = self.client.post('/signup', data = {
            'email' : 'user@test.com',
            'name' : 'test user',
            'password' : 'test123'
        }, follow_redirects = True)
        assert response.status_code == 200
        # should redirect to the login page
        assert response.request.path == '/login'

        # verify that user can now login
        response = self.client.post('/login', data = {
            'email' : 'user@test.com',
            'password' : 'test123'
        }, follow_redirects = True)
        assert response.status_code == 200
        html = response.get_data(as_text = True)
        # TODO should the user name be displayed?
        # assert 'test user' in html

    def test_hashed_passwords(self):
        response = self.client.post('/signup', data = {
            'email' : 'user@test.com',
            'name' : 'test user',
            'password' : 'test123'
        }, follow_redirects = True)
        assert response.status_code == 200
        # should redirect to the login page
        assert response.request.path == '/login'

        user = User.query.filter_by(email='user@test.com').first()
        assert user is not None
        assert check_password_hash(user.password, 'test123')


    def test_sql_injection(self):
        response = self.client.post('/signup', data = {
            'email' : 'user@test.com"; drop table user; -- ',
            'name' : 'test user',
            'password' : 'test123'
        }, follow_redirects = True)
        assert response.status_code == 200
        response = self.client.get('/', follow_redirects = True)
        assert response.status_code == 200




    # TODO test commenting
    # Get the login user and the commented photo
    def test_commenting_XSS_attack(self):
        response = self.client.post('/signup', data = {
            'email' : 'fakefake@fake.com',
            'name'  : 'fake',
            'password': 'fakefake'
        }, follow_redirects = True)
        assert response.status_code == 200
        # account created

        # TODO login
        response = self.client.post('/login', data = {
            'email' : 'fakefake@fake.com',
            'password': 'fakefake'
        }, follow_redirects = True)
        assert response.status_code == 200

        user = User.query.filter_by(name='fake').first()
        photo = Photo.query.filter_by(id='1').first()
        # Attempt to leave comment
        response = self.client.post('/photo/1/comment/', data = {
            'text' : '<script>alert("hello");</script>'
        }, follow_redirects = True)
        assert response.status_code == 200
        # should redirect back to the view comment page
        assert response.request.path == '/photo/1/comment/all'
        # 

    # TODO test of the admin powerers
    def test_admin(self):
        response = self.client.post('/login', data = {
            'email' : 'not@fake.com',
            'password': 'notbad'
        }, follow_redirects = True)
        assert response.status_code == 200