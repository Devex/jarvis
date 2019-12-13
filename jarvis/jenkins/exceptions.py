class UnknownJobError(Exception):
    def __init__(self, job):
        self._job = job

    def __str__(self):
        return 'Unknown job `{}`'.format(self._job)


class ArgumentsFormatError(Exception):
    def __init__(self, args):
        self._args = args

    def __str__(self):
        return "Arguments provided (`{}`) aren't correctly formatted (`KEY=value [...]`)".format(self._args)


class ArgumentsRequiredError(Exception):
    def __init__(self, args):
        self._args = args

    def __str__(self):
        return "Job `{}` requires arguments (`KEY=value [...]`)".format(self._args)
