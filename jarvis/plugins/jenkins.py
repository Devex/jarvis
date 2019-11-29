import re
import logging
from jinja2 import Template
from slackbot.bot import respond_to
from slackbot_settings import JENKINS_URL, JENKINS_USER, JENKINS_PASSWORD

import jarvis.plugins.jenkins_api as api


def smart_thread_reply(message, reply):
    message.reply(reply, in_thread=('thread_ts' in message.body))


logger = logging.getLogger(__name__)
server = api.connect(JENKINS_URL, JENKINS_USER, JENKINS_PASSWORD)
job_description_template = Template('''
This is what I know about `{{ job.name }}` ({{ job.url }}):
{{ job.description or "No description provided/available" }}
{% for param in job.params %}
> `{{ param.name }}`: {{ param.description }}
{% if param.defaultValue %}>   Defaults to `{{ param.defaultValue }}`. {% endif %}
{% if param.choices %}>   Possible choices are : {% for choice in param.choices %}
>     - `{{ choice }}` {% endfor %} {% endif %} {% endfor %}
''')


@respond_to('^list$', re.IGNORECASE)
def list(message):
    logger.debug('list command invoked')
    reply = "I found {} jobs:\n".format(len(server.jobs))
    for job in server.jobs:
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
    try:
        job_info = server.run(job_name, args)
        logger.debug('Jenkins replied: {}'.format(job_info))
    except api.UnknownJobError as e:
        job_info = str(e)
        smart_thread_reply(message, str(e))
    else:
        response += " ({})".format(job_info['url'])
        logger.debug(response)
        if response == '':
            message.react('ok_hand')
            smart_thread_reply(message, response)
        else:
            smart_thread_reply(message, response)
    finally:
        logger.debug('Jenkins replied: {}'.format(job_info))


@respond_to('describe ([^ ]*)', re.IGNORECASE)
def describe(message, job_name):
    logger.debug('describe command invoked: job={}'.format(job_name))
    try:
        job = server.jobs[job_name]
    except api.UnknownJobError as e:
        smart_thread_reply(message, str(e))
        return
    else:
        smart_thread_reply(message, job_description_template.render(job=job))
