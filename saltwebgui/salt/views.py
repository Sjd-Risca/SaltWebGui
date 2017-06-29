# -*- coding: utf-8 -*-
"""Saltstack web GUI, for easy jobs administration.
"""
import json
import shlex
import yaml
from flask import Blueprint, render_template, redirect, flash, url_for, g, \
    request
from flask_login import login_required
from . import form
from .debug import debug
from saltwebgui.decorators import api_status

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
        JOBS.update()
    _jobs = JOBS.jobs
    header = JOBS.header
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
        if JOB.update(jid):
            flash('Updated job id n. {}'.format(jid), 'success')
        else:
            flash('Error trying to update job id n. {}'.format(jid), 'warning')
        return redirect(url_for('salt.job', jid=jid, action='list'))
    elif jid and action == 'list':
        _job = JOB.get_jid(jid)
        #if has minions
        minion_status = JOB.minion_status(jid)
        debug(minion_status)
        return render_template('salt/job_result.html',
                               jid=jid,
                               minions=minion_status,
                               job=_job)
    elif jid and action == 'raw':
        _job = JOB.indented_jid(jid)
        return render_template('salt/job_result_raw.html', job=_job, jid=jid)
    elif jid and action == 'full':
        head, body = JOB.full_jid_table(jid)
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
        KEYS.list_keys()
        return render_template('salt/keys.html', keys=KEYS.keys)
    elif action == 'accept' and key:
        return 'TO BE IMPLEMENTED'
    else:
        domain = request.url_root
        func = 'salt/key/&lt;jid&gt;/&lt;action&gt;'
        return 'Usage: {}{}'.format(domain, func)

@salt.route('/minions/<action>/')
@salt.route('/minions/<action>/<minion>')
@login_required
def minions(action='list', minion=None):
    """Administrator for jobs."""
    if action == 'list':
        KEYS.list_keys()
        _minions = sorted(KEYS.keys.get('accepted', list()))
        return render_template('salt/minions_list.html', minions=_minions)
    if minion is None:
        flash('Please first select a minion from the Minion list', 'warning')
        return redirect(url_for('salt.minions', action='list'))
    outformat = request.args.get('outformat', 'yaml')
    if action in ['pillars', 'tops', 'grains'] and outformat in ['raw', 'yaml']:
        data = MINIONS.get_data(minion, action, outformat)
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
        RUN.highstate(target, test)
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
        RUN.cmd(target, cmd[0], cmd[1:], test)
        flash('Running the command: {}'.format(user_cmd), 'success')
        return redirect(url_for('salt.run'))

    return render_template('salt/cmd.html',
                           FormSalt=form_salt,
                           FormHighstate=form_highstate)


class Job(object):
    """Job administrator"""
    def __init__(self):
        self.jobs = dict()

    @api_status
    def update(self, jid=None):
        """Return the job by ID"""
        if jid:
            _job = g.salt.runner('jobs.lookup_jid', jid=jid)
            self.jobs[jid] = _job['return'][0] #pylint: disable=redefined-outer-name,invalid-name,unused-variable
            return True
        else:
            raise ValueError('job parameter is missing')

    def job_updated(self, jid):
        """Check if a job has already updated, if not try to update it"""
        if jid in self.jobs:
            return True
        else:
            return self.update(jid)

    def get_jid(self, jid):
        """Return the jid"""
        self.job_updated(jid)
        return self.jobs[jid]

    def indented_jid(self, jid):
        """Return a raw string of the job outputter, but with nice indentation.
        """
        self.job_updated(jid)
        return json.dumps(self.jobs[jid], sort_keys=True, indent=2)

    @staticmethod
    def task_result_count(returner, minion, status):
        """Count how many task for minion are in the called status"""
        count = 0
        try:
            if not hasattr(returner[minion], '__iter__'):
                return 0
            for task in returner[minion]:
                if returner[minion][task]['result'] is status:
                    count += 1
        except KeyError as err:
            print err
        except TypeError as err:
            # If the salt command has failed, then a list is returned.
            print err
        return count

    def minion_returner_state(self, returner, minion):
        """Return a tuple of the output states"""
        return self.task_result_count(returner, minion, True), \
               self.task_result_count(returner, minion, None), \
               self.task_result_count(returner, minion, False)

    def minion_status(self, jid):
        """Return a list of minion followed by their execution status"""
        self.job_updated(jid)
        _job = self.jobs[jid]
        _minion = dict()
        for minion in _job:
            #to be rewritten with task_result_count
            _minion[minion] = self.minion_returner_state(_job, minion)
        return _minion

    def full_jid_table(self, jid):
        """Return a table.

        Every line will be a state returner, every column a key value"""
        cols = set()
        #header = list()
        body = list()
        self.job_updated(jid)
        _job = self.jobs[jid]
        for minion in _job:
            for work in _job[minion]:
                for param in _job[minion][work]:
                    cols.add(param)
        for minion in _job:
            for work in _job[minion]:
                row = dict()
                row['minion'] = minion
                row['id'] = work
                for key in cols:
                    row[key.lower()] = _job[minion][work].get(key)
                body.append(row)
        cols.add('minion')
        cols.add('ID')
        return cols, body


