
ARG REGISTRY_DOMAIN
ARG REGISTRY_PROJECT
ARG IMAGE_TAG
FROM ${REGISTRY_DOMAIN}/${REGISTRY_PROJECT}/tm-entsoe-service:$IMAGE_TAG

COPY /docker/entsoe-demo/entsoe.yaml /app/resources/deployment/entsoe.yaml
#COPY /docker/entsoe-demo/entsoe.yaml /app/resources/deployment/entsoe2.yml

ENV KE_KI_CONFIG_PATH="/app/resources/deployment/ke_config.yaml"
ENV DB_INIT_SCRIPT_LOCATION="/app/resources/deployment/db/pg_init.sql"
ENV APP_LOGGING_CONF_PATH="/app/resources/deployment/logging.ini"
ENV SERVICE_LOG_DIR=/var/log/
EXPOSE 8080
CMD ["python", "manage.py","-c" ,"/config/config.yaml"  ]