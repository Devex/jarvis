import logging
import jenkins

from jarvis.jenkins.jobs import Jobs
from jarvis.jenkins.exceptions import UnknownJobError


logger = logging.getLogger(__name__)


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

    @classmethod
    def connect(self, url, user, password):
        return JenkinsAPI(jenkins.Jenkins(
            url,
            user,
            password,
        ))

    @property
    def server(self):
        return self._server.server

    @property
    def job_names(self):
        return [job['name'] for job in self.jobs]

    def run(self, job, args=None):
        if args is None:
            args = ''
        if job in self.job_names:
            self._server.build_job(job, args)
            return self._server.get_job_info(job)
        else:
            raise UnknownJobError(job)

    def describe(self, job):
        if job in self.job_names:
            return self._server.get_job_info(job)
        else:
            raise UnknownJobError(job)
