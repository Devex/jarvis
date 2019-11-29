from collections.abc import MutableMapping
import logging

from jarvis.jenkins.job import Job


logger = logging.getLogger(__name__)


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
