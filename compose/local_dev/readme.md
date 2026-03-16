## Services

### ENTSO-E

#### Configure

This service requires API TOKEN (
ENTSOE_TOKEN) - [acquire token](https://www.amsleser.no/blog/post/21-obtaining-api-token-from-entso-e)  
Put token in [./env/.env.secrets](./env/.env.secrets)

Market configuration is located in [./docker/entsoe-service/entsoe.yaml](./docker/entsoe-service/entsoe.yaml)

#### Additional information

Service on start loads prices for the last 5 days for the configured markets

### Trading Manager

#### Configuration

Sample TM configuration with subscribed markets can be found here: [config](./docker/trading-manager/config.yaml)

### PGAdmin (DB viewer)

By default PGAdmin is exposed to: http://localhost:9199/

Login settings:

```
system: postgresql
server: local-tm-db-1
Username: postgres
password: postgres
database: postgres
```

```
schema: public
```

## Docker

Root directory: `local_dev`

Download & import docker images [here](#download-images)

### Build

```yaml
docker-compose -p local -f compose.yaml --env-file .env build 
```

### Run

```yaml
docker-compose -p local -f compose.yaml --env-file .env create
docker-compose -p local -f compose.yaml --env-file .env start 
```

check consumed resources:

```yaml
 docker stats --no-stream --format "{{.Container}} cpu={{.CPUPerc}} mem={{.MemUsage}} net={{.NetIO}} name:{{.Name}}"
```

### Download images

```shell

#download images from:
https://box.pionier.net.pl/d/2782022c45ce4360a8c5/

```

old links:

```shell

#configured  trading manager service
https://box.pionier.net.pl/f/850de4ebd6f54d1b8613/?dl=1
#configured entso-e service
https://box.pionier.net.pl/f/617f3569a0f244de9af6/?dl=1
#base entso-e image for docker build
https://box.pionier.net.pl/f/617f3569a0f244de9af6/?dl=1
```

### import image

```shell
docker load -i ./images/trading-manager.0.5.1.tar
docker load -i ./images/local-entsoe-service.latest.tar 
docker load -i ./images/base-entsoe-service.latest.tar
```

### export image

```shell

docker save -o "./images/trading-manager.$Env:TM_TAG.tar" "$Env:REGISTRY_DOMAIN/$Env:REGISTRY_PROJECT/trading-manager:$Env:TM_TAG"
docker save -o ./images/local-entsoe-service.latest.tar "$Env:REGISTRY_DOMAIN/$Env:REGISTRY_PROJECT/local-entsoe-service:latest" 
docker save -o ./images/base-entsoe-service.latest.tar "$Env:REGISTRY_DOMAIN/$Env:REGISTRY_PROJECT/tm-entsoe-service:latest" 
 

```

## Samples Digital Twin and Flexibility Manager clients

### Build

```yaml
docker-compose -p local -f sample.yaml --env-file .env build 
```

### Override main script with custom script
 
in sample.yaml
```yaml

...
  volumes:
      - ./input/dt_ki.py:/app/examples/dt_ki.py
...
...
  volumes:
      - ./input/fm_ki.py:/app/examples/fm_ki.py
...
```

### Logs
```shell

#DT docker:
docker exec local-dt-service-1 cat /var/log/service.log
docker cp local-dt-service-1:/var/log/service.log dt.service.log

#FM docker
docker exec local-fm-service-1 cat /var/log/service.log
docker cp local-fm-service-1:/var/log/service.log fm.service.log

```

```shell

docker logs local-fm-service-1

```