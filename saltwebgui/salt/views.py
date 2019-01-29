# -*- coding: utf-8 -*-
"""Saltstack web GUI, for easy jobs administration.
"""
import shlex
from flask import Blueprint, render_template, redirect, flash, url_for, \
    request
from flask_login import login_required
from . import form, models
from .debug import debug

salt = Blueprint('salt', __name__, url_prefix='/salt') #pylint: disable=invalid-name

# TO BE MOVED to configuration of Blueprint
DEBUG = 2

@salt.route('/')
@login_required
def main_window():
    """Landing page (/salt)"""
    return render_template('salt/base.html')

@salt.route('/jobs/<action>')
@login_required
def jobs(action='list'):
    """Administrator for jobs."""
    if action == 'update':
        models.JOBS.update()
    _jobs = models.JOBS.jobs
    header = models.JOBS.header
    return render_template('salt/jobs_list.html', jobs=_jobs, header=header)

@salt.route('/job//<action>')
@salt.route('/job/<jid>/<action>')
@login_required
def job(jid=None, action='list'):
    """Single job administration.

    The following actions are supported:

    - update: update the job data from saltstack
    - list: list the job's returner in a fancy way
    - raw: show raw (textual) data from the returner
    - full: list the job's returner into a pretty table
    """
    if jid and action == 'update':
        if models.JOB.get_job(jid):
            flash('Updated job id n. {}'.format(jid), 'success')
        else:
            flash('Error trying to update job id n. {}'.format(jid), 'warning')
        return redirect(url_for('salt.job', jid=jid, action='list'))
    elif jid and action == 'list':
        _job = models.JOB.get_jid(jid)
        #if has minions
        minion_status = models.JOB.minion_status(jid)
        debug(minion_status)
        return render_template('salt/job_result.html',
                               jid=jid,
                               minions=minion_status,
                               job=_job)
    elif jid and action == 'raw':
        _job = models.JOB.indented_jid(jid)
        return render_template('salt/job_result_raw.html', job=_job, jid=jid)
    elif jid and action == 'full':
        head, body = models.JOB.full_jid_table(jid)
        return render_template('salt/job_result_table.html', body=body,
                               head=head, jid=jid)
    else:
        domain = request.url_root
        func = 'salt/job/&lt;jid&gt;/&lt;action&gt;'
        return 'Usage: {}{}'.format(domain, func)

@salt.route('/keys/<action>/')
@salt.route('/keys/<action>/<key>')
@login_required
def keys(action='list', key=None):
    """Manage minions' keys"""
    if action == 'list':
        models.KEYS.list_keys()
        return render_template('salt/keys.html', keys=models.KEYS.keys)
    elif action == 'accept' and key:
        return 'TO BE IMPLEMENTED'
    domain = request.url_root
    func = 'salt/key/&lt;jid&gt;/&lt;action&gt;'
    return 'Usage: {}{}'.format(domain, func)

@salt.route('/minions/<action>/')
@salt.route('/minions/<action>/<minion>')
@login_required
def minions(action='list', minion=None):
    """Administrator for jobs."""
    if action == 'list':
        models.KEYS.list_keys()
        _minions = sorted(models.KEYS.keys.get('accepted', list()))
        return render_template('salt/minions_list.html', minions=_minions)
    if minion is None:
        flash('Please first select a minion from the Minion list', 'warning')
        return redirect(url_for('salt.minions', action='list'))
    outformat = request.args.get('outformat', 'yaml')
    if action in ['pillars', 'tops', 'grains'] and outformat in ['raw', 'yaml']:
        data = models.MINIONS.get_data(minion, action, outformat)
    else:
        domain = request.url_root
        func = 'minions/&lt;action&gt;'
        return 'Usage: {}{}'.format(domain, func)
    return render_template('salt/minions_pillars.html',
                           action=action,
                           minion=minion,
                           data=data,
                           outformat=outformat)

@salt.route('/run', methods=['GET', 'POST'])
@login_required
def run():
    """Run commands"""
    form_highstate = form.FormHighstate(prefix='form_highstate',
                                        test=True)
    form_salt = form.FormSalt(prefix='form_salt')

    if form_highstate.validate_on_submit() and form_highstate.submit.data: #pylint: disable=no-member
        target = form_highstate.target.data
        test = form_highstate.test_mode.data
        if test == 'True':
            test = True
        elif test == 'False':
            test = False
        models.RUN.highstate(target, test)
        flash('Running the command: salt state.apply test={}'.format(test),
              'success')
        return redirect(url_for('salt.run'))
    elif form_salt.validate_on_submit() and form_salt.submit.data:
        target = form_salt.target.data
        command = form_salt.command.data
        test = form_salt.test_mode.data
        if test == 'True':
            test = True
        elif test == 'False':
            test = False
        user_cmd = '{} {} {} test={}'.format('salt', target, command, test)
        cmd = shlex.split(command)
        models.RUN.cmd(target, cmd[0], cmd[1:], test)
        flash('Running the command: {}'.format(user_cmd), 'success')
        return redirect(url_for('salt.run'))

    return render_template('salt/cmd.html',
                           FormSalt=form_salt,
                           FormHighstate=form_highstate)
