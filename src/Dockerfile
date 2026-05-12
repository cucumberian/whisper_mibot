FROM python:3.12-slim

ENV USER_HOME=/home/app/
ENV APP_HOME=${USER_HOME}/app/

RUN mkdir -p ${APP_HOME}

WORKDIR ${APP_HOME}

COPY requirements.freeze .

RUN pip install --no-cache-dir -r requirements.freeze

COPY . .

RUN groupadd --system app && \
    useradd --system --gid app --home-dir ${USER_HOME} app && \
    chown -R app:app ${USER_HOME}

USER app
