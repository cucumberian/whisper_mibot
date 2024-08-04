FROM python:3.12-alpine3.20

ENV USER_HOME=/home/app/
ENV APP_HOME=${USER_HOME}/app/

RUN mkdir -p ${APP_HOME}

WORKDIR ${APP_HOME}

COPY requirements.freeze .

RUN pip install --no-cache-dir -r requirements.freeze

COPY . .

RUN addgroup --system app
RUN adduser -S -G app app
RUN chown -R app:app ${USER_HOME}
USER app