from collections.abc import MutableMapping
import logging
import jenkins


logger = logging.getLogger(__name__)


def connect(url, user, password):
    return JenkinsAPI(jenkins.Jenkins(
        url,
        user,
        password,
    ))


def parse_args(parameters):
    return {key: value for key, value in [
        param.split('=') for param in parameters.split()]}


def parse_params(job_info):
    params = []
    param_defs_properties = [item for item in job_info.get(
        'property', []) if 'parameterDefinitions' in item]
    param_defs = param_defs_properties[0] if param_defs_properties else {}
    for param_def in param_defs.get('parameterDefinitions', []):
        defaultValue = param_def['defaultParameterValue']['value']
        if param_def['type'] == 'BooleanParameterDefinition':
            defaultValue = str(param_def['defaultParameterValue']['value'])
        if defaultValue is None:
            defaultValue = ''
        param = {
            'name': param_def['name'].strip(),
            'type': param_def['type'].strip(),
            'description': param_def['description'].strip(),
            'defaultValue': defaultValue.strip(),
        }
        if 'choices' in param_def:
            param['choices'] = param_def['choices']
        params.append(param)
    return params


class Job(MutableMapping):
    def __init__(self, job, server):
        self._server = server
        self._job = {}
        logger.debug('Loading job {} ({})'.format(job['name'], job['_class']))
        for k in job:
            self._job[k] = job[k]
        job_info = self._server.get_job_info(job['name'])
        self._job['fullDisplayName'] = job_info['fullDisplayName']
        self._job['description'] = job_info['description']
        self.params = parse_params(job_info)

    def __getitem__(self, key):
        return self._job[key]

    def __setitem__(self, key, value):
        self._job[key] = value

    def __delitem__(self, key):
        del self._job[key]

    def __len__(self):
        return len(self._job)

    def __iter__(self):
        return iter(self._job)

    def clear(self):
        self._job = {}

    def pop(self, key, default=None):
        return self._job.pop(key, default)

    def popitem(self):
        return self._job.popitem()

    def setdefault(self, key, default=None):
        self._job.setdefault(key, default)

    def update(self, other):
        self._job.update(other)


class Jobs(MutableMapping):
    def __init__(self, server):
        self._server = server
        self._jobs = {}
        self._update()

    def __getitem__(self, key):
        return self._jobs[key]

    def __setitem__(self, key, value):
        self._jobs[key] = value

    def __delitem__(self, key):
        del self._jobs[key]

    def __len__(self):
        return len(self._jobs)

    def __iter__(self):
        return iter(self._jobs.values())

    def _update(self):
        jobs = self._server.get_jobs()
        self._jobs.clear()
        for j in jobs:
            self._jobs[j['name']] = Job(j, self._server)

    def clear(self):
        self._jobs = {}

    def pop(self, key, default=None):
        return self._jobs.pop(key, default)

    def popitem(self):
        return self._jobs.popitem()

    def setdefault(self, key, default=None):
        self._jobs.setdefault(key, default)

    def update(self, other):
        self._jobs.update(other)


class UnknownJobError(Exception):
    def __init__(self, job):
        self._job = job

    def __str__(self):
        return 'Unknown job {}'.format(self._job)


class JenkinsAPI(object):
    def __init__(self, jenkins):
        logger.info('Initializing Jenkins API')
        self._server = jenkins
        self.user = self._server.get_whoami()
        self.version = self._server.get_version()
        logger.info('I am {} at {} (v.{})'.format(
            self.user['fullName'], self._server.server, self.version))
        logger.info('Initializing jobs')
        self.jobs = Jobs(self._server)
        logger.info('{} jobs loaded'.format(len(self.jobs)))

    @property
    def server(self):
        return self._server.server

    @property
    def job_names(self):
        return [job['name'] for job in self.jobs]

    def run(self, job, parameters=None):
        if job in self.job_names:
            args = parse_args(parameters)
            self._server.build_job(job, args)
            return self._server.get_job_info(job)
        else:
            raise UnknownJobError(job)

    def describe(self, job):
        if job in self.job_names:
            return self._server.get_job_info(job)
        else:
            raise UnknownJobError(job)
