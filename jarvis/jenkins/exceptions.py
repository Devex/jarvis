class UnknownJobError(Exception):
    def __init__(self, job):
        self._job = job

    def __str__(self):
        return 'Unknown job {}'.format(self._job)
