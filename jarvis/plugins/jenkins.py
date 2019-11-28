import re
import logging
from slackbot.bot import respond_to
from slackbot_settings import JENKINS_URL, JENKINS_USER, JENKINS_PASSWORD

from jarvis.plugins.jenkins_api import connect


def smart_thread_reply(message, reply):
    message.reply(reply, in_thread=('thread_ts' in message.body))


logger = logging.getLogger(__name__)
api = connect(JENKINS_URL, JENKINS_USER, JENKINS_PASSWORD)


@respond_to('^list$', re.IGNORECASE)
def list(message):
    logger.debug('list command invoked')
    reply = "I found {} jobs:\n".format(len(api.jobs))
    for job in api.jobs:
        reply += "{}\n".format(job['name'])
    smart_thread_reply(message, reply)


@respond_to('build ([^ ]*)(.*)', re.IGNORECASE)
def build(message, job_name, args):
    logger.debug('build command invoked: job={}, args={}'.format(
        job_name,
        args,
    ))
    try:
        {key: value for (key, value) in [
            param.split('=') for param in args.split()]}
    except ValueError:
        logger.error('Parameters in build are wrong: {}'.format(args))
        smart_thread_reply(
            message, "Parameter passing is incorrect. Parameter should be `KEY=value`")
        return
    response = "Building {}".format(job_name)
    if args != '':
        response += " with parameters {}".format(args.strip())
    else:
        response += " without parameters"
    job_info = api.run(job_name, args)
    logger.debug('Jenkins replied: {}'.format(job_info))
    response += " ({})".format(job_info['url'])
    logger.debug(response)
    if response == '':
        message.react('ok_hand')
        smart_thread_reply(message, response)
    else:
        smart_thread_reply(message, response)
