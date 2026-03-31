# Trading Manager

## Description

The Trading Manager (TM) is a core component of the BlueBird project, responsible for enabling interaction with multiple energy markets and providing market-related intelligence to other system components, in particular the Flexibility Manager (FM). Its primary function is to acquire energy price data—covering both energy production and energy consumption—for defined time intervals and to deliver this information in a structured form suitable for further optimisation and decision-making processes.

## docker management

docker-compose -f .\compose\local.yml --env-file .\resources\.env build
docker-compose -f .\compose\local.yml --env-file .\resources\.env build tm-service

docker-compose -f .\compose\local.yml --env-file .\resources\.env build --no-cache

docker save -o d:/tmp/tm-service-app_latest.tar tm-service-app:latest
docker save -o d:/tmp/${image_name}_${image_version}.tar ${full_image_name}

docker save -o d:/tmp/${image_name}_${image_version}.tar ${full_image_name}

### Healthcheck

http://localhost:9090/healthcheck/docs
 
 

 
## Installation
 

## Usage
 
## Support
  

## License

For open source projects, say how it is licensed.
 