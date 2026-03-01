FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SERVICE_LOG_DIR=/logs/
RUN apt-get update \
  && apt-get install --yes --no-install-recommends \
    build-essential \
    cmake \
    curl \
    git \
    postgresql-client \
  && apt-get autoremove \
  && rm -rf /var/lib/apt/lists/*
# RUN apt-get update; apt-get install -y gcc libc-dev git
RUN mkdir app
RUN mkdir app/resources
RUN mkdir app/tm
RUN mkdir config
RUN mkdir logs
RUN mkdir env
WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY /requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY /tm /app/tm
COPY /manage.py /app/manage.py
COPY /demo_ki.py /app/demo_ki.py
COPY /resources/deployment /app/resources/deployment
COPY /docker/app/config.yaml /config/config.yaml
COPY /resources/env/.env.tm.demo /env/.env.tm.demo
ENV KE_KI_CONFIG_PATH="/app/resources/deployment/ke_config.yaml"
ENV DB_INIT_SCRIPT_LOCATION="/app/resources/deployment/db/pg_init.sql"
ENV APP_LOGGING_CONF_PATH="/app/resources/deployment/logging.ini"
#ENV APP_USE_SCHEDULER=True
#ENV APP_USE_REST_API=True
#ENV APP_USE_KE_API=True
ENV SERVICE_LOG_DIR=/var/log/
EXPOSE 8080
CMD ["python", "manage.py","-c" ,"/config/config.yaml"  ]