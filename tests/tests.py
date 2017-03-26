# -*- coding: utf-8 -*-
"""Utility for testing the flask app"""
#pylint: disable=no-self-use,too-many-public-methods

import unittest
from flask_testing import TestCase

from saltwebgui import create_app
from saltwebgui.user import User
from saltwebgui.config import TestConfig
from saltwebgui.extensions import db


class BaseTestCase(TestCase):
    """Default test class, use this for setting the db and other basic
    structures"""

    def create_app(self):
        app = create_app(TestConfig)
        return app

    def init_data(self):
        """Set test parameters"""
        demo = User(name=u'demo',
                    email=u'demo@example.com',
                    password=u'123456')
        db.session.add(demo)
        db.session.commit()

    def setUp(self):
        """Reset all tables before testing."""

        db.create_all()
        self.init_data()
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean db session and drop all tables."""

        db.session.remove()
        db.drop_all()

    def login(self, username, password):
        """Login test"""
        data = {
            'login': username,
            'password': password,
        }
        response = self.client.post('/login', data=data, follow_redirects=True)
        assert "Logged in" in response.data
        return response

    def _logout(self):
        response = self.client.get('/logout')
        self.assertRedirects(response, location='/')

    def _test_get_request(self, endpoint, template=None):
        response = self.client.get(endpoint)
        self.assert_200(response)
        if template:
            self.assertTemplateUsed(name=template)
        return response

    def _test_get_redirect(self, endpoint, redirect_to):
        response = self.client.get(endpoint)
        self.assert_redirects(response, redirect_to)
        return response


class TestFrontend2(BaseTestCase):

    def test_index(self):
        self._test_get_request('/', 'index.html')
        self._test_get_request('/login', 'frontend/login.html')

        response = self.client.post('/login', data={
            'login': "demo@example.com",
            'password': "123456"}, follow_redirects=True)
        assert "Logged in" in response.data
        self._test_get_redirect('/', '/user/profile')
        self._logout()
        self._test_get_request('/', 'index.html')

    def test_login_page(self):
        self._test_get_request('/login', 'frontend/login.html')
        with self.client:
#            self.assertTrue(current_user.is_anonymous())
            response = self.client.post('/login', data={
                'login': "demo@example.com",
                'password': "123456"}, follow_redirects=True)
            assert "Logged in" in response.data
#            self.assertTrue(current_user.is_anonymous())
            self._test_get_redirect('/login', '/user/profile')
            self._logout()
            self._test_get_request('/login', 'frontend/login.html')
            response = self.client.post('/login', data={
                'login': "error@example.com",
                'password': "123456"}, follow_redirects=True)
            assert "Sorry, invalid login" in response.data

    def test_signup(self):
        self._test_get_request('/signup', 'frontend/signup.html')

        data = {
            'email': 'new_user@example.com',
            'password': '123456',
            'name': 'new_user',
            'agree': True,
        }
        response = self.client.post('/signup', data=data, follow_redirects=True)
        assert "Signed up" in response.data
        new_user = User.query.filter_by(email=data['email']).first()
        assert new_user.name == "new_user"

    def test_login(self):
        self._test_get_request('/login', 'frontend/login.html')

        response = self.client.post('/login', data={
            'login': "demo@example.com",
            'password': "123456"}, follow_redirects=True)
        assert "Logged in" in response.data
        self._test_get_redirect('/', '/user/profile')
        self._logout()
        self._test_get_request('/', 'index.html')

    def test_logout(self):
        self.login("demo@example.com", "123456")
        self._logout()


if __name__ == '__main__':
    unittest.main()
