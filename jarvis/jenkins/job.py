from collections.abc import MutableMapping
import logging

from jarvis.jenkins.exceptions import ArgumentsFormatError


logger = logging.getLogger(__name__)


def parse_args(args):
    args = args.strip()
    try:
        params = {key: value for key, value in [
            param.split('=') for param in args.split()]}
    except ValueError:
        raise ArgumentsFormatError(args)
    return params


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

    def run(self, args):
        self._server.build_job(self._job['name'], parse_args(args))
        return self._server.get_job_info(self._job['name'])

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
