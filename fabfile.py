#!/usr/bin/env python
"""Utilities for project management"""
import os
import logging
from fabric.api import task, settings
from fabric.operations import local, run
from fabric.context_managers import prefix

log = logging.getLogger()  #pylint: disable=invalid-name

ROOT = os.path.dirname(os.path.realpath(__file__))
VENV = os.path.join(ROOT, "venv")

def virtualenv(command):
    """
    Runs the command in the virtuale environment
    """
    activate = os.path.join(VENV, "bin/activate")
    with prefix("source {}".format(activate)):
        result = local(command, shell="/bin/bash")
    return result

@task
def set_virtualenv():
    """venv setup"""
    action = local("virtualenv \"{}\"".format(VENV))
    if action.succeeded:
        log.info("Virtualenv is created in %s", VENV)
    else:
        print "Error creating virtualenv"
        exit(1)

@task
def install_pips():
    """Install dev pips"""
    res = virtualenv("pip install -r requirements.dev.txt")
    print res.stdout

@task
def checks_requirements():
    """Check system requirements"""
    required_dep_pkgs = ["libmariadbclient-dev", "python-dev", "libffi-dev", "gcc"]
    missing = list()
    with settings(warn_only=True):
        for pkg in required_dep_pkgs:
            exists = local("dpkg -l {}".format(pkg), capture=True)
            if exists.failed:
                missing.append(pkg)
    if len(missing) > 0:
        print "Missing packages: ", missing
        exit(1)
