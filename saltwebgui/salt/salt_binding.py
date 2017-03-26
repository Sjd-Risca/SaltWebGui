#!/usr/bin/env python2
"""
This code is legacy.
Now the SaltWebGui interface with saltstack througth salt-api via pepper, this code was use
in substitution of it to bind directly to salt, salt-key and salt-run shell commands.
"""
import ast
from prettytable import PrettyTable
from subprocess import Popen, PIPE
from debug import debug


class Jobs(object):                 # pylint: disable=too-few-public-methods
    """Manage saltstack jobs."""

    def __init__(self):
        """initialize default object"""
        self.sort_key = ['StartTime']
        self.jobs_list = dict()
        self.show = ['ID', 'Target', 'Function', 'Arguments', 'StartTime']

    def update_jobs_list(self):
        """Return jobs list"""
        run_update = Popen(['salt-run', 'jobs.list_jobs', '--out=raw'],
                           stdin=PIPE, stdout=PIPE, stderr=PIPE)
        raw_jobs, err = run_update.communicate() # pylint: disable=unused-variable
        jobs = ast.literal_eval(raw_jobs)
        self.jobs_list = jobs

    def jobs_sorted_by(self, key, reverse_order=True):
        """
        Return a list of jobs ID sorted by:
            - ID;
            - Function;
            - Target;
            - User
            - StartTime
            - Target-type
            - Arguments

        The sorting key needs to be a list [key1, key2...].

        Options:
         * reverse_order: do a reverse order (default: True)
        """
        indexed_by = list()
        allowed = ['ID', 'Function', 'Target', 'User', 'StartTime',
                   'Target-type', 'Arguments']
        for _key in key:
            if _key in allowed:
                indexed_by.append(_key)
        jobs_sorted = list()
        for job_id, value in self.jobs_list.iteritems():
            tmp = list()
            for key in indexed_by:
                if key == 'ID':
                    tmp.append(job_id)
                else:
                    tmp.append(value[key])
            tmp.append(job_id)
            jobs_sorted.append(tmp)
        jobs_sorted = sorted(jobs_sorted, reverse=reverse_order)
        index = list()
        for job in jobs_sorted:
            index.append(job[-1])
        return index

    def filtered(self, filters):
        """Filter the jobs list excluding the command provided as list"""
        if filters == None:
            return self.jobs_list
        jobs_filtered = dict()
        for job, value in self.jobs_list.iteritems():
            add = 0
            for _fil in filters:
                if value['Function'].startswith(_fil):
                    add += 1
            if add == 0:
                jobs_filtered[job] = value
        return jobs_filtered

    def easy_show(self):
        """Fancy list of jobs"""
        tab = PrettyTable(self.show)
        for job_id, value in self.jobs_list.iteritems():
            tmp = list()
            for key in self.show:
                if key == 'ID':
                    tmp.append(job_id)
                else:
                    tmp.append(value[key])
            tab.add_row(tmp)
        return tab

class Job(object):
    """Manage single job"""
    def __init__(self, job_id):
        """Start class"""
        self.job_id = job_id
        self.job = dict()
        self.get_job()
        self.minions = self.job.keys()
        self.show = ['__id__', 'result', 'comment', 'name', 'duration']

    def get_job(self):
        """Upload the job."""
        cmd = ['salt-run', 'jobs.lookup_jid', str(self.job_id), '--out=raw']
        get_output = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        raw_job, err = get_output.communicate() # pylint: disable=unused-variable
        self.job = ast.literal_eval(raw_job)
        debug(self.job)

    def successed(self, minion):
        """Return number of job's task that successed on minion."""
        return self.task_result_count(minion, True)

    def none(self, minion):
        """Return number of job's task that faild on minion."""
        return self.task_result_count(minion, None)

    def failed(self, minion):
        """Return number of job's task that faild on minion."""
        return self.task_result_count(minion, False)

    def task_result_count(self, minion, status):
        """Count how many task for minion are in the called status"""
        count = 0
        try:
            if not hasattr(self.job[minion], '__iter__'):
                return 0
            for task in self.job[minion]:
                if self.job[minion][task]['result'] is status:
                    count += 1
        except KeyError as err:
            print err
        except TypeError as err:
            # If the salt command has failed, then a list is returned.
            print err
        return count

    def list_all_job(self):
        """Print all jobs"""
        tab = PrettyTable(self.show)
        for minion, output in self.job.iteritems():
            tab.add_row(minion)
            for _id, value in output.iteritems(): #pylint: disable=unused-variable
                tmp = list()
                for key in self.show:
                    if key in value:
                        val = value[key]
                    else:
                        val = ''
                    tmp.append(val)
                tab.add_row(tmp)
        return tab

class RunJob(object):
    """Execute a saltstack command"""
    def __init__(self):
        """Init default options"""
        self.run = 'salt-run'
        self.call = 'salt'
        self.key = 'salt-key'

    def show_keys(self):
        """Retun the list of minions keys"""
        cmd = [self.key, '-L']
        get_output = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        raw_list, err = get_output.communicate() # pylint: disable=unused-variable
        return raw_list

    def call_function(self, target, function, options=False, async=True):
        """Execute salstack call to minions' target. It is possible to add some
        option to the command itself in the form of vector.
          > RunJob.call_function('state.highstate', ['test=True'])
        """
        cmd = [self.call, str(target), str(function)]
        if options is not False:
            cmd.extend(options)
        if async:
            cmd.append('--async')
        cmd.append('--state-output=full')
        debug(cmd)
        get_output = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        raw_list, err = get_output.communicate() # pylint: disable=unused-variable
        return raw_list, err

    def call_command(self, target, command, async=True):
        """Execute a saltstack call on a mionions' target. The object to be
        called has to be a vector like:
          > RunJob.call_command('*', ['cmd.run', 'whoami'])
        """
        cmd = [self.call, str(target)]
        cmd.extend(command)
        if async:
            cmd.append('--async')
        cmd.append('--state-output=full')
        debug(cmd)
        get_output = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        raw_list, err = get_output.communicate() # pylint: disable=unused-variable
        return raw_list, err

class ManageKeys(object):
    """Manage saltstack keys"""
    def __init__(self):
        """Init default options"""
        self.key = 'salt-key'

    def show_keys(self):
        """Retun the list of minions keys"""
        cmd = [self.key, '-L']
        get_output = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        raw_list, err = get_output.communicate() # pylint: disable=unused-variable
        keylist = [y for y in (x.strip() for x in raw_list.splitlines()) if y]
        return keylist

    def accept_key(self, keyname):
        """Accept the minion key"""
        pass
