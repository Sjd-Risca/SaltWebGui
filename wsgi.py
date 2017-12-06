#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Wsgi script for running SaltWebGui.
Is possible to use this script from cli as well with a Python Web Server Gateway Interface (WSGI)
HTTP server like uwsgi, gunicon, apache mod_swgi.

Usage:
    FLASK_APP=./wsgi.py flask run

This way is possible to use flask cli commands and pass other options, like:
    FLASK_APP=./wsgi.py FLASK_DEBUG=1 flask run --port 50001

For running in a custom virtualenv use the environment variable VIRTUALENV, otherwise this
script will  search in the path "[../][v]env"
"""
import sys
import os

project = "saltwebgui"
if os.environ.get('VIRTUALENV', False):
    VENV_PATH = os.environ('VIRTUALENV')
else:
    VENV_PATH = ['venv', 'env', '../venv', '../env']

BASE_DIR = os.path.join(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

def virtualenv():
    """Activate the virtualenv"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    for path in VENV_PATH:
        if os.path.isdir(os.path.join(dir_path, path)):
            activate_this = os.path.join(dir_path, path, "bin/activate_this.py")
    execfile(activate_this, dict(__file__=activate_this))

virtualenv()
from saltwebgui import create_app #pylint: disable=wrong-import-position
application = create_app()


@application.cli.command()
def cov():
    """Runs the unit tests with coverage."""
    print 'Please run the script ./get_coverage.py'

@application.cli.command()
def test():
    """Runs the unit tests."""
    print 'please run python -m unittest discover'
