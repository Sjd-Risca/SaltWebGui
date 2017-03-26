# -*- coding: utf-8 -*-
"""Forms for login"""
from flask_wtf import Form
from wtforms import HiddenField, BooleanField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

from ..constants import USERNAME_LEN_MIN, USERNAME_LEN_MAX, \
                    PASSWORD_LEN_MIN, PASSWORD_LEN_MAX


class LoginForm(Form):
    """A basic login form"""
    next = HiddenField()
    login = StringField('Username or email',
                        [DataRequired(),
                         Length(USERNAME_LEN_MIN, USERNAME_LEN_MAX)])
    password = PasswordField('Password',
                             [DataRequired(),
                              Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    remember = BooleanField('Remember me')
    # Use render_kw to set style of submit button
    submit = SubmitField('Sign in',
                         render_kw={"class": "btn btn-success btn-block"})
