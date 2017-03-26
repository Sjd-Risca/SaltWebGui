# -*- coding: utf-8 -*-
"""Istance for creating the app"""

import pepper
from flask import Flask, render_template, g

from .config import DefaultConfig
from .user import USER

from .extensions import login_manager
from .filters import pretty_date, nl2br
from .utils import INSTANCE_FOLDER_PATH

from flask_login import current_user


# For import *
__all__ = ['create_app']


def create_app(config=None, app_name=None):
    """Create a Flask app."""

    if app_name is None:
        app_name = DefaultConfig.PROJECT

    app = Flask(app_name,
                instance_path=INSTANCE_FOLDER_PATH,
                instance_relative_config=True)
    configure_app(app, config)
    configure_hook(app)
    configure_blueprints(app)
    configure_extensions(app)
    configure_logging(app)
    configure_template_filters(app)
    configure_error_handlers(app)
    configure_cli(app)

    return app


def configure_app(app, config=None):
    """Parameters can be passed by loading the app with a custom set of parameters, like::
      create_app('test')
    Or with custom environment variables::
      SECRET_KEY_APP_CONFIG='random' flask run
    And of course from file located in /etc/saltwebgui/config.py.
    """
    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(DefaultConfig)
    if config:
        app.config.from_object(config)
    # http://flask.pocoo.org/docs/config/#instance-folders
    app.config.from_pyfile('/etc/saltwebgui/config.py', silent=True)
    # Use instance folder instead of env variables to make deployment easier.
    app.config.from_envvar('%s_APP_CONFIG' % DefaultConfig.PROJECT.upper(),
                           silent=True)


def configure_extensions(app):
    """Setup extensions"""

    # flask-login
    login_manager.login_view = 'frontend.login'

    @login_manager.user_loader
    def load_user(_id): #pylint: disable=unused-variable
        """This function will call back the current user for login_manager"""
        if _id in USER:
            return USER[_id]
        return None
    login_manager.setup_app(app)


def configure_blueprints(app):
    """Configure blueprints in views."""

    from saltwebgui.frontend import frontend
    from saltwebgui.salt import salt

    for _bp in [frontend, salt]:
        app.register_blueprint(_bp)


def configure_template_filters(app):
    """Configure custom jinja filters."""

    app.jinja_env.filters["pretty_date"] = pretty_date
    app.jinja_env.filters["nl2br"] = nl2br


def configure_logging(app):
    """Configure file(info) and email(error) logging."""

    if app.debug or app.testing:
        # Skip loggin setup for debug and test mode: just check standard output.
        return

    import logging
    import os
    from logging.handlers import SMTPHandler
    # logs' level: [DEBUG, INFO, WARN, ERROR]
    # Set info level on logger, which might be overwritten by handers.
    # Suppress DEBUG messages.
    app.logger.setLevel(logging.INFO)

    if os.path.isdir(app.config['LOG_FOLDER']):
        info_log_path = os.path.join(app.config['LOG_FOLDER'], 'info.log')
        info_file_handler = logging.handlers.RotatingFileHandler(info_log_path,
                                                                 maxBytes=100000,
                                                                 backupCount=10)
        info_file_handler.setLevel(logging.INFO)
        info_file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        app.logger.addHandler(info_file_handler)
    else:
        print '{} is missing! Please create it.'.format(os.path.isdir(app.config['LOG_FOLDER']))

    #mail_handler = SMTPHandler(app.config['MAIL_SERVER'],
    #                           app.config['MAIL_USERNAME'],
    #                           app.config['ADMINS'],
    #                           'Your Application Failed!',
    #                           (app.config['MAIL_USERNAME'],
    #                            app.config['MAIL_PASSWORD']))
    #mail_handler.setLevel(logging.ERROR)
    #mail_handler.setFormatter(logging.Formatter(
    #    '%(asctime)s %(levelname)s: %(message)s '
    #    '[in %(pathname)s:%(lineno)d]'))
    #app.logger.addHandler(mail_handler)


def configure_hook(app):
    """Application hook"""

    def salt_api(app):
        """Init the salt-api connector"""
        g.user = current_user
        if g.user.is_anonymous:
            g.salt = None
        elif g.user.auth:
            g.salt = pepper.Pepper(app.config['SALT_URI'])
            g.salt.auth = g.user.auth
        else:
            g.salt = None

    @app.before_request
    def before_request(): #pylint: disable=unused-variable
        """Action to perform before request"""
        salt_api(app)


def configure_error_handlers(app):
    """For info: http://flask.pocoo.org/docs/latest/errorhandling/"""

    @app.errorhandler(404)
    def page_not_found(error):  #pylint: disable=unused-argument,unused-variable
        """Redirect for error 404"""
        return render_template("errors/404.html"), 404


def configure_cli(app):  #pylint: disable=unused-argument
    """Add here cli command for Flask"""
    pass

# Example
#    @app.cli.command()
#    def initdb():
#        db.drop_all()
#        db.create_all()
