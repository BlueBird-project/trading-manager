
ARG REGISTRY_DOMAIN
ARG REGISTRY_PROJECT
ARG IMAGE_TAG
FROM ${REGISTRY_DOMAIN}/${REGISTRY_PROJECT}/trading-manager:$IMAGE_TAG

#ENV KE_KI_CONFIG_PATH="/app/resources/deployment/ke_config.yaml"
#ENV DB_INIT_SCRIPT_LOCATION="/app/resources/deployment/db/pg_init.sql"
#ENV APP_LOGGING_CONF_PATH="/app/resources/deployment/logging.ini"
ENV SERVICE_LOG_DIR=/var/log/
#RUN mkdir /app/examples
COPY /docker/dt-service/examples /app/examples
COPY /docker/dt-service/examples/dt_ki.py /app/dt_ki.py
COPY /docker/dt-service/resources/deployment/ki/dt_sample.yaml /app/resources/deployment/ki/dt_sample.yaml
EXPOSE 8080
CMD ["python", "dt_ki.py","-c" ,"/config/config.yaml"    ]