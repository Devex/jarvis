# Devex Jarvis

Jarvis is a replacement bot for Marvin, built using Python's slackbot, which helps build commands faster.

Jarvis is currently ready to be used as a container.

### Environment variables

Jarvis uses the following environment variables:

- `SLACKBOT_API_TOKEN`: Slack token for the account to use here
- `SLACKBOT_ERRORS_DEST`: Slack account to what send all errors
- `JENKINS_URL`: URL where Jenkins is reachable
- `JENKINS_USER`: User to use when talking to Jenkins
- `JENKINS_PASSWORD`:  Password for the corresponding Jenkins user

### Build

In order to build it, use the following command in the root of the repository:

```
docker build -t jarvis .
```

### Running locally

To have Jarvis running locally, use the following command:

```
docker run --rm \
       --env JENKINS_PASSWORD=${JENKINS_PASSWORD} \
       --env JENKINS_URL=${JENKINS_URL} \
       --env JENKINS_USER=${JENKINS_USER} \
       --env SLACKBOT_API_TOKEN=${SLACKBOT_API_TOKEN} \
       --env SLACKBOT_ERRORS_DEST=${SLACKBOT_ERRORS_DEST} \
       jarvis
```

### Publishing new version

Once the new version is ready for deploy, publish the container:

```
aws ecr get-login --no-include-email | bash
REPO=406396564037.dkr.ecr.us-east-1.amazonaws.com/jarvis
TAG=$(git rev-parse HEAD)
docker build -t ${REPO}:${TAG} .
docker push ${REPO}:${TAG}
```

### Deploying

With the `JENKINS_PASSWORD` and the `SLACKBOT_API_TOKEN` exported, use the following commands:

```
kubectl apply -f manifests/jarvis-ns.yaml
kubectl create secret generic jarvis-secrets \
        --from-literal=jenkins_password=${JENKINS_PASSWORD} \
        --from-literal=slack_token=${SLACKBOT_API_TOKEN} \
        -n jarvis
sed -e "s/@@IMAGE@@/${REPO}:${TAG}/" manifests/jarvis-deploy.yaml | kubectl apply -f -
```
