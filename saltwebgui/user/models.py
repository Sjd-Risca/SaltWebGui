# -*- coding: utf-8 -*-
"""Basic user model"""

import urllib2
import pepper
from flask_login import UserMixin
from flask import flash, current_app

USER = dict()

class User(UserMixin):
    """Extreamly symple user model.
    """

    def __init__(self, username, auth=None):
        """Create a new user attributes:
         - username: user for login
         - auth: salt-api token
         """
        self.username = username
        self.auth = auth

    def __repr__(self):
        return self.username

    def get_id(self):
        return self.username

    @classmethod
    def authenticate(cls, login, password):
        """Performe the authentication against salt-api"""
        salt = pepper.Pepper(current_app.config['SALT_URI'])
        auth = None
        try:
            auth = salt.login(login, password, 'pam')
            authenticated = True
        except urllib2.URLError:
            flash('Error connecting to salt master', 'warning')
            authenticated = False
        except pepper.libpepper.PepperException as err:
            flash(err, 'warning')
            authenticated = False
        user = cls(login, auth)
        if authenticated:
            USER.setdefault(user.username, user)
        return user, authenticated

