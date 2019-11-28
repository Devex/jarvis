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


class JenkinsAPI(object):
    def __init__(self, jenkins):
        logger.info('Initializing Jenkins API')
        self._server = jenkins
        self.user = self._server.get_whoami()
        self.version = self._server.get_version()
        self._jobs = None
        logger.info('I am {} at {} (v.{})'.format(
            self.user['fullName'], self._server.server, self.version))

    @property
    def server(self):
        return self._server.server

    @property
    def jobs(self):
        if self._jobs is None:
            self._jobs = self._server.get_jobs()
        return self._jobs

    @property
    def job_names(self):
        return [job['name'] for job in self.jobs]

    def run(self, job, parameters=None):
        if job in self.job_names:
            args = parse_args(parameters)
            self._server.build_job(job, args)
            return self._server.get_job_info(job)
        else:
            raise Exception("Unknown job: {}".format(job))