class Jobs(object):
    """Object for jobs administration"""
    def __init__(self):
        self.jobs = None
        self.header = ('Function', 'Target', 'Target-type', 'User', \
            'StartTime', 'Arguments')

    @api_status
    def update(self):
        """Update the jobs database"""
        _jobs = g.salt.runner('jobs.list_jobs')
        self.jobs = _jobs['return'][0]
        return True

    def get_raw(self):
        """Return the raw list of jobs as from the returner"""
        return self.jobs

class Keys(object):
    """Key administration"""
    def __init__(self):
        self.keys = None

    @api_status
    def list_keys(self):
        """Return a list of all available keys in the format
        {'accepted': [1,2,3],
         'denied': [4,5,6],
         'pre': [7,8],
         'rejected': [9,10]}
        """
        _ret = g.salt.low([{'client': 'wheel', 'fun': 'key.list_all'}])
        _minions = _ret['return'][0]['data']['return']
        _keys = dict()
        _keys['accepted'] = _minions['minions']
        _keys['denied'] = _minions['minions_denied']
        _keys['pre'] = _minions['minions_pre']
        _keys['rejected'] = _minions['minions_rejected']
        self.keys = _keys

    def accept(self, key):
        """Accept the given key"""
        pass
        #_ret = g.salt.low([{'client': 'wheel', 'fun': 'key.list_all'}])
        #print _jobs
    def remove(self, key):
        """Accept the given key"""
        pass
    def reject(self, key):
        """Accept the given key"""
        pass

class Minions(object):
    """Minions' data administrator"""
    def __init__(self):
        self.pillars = dict()
        self.tops = dict()
        self.grains = dict()

    @api_status
    @staticmethod
    def runner(tgt, func, arg=None, kwarg=None):
        """Interface to salt-api"""
        return g.salt.local(tgt, func, arg, kwarg)

    def update(self, minion=None, resource='pillars'):
        """Update the specified resource"""
        commands = {'pillars': 'pillar.items', 'tops': 'state.show_top', 'grains': 'grains.items'}
        if minion is None:
            return False
        if resource in commands:
            data = self.runner(minion, commands[resource])
            cleandata = data.get('return', list())[0].get(minion, dict())
            _db = getattr(self, resource)
            _db[minion] = cleandata
            return True

    @staticmethod
    def indented(data):
        """Return a raw and indented json text
        """
        return json.dumps(data, sort_keys=True, indent=2)

    @staticmethod
    def yaml(data):
        """Return text as yaml"""
        return yaml.safe_dump(data, default_flow_style=False, explicit_start=False)

    def get_data(self, minion, resource, outformat):
        """Easy link for calling back the requested data.

        Input:
          - minion: minion name
          - resource: pillars, tops or grains
          - outformat: yaml or raw (its a pretty json)
        """
        if not (resource in ['pillars', 'tops', 'grains'] and outformat in ['raw', 'yaml']):
            return 'Wrong or missing parameters'
        self.update(minion, resource)
        data = getattr(self, resource)
        _filter = getattr(self, outformat)
        return _filter(data[minion])


class Run(object):
    """command execution"""
    def __init__(self):
        pass

    @api_status
    @staticmethod
    def runner(tgt, func, arg=None, kwarg=None):
        """Interface to salt-api"""
        g.salt.local_async(tgt, func, arg, kwarg)
        return True

    def highstate(self, tgt, test=True):
        """Execute a state.apply"""
        if test:
            return self.runner(tgt, 'state.apply', kwarg={'test': True})
        else:
            return self.runner(tgt, 'state.apply')

    def cmd(self, tgt, func, arg=None, test=True):
        """Run command"""
        if test:
            return self.runner(tgt, func, arg, kwarg={'test': True})
        else:
            return self.runner(tgt, func, arg)


# Initiate object (maybe move outside later on)
JOBS = Jobs()
JOB = Job()
KEYS = Keys()
MINIONS = Minions()
RUN = Run()

