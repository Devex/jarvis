FROM python:3.6-alpine

# build with:
# docker build -t jarvis:$(git tag --sort v:refname | tail -1) .
ENV APP_HOME /opt/jarvis

WORKDIR ${APP_HOME}

COPY Pipfile Pipfile.lock ${APP_HOME}/
RUN pip install --no-cache-dir pipenv && \
    pipenv install

COPY . ${APP_HOME}/

CMD [ "pipenv", "run", "python", "run.py" ]