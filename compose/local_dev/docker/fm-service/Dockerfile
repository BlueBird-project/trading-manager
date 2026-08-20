
ARG REGISTRY_DOMAIN
ARG REGISTRY_PROJECT
ARG IMAGE_TAG
FROM ${REGISTRY_DOMAIN}/${REGISTRY_PROJECT}/trading-manager:$IMAGE_TAG


ENV SERVICE_LOG_DIR=/var/log/
#RUN mkdir /app/examples
COPY /docker/fm-service/examples /app/examples
COPY /docker/fm-service/examples/fm_ki.py /app/fm_ki.py
COPY /docker/dt-service/examples/config.yaml /app/config/config.yaml
#COPY /docker/dt-service/resources/deployment/ki/fm_sample.yaml /app/resources/deployment/ki/fm_sample.yaml
#COPY /docker/dt-service/resources/deployment/ki/fm.yaml /app/resources/deployment/ki/fm.yaml
#COPY /docker/dt-service/resources/deployment/ki/dam.yaml /app/resources/deployment/ki/dam.yaml
EXPOSE 8080
WORKDIR /app
CMD ["python", "fm_ki.py" ,"-c" ,"/config/config.yaml"    ]