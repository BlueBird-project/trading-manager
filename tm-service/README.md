# Trading Manager

## Description

The Trading Manager (TM) is a core component of the BlueBird project, responsible for enabling interaction with multiple energy markets and providing market-related intelligence to other system components, in particular the Flexibility Manager (FM). Its primary function is to acquire energy price data—covering both energy production and energy consumption—for defined time intervals and to deliver this information in a structured form suitable for further optimisation and decision-making processes.

### Field description

* 'ISP' - An Imbalance Settlement Period (ISP) is the specific time interval in the electricity market used to calculate the difference between how much power
  a market participant (like a power generator or supplier) contracted to generate/consume and how much they actually generated/consumed
* 'isp_unit' - isp time range unit , by default in minutes (Countries in EU use 15min interval - 2026-06-12).
* 'isp_start' - determines the offset since the beginning off the offer . `isp_start=0` - first ISP, `isp_start=4` - starts on  hour after the beginning (for 15 minute unit)

### Graph Patterns 

Smart client configuration and TM shared knowledge graph patterns are in: [ke_config.yaml](./resources/deployment/ke_config.yaml)
TM Smart Client connection graph patterns  to read/subscribe data from other clients in the network  are located in thus [directory](./resources/deployment/ki)


## TM docker management

#### Build:

```
docker-compose -f .\compose\local.yaml --env-file .\resources\.env build

docker-compose -f .\compose\local.yaml --env-file .\resources\.env build tm-service

docker-compose -f .\compose\local.yaml --env-file .\resources\.env build tm-service --no-cache
```

#### Export docker imager

docker save -o d:/tmp/tm-service-app_latest.tar tm-service-app:latest
docker save -o d:/tmp/${image_name}_${image_version}.tar ${full_image_name}

docker save -o d:/tmp/${image_name}_${image_version}.tar ${full_image_name}

## Healthcheck

Service status API (Swagger docs):
```
http://localhost:9090/healthcheck/docs (
```
## Samples 

### Smart Clients Samples

* Flexibility Manager   : `./examples/ki/fm_ki.py`
* Digital Twin : `./examples/ki/dm_ki.py`

### Testing KI interactions

Testing the REACT and ANSWER KE Interaction (FM and DT), The Swagger UI is available by default at:
```
http://{TM_HOST}:{TM_PORT}/api#/KI (swagger)
 
http://localhost:9090/api#/KI
``` 
The Swagger interface allows users to manually trigger data Knowledge Interactions without waiting for the scheduled execution cycle.  



## License

TODO: