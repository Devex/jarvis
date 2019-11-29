import re
import logging
from jinja2 import Template
from slackbot.bot import respond_to
from slackbot_settings import JENKINS_URL, JENKINS_USER, JENKINS_PASSWORD

from jarvis.jenkins import JenkinsAPI as api
from jarvis.jenkins.exceptions import UnknownJobError


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
build_template = Template(
    'Building `{{ build.name }}` with parameters `{{ args }}` ({{ build.url }})')


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
        job = server.jobs[job_name]
        build = job.run(args)
    except UnknownJobError as e:
        smart_thread_reply(message, str(e))
        return
    else:
        smart_thread_reply(
            message, build_template.render(build=build, args=args.strip()))


@respond_to('describe ([^ ]*)', re.IGNORECASE)
def describe(message, job_name):
    logger.debug('describe command invoked: job={}'.format(job_name))
    try:
        job = server.jobs[job_name]
    except UnknownJobError as e:
        smart_thread_reply(message, str(e))
        return
    else:
        smart_thread_reply(message, job_description_template.render(job=job))
