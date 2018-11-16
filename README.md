# Devex Jarvis

Jarvis is a replacement bot for Marvin, built using Python's slackbot, which helps build commands faster.

Jarvis is currently ready to be used as a container.

### Build

Newer versions must be tagged in git repository, and pushed/PR'd to the repository:

```
git tag -a X.X.X
git push
```

In order to build it, use the following command in the root of the repository:

```
docker build -t jarvis:$(git tag --sort v:refname | tail -1) .
```

### Environment variables

Jarvis uses the following environment variables:

- `SLACKBOT_API_TOKEN`: Slack token for the account to use here
- `SLACKBOT_ERRORS_DEST`: Slack account to what send all errors
- `JENKINS_URL`: URL where Jenkins is reachable
- `JENKINS_USER`: User to use when talking to Jenkins
- `JENKINS_PASSWORD`:  Password for the corresponding Jenkins user

### Running locally

To have Jarvis running locally, use the following command:

```
docker run --rm \
       --env JENKINS_PASSWORD=${JENKINS_PASSWORD} \
       --env JENKINS_URL=${JENKINS_URL} \
       --env JENKINS_USER=${JENKINS_USER} \
       --env SLACKBOT_API_TOKEN=${SLACKBOT_API_TOKEN} \
       --env SLACKBOT_ERRORS_DEST=${SLACKBOT_ERRORS_DEST} \
       jarvis:$(git tag --sort v:refname | tail -1)
```

### Publishing new version

Once the new version is ready for deploy, publish the container:

```
aws ecr get-login --no-include-email | bash
docker tag \
       jarvis:$(git tag --sort v:refname | tail -1) \
       406396564037.dkr.ecr.us-east-1.amazonaws.com/jarvis:$(git tag --sort v:refname | tail -1)
docker tag \
       jarvis:$(git tag --sort v:refname | tail -1) \
       406396564037.dkr.ecr.us-east-1.amazonaws.com/jarvis:latest
docker push 406396564037.dkr.ecr.us-east-1.amazonaws.com/jarvis:$(git tag --sort v:refname | tail -1)
docker push 406396564037.dkr.ecr.us-east-1.amazonaws.com/jarvis:latest
```

### Running in K8s cluster

With the `JENKINS_PASSWORD` and the `SLACKBOT_API_TOKEN` exported, use the following commands:

```
kubectl apply -f manifests/jarvis-ns.yaml
kubectl create secret generic jarvis-secrets \
        --from-literal=jenkins_password=${JENKINS_PASSWORD} \
        --from-literal=slack_token=${SLACKBOT_API_TOKEN} \
        -n jarvis
kubectl apply -f manifests/jarvis-deploy.yaml
```
