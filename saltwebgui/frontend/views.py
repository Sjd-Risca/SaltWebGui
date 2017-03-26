# -*- coding: utf-8 -*-
"""Manage frontend page and login page"""
from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, login_user, logout_user
from ..user import User
from .forms import LoginForm


frontend = Blueprint('frontend', __name__) #pylint: disable=invalid-name

@frontend.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@frontend.route('/login', methods=['GET', 'POST'])
def login():
    """Page for user login"""
    form = LoginForm(login=request.args.get('login', None),
                     next=request.args.get('next', None))

    if form.validate_on_submit():
        user, authenticated = User.authenticate(form.login.data,
                                                form.password.data)
        if user and authenticated:
            remember = request.form.get('remember') == 'y'
            if login_user(user, remember=remember):
                flash("Logged in", 'success')
            return redirect(form.next.data or url_for('salt.main_window'))
        else:
            flash('Sorry, invalid login', 'danger')

    return render_template('frontend/login.html', form=form)


@frontend.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('Logged out', 'success')
    return redirect(url_for('frontend.index'))
