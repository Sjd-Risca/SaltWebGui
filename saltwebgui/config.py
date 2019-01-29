# -*- coding: utf-8 -*-
"""Basic configurations module"""
import os
from .utils import INSTANCE_FOLDER_PATH
#pylint: disable=too-few-public-methods

class BaseConfig(object):
    """Base configuration"""

    PROJECT = "SaltWebGui"
    #Salt-api connection parameters
    SALT_URI = "http://127.0.0.1:8000"

    # Get app root path, also can use flask.root_path.
    # ../../config.py
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    DEBUG = False
    TESTING = False

    # http://flask.pocoo.org/docs/quickstart/#sessions
    SECRET_KEY = 'secret key'

    LOG_FOLDER = os.path.join(INSTANCE_FOLDER_PATH, 'logs')


class DefaultConfig(BaseConfig):
    """Production base configuration"""
    LOG_LEVEL = 'warn'


class DebugConfig(BaseConfig):
    """Configuration for live debugging mode"""
    DEBUG = True


class TestConfig(BaseConfig):
    """Configuration for testing purpose (unittest)"""
    TESTING = True
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False

class SaltWebGui(BaseConfig):
    pass
