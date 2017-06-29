# -*- coding: utf-8 -*-
"""Placeholder for custom decorators"""

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user, logout_user
from pepper import PepperException


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def api_status(f):
    """Test is api is working, otherwise logout"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except PepperException as error:
            if error == 'Authentication denied':
                flash('Authentication timeout', 'warning')
            else:
                flash(error, 'warning')
            logout_user()
            return redirect(url_for('frontend.login'))
    return decorated_function
