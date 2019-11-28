import os

DEBUG = os.environ.get('DEBUG', False)
API_TOKEN = os.environ['SLACKBOT_API_TOKEN'] or ''
DEFAULT_REPLY = "I don't understand this reference, sir."
ERRORS_TO = os.environ.get('SLACKBOT_ERRORS_DEST', None)
PLUGINS = [
    'jarvis.plugins',
]
JENKINS_URL = os.environ['JENKINS_URL'] or None
JENKINS_USER = os.environ['JENKINS_USER'] or None
JENKINS_PASSWORD = os.environ['JENKINS_PASSWORD'] or None
