from slackbot.bot import respond_to
from slackbot_settings import *
import requests
from requests.auth import HTTPBasicAuth
import json
import re
import time


class Jenkins():
    def __init__(self, url=None, username=None, password=None):
        if url is None:
            self.url = JENKINS_URL
        else:
            self.url = url
        if username is None:
            self.username = JENKINS_USER
        else:
            self.username = username
        if password is None:
            self.password = JENKINS_PASSWORD
        else:
            self.password = password
        response = requests.get(self._build_api_url(
        ), auth=HTTPBasicAuth(self.username, self.password))
        self.data = json.loads(response.text)
        self.job_count = len(self.data['jobs'])

    def job_list(self):
        return [job['name'] for job in self.data['jobs']]

    def _build_api_url(self, path=None):
        if path is None:
            path = "{}/".format(self.url)
        return "{}{}".format(path, 'api/json')

    def _build_crumbIssuer_url(self):
        crumbIssuer_url = "{}/crumbIssuer/".format(self.url)
        return "{}".format(self._build_api_url(crumbIssuer_url))

    def _get_crumb(self):
        response = requests.get(self._build_crumbIssuer_url(
        ), auth=HTTPBasicAuth(self.username, self.password))
        crumb_data = json.loads(response.text)
        return crumb_data['crumbRequestField'], crumb_data['crumb']

    def _get_job_data(self, job_name):
        for job in self.data['jobs']:
            if job['name'] == job_name:
                return job

    def _build_build_url(self, job_name):
        job = self._get_job_data(job_name)
        return "{}build".format(job['url'])

    def _build_buildWithParams_url(self, job_name):
        job = self._get_job_data(job_name)
        return "{}buildWithParameters".format(job['url'])

    def _task_started(self, task_data):
        if "executable" in task_data:
            if task_data["executable"] is dict and "url" in task_data["executable"]:
                return True
        return False

    def build(self, job_name, job_params=None):
        if job_params is None or job_params == {}:
            build_method = self._build_build_url
        else:
            build_method = self._build_buildWithParams_url
        auth = HTTPBasicAuth(self.username, self.password)
        crumb_data = self._get_crumb()
        # , 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        headers = {crumb_data[0]: crumb_data[1]}
        url = build_method(job_name)
        response = requests.post(
            url, auth=auth, headers=headers, data=job_params)
        if response.status_code == 201:
            job_id = response.headers['Location'].split('/')[-2]
            queue_url = self._build_api_url(response.headers['Location'])
            response2 = requests.post(queue_url, auth=auth, headers=headers)
            queued_task = json.loads(response2.text)
            max_retries = 5
            retries = 1
            while not queued_task["buildable"] and \
                    retries < max_retries:
                time.sleep(2 ^ retries - 1)
                response2 = requests.post(
                    queue_url, auth=auth, headers=headers)
                try:
                    queued_task = json.loads(response2.text)
                except json.decoder.JSONDecodeError:
                    pass
                retries += 1
            retries = 1
            while queued_task["buildable"] and \
                "pending" in queued_task and not queued_task["pending"] and \
                    retries < max_retries:
                time.sleep(2 ^ retries - 1)
                response2 = requests.post(
                    queue_url, auth=auth, headers=headers)
                queued_task = json.loads(response2.text)
                retries += 1
            if queued_task is not None and \
                "executable" in queued_task and \
                queued_task["executable"] is not None and \
                    "url" in queued_task["executable"]:
                return queued_task["executable"]["url"]
            else:
                return "Task was accepted, check on Jenkins UI for execution {}".format(response.headers['Location'])
        else:
            return "Error queueing task, probably wrong arguments ({})".format(response.status_code)


def smart_thread_reply(message, reply):
    message.reply(reply, in_thread=('thread_ts' in message.body))


@respond_to('^list$', re.IGNORECASE)
def list(message):
    J = Jenkins()
    reply = "I found {} jobs:\n".format(J.job_count)
    for job in J.job_list():
        reply += "{}\n".format(job)
    smart_thread_reply(message, reply)


@respond_to('build ([^ ]*)(.*)', re.IGNORECASE)
def build(message, job, args):
    J = Jenkins()
    try:
        params = {key: value for (key, value) in [
            param.split('=') for param in args.split()]}
    except ValueError:
        smart_thread_reply(
            message, "Parameter passing is incorrect. Parameter should be KEY=value")
        return
    if job in J.job_list():
        reply = J.build(job, params)
        if reply == '':
            message.react('ok_hand')
            smart_thread_reply(message, reply)
        else:
            smart_thread_reply(message, reply)
    else:
        smart_thread_reply(message, "Unknown job")


if __name__ == "__main__":
    try:
        input = raw_input
    except NameError:
        pass
    J = Jenkins()
    help_message = "You can use help, list, build, or quit"
    command = input("> ")
    while command != "quit":
        if command == "help":
            print(help_message)
        elif command == "list":
            for job in J.job_list():
                print(job)
        elif command.startswith("build"):
            command_parts = command.split()
            job, args = command_parts[1], command_parts[2:]
            params = {key: value for (key, value) in [param.split('=') for param in args]}
            result = J.build(job, params)
            print(result)
        command=input("> ")
    print("Quitting test mode")
