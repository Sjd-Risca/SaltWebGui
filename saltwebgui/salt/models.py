# -*- coding: utf-8 -*-
"""Saltstack access interface abstraction.

Be keen to the usage of full_return"""
import json
import logging
import yaml
from flask import flash, g
from ..decorators import api_status

logger = logging.getLogger('pepper')

class JobProxy(object):
    """Jobs storage object"""
    def __init__(self):
        self._jobs_cache = dict()

    @api_status
    def get_job(self, jid=None):
        """Get the job from salt master and save locally.
        Expected result:
        {"data": {
             "_stamp": "2019-01-28T22:48:21.459847",
             "fun": "runner.jobs.lookup_jid",
             "fun_args": [{"jid": "20190128215534115075"}],
             "jid": "20190128234817170064",
             "return": {
                 "data": {MINION: {MINION: JOBS}},
                 "outputter": "highstate"},
             "success": true,
             "user": "salt"},
         "tag": "salt/run/20190128234817170064/ret"}
        """
        if not jid:
            raise ValueError('Jid parameter is missing')
        job = g.salt.runner('jobs.lookup_jid', jid=jid, missing=True, full_return=True)
        logger.debug("Found job id %s document as: %r", jid, job)
        self._jobs_cache[jid] = job
        return True

    def job_updated(self, jid):
        """Check if a job has already updated, if not try to update it"""
        if jid in self._jobs_cache.keys():
            return True
        return self.get_job(jid)

    def job_data(self, jid):
        """Return the data from the job"""
        return self._jobs_cache[jid]['data']['return']['data']

    def get_jid(self, jid):
        """Get the jid output.
        If the output is not already present and is not possible to retrive it, return False.
        """
        if self.job_updated(jid):
            return self.job_data(jid)
        flash('Error reading job "{0}"'.format(jid), 'warning')
        return False

    def indented_jid(self, jid):
        """Return a raw string of the job outputter, but with nice indentation.
        """
        if self.job_updated(jid):
            return json.dumps(self.job_data(jid), sort_keys=True, indent=2)
        flash('Error reading job "{0}"'.format(jid), 'warning')
        return False

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
        """Return, for the select jid, a list of the minions executed followed
        by the count of steps for each status between success, still, failed.
        If is not possible to retrieve the jid, return False.
        """
        _job = self.get_jid(jid)
        if not _job:
            return False
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
        _job = self.job_data(jid)
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


class JobsList(object):
    """Object for managing jobs execution index"""
    def __init__(self):
        self._jobs_data = None
        self.header = ('Function', 'Target', 'Target-type', 'User', \
            'StartTime', 'Arguments')

    def filtered_data(self):
        """Return only the jobs data filtered by header.
        Expected result:
            {JOB_ID: {"Function": xxx, "Target": xxx, "Target-type": xxx,
                      "User": xxx, "StartTime": xxx, "Arguments": xxx},
             ...
            }
        """
        return self._jobs_data['data'].get("return")

    @property
    def last_update(self):
        """Time of last update"""
        return self._jobs_data.get("_stamp")

    @property
    def jobs(self):
        """Return list of jobs"""
        if self._jobs_data is None:
            self.update()
        return self.filtered_data

    @api_status
    def update(self):
        """Update the jobs database.
        The runner payload expected is:
        {"return": [
            "tag": xxx,
            "data": {'fun_args': xxx,
                     'jid': xxx,
                     'return': HERE JOBS DATA},
            'success':True,
            '_stamp': '2019-01-28T22:59:07.699850', 'user':u'salt',
            'fun': 'runner.jobs.list_jobs'
            ]}
        """
        _jobs_list = g.salt.runner('jobs.list_jobs', full_return=True)
        logger.debug("Update of jobs list: %r", _jobs_list)
        self._jobs_data = _jobs_list['return'][0]
        return True

    def get_raw(self):
        """Return the raw list of jobs as from the returner"""
        return self._jobs_data

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

    @staticmethod
    @api_status
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
        raise ValueError("Unknown command option")

    @staticmethod
    def indented(data):
        """Return a raw and indented json text
        """
        return json.dumps(data, sort_keys=True, indent=2)

    @staticmethod
    def yaml(data):
        """Return text as yaml"""
        return yaml.safe_dump(data, default_flow_style=False, explicit_start=False)

    @staticmethod
    def raw(data):
        """Return text as raw"""
        return data

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

    @staticmethod
    @api_status
    def runner(tgt, func, arg=None, kwarg=None):
        """Interface to salt-api"""
        g.salt.local_async(tgt, func, arg, kwarg)
        return True

    def highstate(self, tgt, test=True):
        """Execute a state.apply"""
        if test:
            return self.runner(tgt, 'state.apply', kwarg={'test': True})
        return self.runner(tgt, 'state.apply')

    def cmd(self, tgt, func, arg=None, test=True):
        """Run command"""
        if test:
            return self.runner(tgt, func, arg, kwarg={'test': True})
        return self.runner(tgt, func, arg)


# Initiate object (maybe move outside later on)
JOBS = JobsList()
JOB = JobProxy()
KEYS = Keys()
MINIONS = Minions()
RUN = Run()
