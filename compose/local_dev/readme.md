
## Services

### ENTSO-E

#### Configure

Service documentation is [here](https://github.com/BlueBird-project/tm-market-plugins/blob/main/entso-e/README.md)
List of market codes is [here](https://transparencyplatform.zendesk.com/hc/en-us/articles/15885757676308-Area-List-with-Energy-Identification-Code-EIC)


Configuration:
1. Obtain API Token (ENTSOE_TOKEN) - [acquire token](https://www.amsleser.no/blog/post/21-obtaining-api-token-from-entso-e)  
2. Set API Token in [./env/.env.secrets](./env/.env.secrets)
3. Configure markets [./docker/entsoe-service/entsoe.yaml](./docker/entsoe-service/entsoe.yaml)


#### Additional information

 * Service on start loads prices for the last 5 days for the configured markets

### Trading Manager

#### Configuration

Sample TM configuration with subscribed country markets can be found [here (configuration loaded in compose.yaml)](./docker/trading-manager/app_config.yaml)
and  [here](./docker/trading-manager/config.yaml)

### Sample FM Service

This service provides sample FM Smart Client implementation with sample interactions fed with random data.
Docker configuration is [here](./docker/fm-service/Dockerfile) and FM service sources are located[here](./docker/fm-service/examples)   


### Sample DT service 

This service provides sample DM Smart Client implementation with sample interactions fed with random data.
Docker configuration is [here](./docker/dt-service/Dockerfile) and FM service sources are located[here](./docker/dt-service/examples)  



### PGAdmin (DB web gui)

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



## Docker images

Root directory: `local_dev`

Download & import docker images [here](#download-images)

### Build

Set env variables
```shell
./set-env.ps1
```

```yaml
docker-compose -p local -f compose.yaml --env-file .env build

#with samples:
docker-compose -p local -f sample_compose.yaml --env-file .env build

#samples + tge
docker-compose -p local -f all_compose.yaml --env-file .env --env-file ./env/.env.secrets  build

```

### Run

```yaml
docker-compose -p local -f compose.yaml --env-file .env create
docker-compose -p local -f compose.yaml --env-file .env start

#with samples:
docker-compose -p local -f sample_compose.yaml --env-file .env create
docker-compose -p local -f sample_compose.yaml --env-file .env start

#samples + tge service
docker-compose -p local -f all_compose.yaml --env-file .env --env-file ./env/.env.secrets  create
docker-compose -p local -f all_compose.yaml --env-file .env --env-file ./env/.env.secrets  start 
```

check consumed resources:

```yaml
 docker stats --no-stream --format "{{.Container}} cpu={{.CPUPerc}} mem={{.MemUsage}} net={{.NetIO}} name:{{.Name}}"
```

### Download images

```shell

#download images from:
https://box.pionier.net.pl/d/7603fc382fa74e89a490/

#old link
https://box.pionier.net.pl/d/2782022c45ce4360a8c5/

```
 
### import image

```shell
docker load -i .\images\trading-manager.latest.tar
docker load -i .\images\local-entsoe-service.latest.tar

#DT and FM sample dockers 
docker load -i .\images\local-dt-service.tar
docker load -i .\images\local-fm-service.tar

# ENTSO-E build/base image
docker load -i .\images\base-entsoe-service.latest.tar 
#TGE service
docker load -i .\images\bluebird.tge-dayahead-service_latest.ta
```

### export image

```shell

docker save -o "./images/trading-manager.$Env:TM_TAG.tar" "$Env:REGISTRY_DOMAIN/$Env:REGISTRY_PROJECT/trading-manager:$Env:TM_TAG"
docker save -o "./images/trading-manager.latest.tar" "$Env:REGISTRY_DOMAIN/$Env:REGISTRY_PROJECT/trading-manager:$Env:TM_TAG" "$Env:REGISTRY_DOMAIN/$Env:REGISTRY_PROJECT/trading-manager:latest"

docker save -o "./images/local-entsoe-service.latest.tar" "$Env:REGISTRY_DOMAIN/$Env:REGISTRY_PROJECT/local-entsoe-service:latest" 
docker save -o "./images/local-dt-service.tar"  "$Env:REGISTRY_DOMAIN/$Env:REGISTRY_PROJECT/local-dt-service:latest" 
docker save -o "./images/local-fm-service.tar"  "$Env:REGISTRY_DOMAIN/$Env:REGISTRY_PROJECT/local-fm-service:latest" 

docker save -o "./images/base-entsoe-service.$Env:ENTSO_E_TAG.tar" "$Env:REGISTRY_DOMAIN/$Env:REGISTRY_PROJECT/tm-entsoe-service:$Env:ENTSO_E_TAG" "$Env:REGISTRY_DOMAIN/$Env:REGISTRY_PROJECT/tm-entsoe-service:latest" 
docker save -o "./images/base-entsoe-service.latest.tar" "$Env:REGISTRY_DOMAIN/$Env:REGISTRY_PROJECT/tm-entsoe-service:latest" 

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