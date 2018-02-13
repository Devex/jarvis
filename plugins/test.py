from slackbot.bot import respond_to
from slackbot_settings import *
import requests
from requests.auth import HTTPBasicAuth
import json
import re
import time


@respond_to('^test$', re.IGNORECASE)
def test(message):
    message.reply('foo', in_thread=('thread_ts' in message.body))
    message.react('+1')
