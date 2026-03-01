## Docker

Root directory: `local_dev`

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
## Services

### ENTSO-E

#### Configure

This service requires API TOKEN (
ENTSOE_TOKEN) - [acquire token](https://www.amsleser.no/blog/post/21-obtaining-api-token-from-entso-e)  
Put token in [./env/.env.secrets](./env/.env.secrets)

Market configuration is located in [./docker/entsoe-service/entsoe.yaml](./docker/entsoe-service/entsoe.yaml)

#### Additional information

Service loads prices for 5 days for configured markets

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

##### sample FM URI:

http://fm.bluebird.com/ts/1772215794840/1772302194840/15/2

## export image

```shell

docker save -o ./images/trading-manager.0.3.0.tar "$Env:REGISTRY_DOMAIN/$Env:REGISTRY_PROJECT/trading-manager:0.3.0"
docker save -o ./images/tm-demo-entsoe-service.latest.tar "$Env:REGISTRY_DOMAIN/$Env:REGISTRY_PROJECT/tm-demo-entsoe-service:latest" 

```

załadowanie obrazów:
docker load -i ./images/trading-manager.0.3.0.tar
docker load -i ./images/tm-demo-entsoe-service.latest.tar

stworzenie kontenerów:
docker-compose -p bb_local -f demo.yaml --env-file .env create

uruchomienie
docker-compose -p pmb -f demo.yaml --env-file .env start

uruchomienie pozostałych kontenerów ( kontenery uruchamiają się szybciej niż postgresql zacznie odpowiadać) :
docker-compose -p pmb -f demo.yml --env-file .env start

Odpytanie w konsoli o dane z rynku (dwa państwa do testów, data poczatku oferty - w formacie yyyy-mm-dd) :
docker exec pmb-tm-service-1 python demo_ki.py --country {country_name} -d {date}

docker exec pmb-tm-service-1 python demo_ki.py --country POLAND -d 2026-01-31
docker exec pmb-tm-service-1 python demo_ki.py --country SPAIN -d 2026-01-31

docker exec pmb-tm-service-1 python demo_ki.py --country SPAIN -d 2026-01-31 --type dayahead
docker exec pmb-tm-service-1 python demo_ki.py --country SPAIN -d 2026-01-31 --type intraday
w demie dostępne dane sa z ostatnich 30 dni  (docelowo bedzie trzeba zaimplementować pobieranie danych na żądanie :

pgadmin (baza danych):
http://localhost:9199/

dane logowania
system: postgresql
server: pmb-tm-db-1
Username: postgres
password: postgres
database: postgres

Tabele, każdy serwis ma swój prefix:

- 'bb_tm_' to trading manager
- 'demo_entsoe_' serwis pobierajace dane z entsoe
- 'demo_tm_' tabele ktore uzupełniane przez skrypt demo_ki.py

market_details -> tabele dotyczace informacji o rynkacj
offer_details -> tabele zawierające metadane o danej ofercie (np ceny z danego dnia )
market_offer -> tabela z cenami w czasie

ISP to jest w skrocie jednostka czasu dla ktorej jest wyznaczona cena (np 15 minut, 60 minut itp) -> te nazwy wziąłem z
USEF framework , ponieważ opieramy sie bardziej o KE to pewnie to zmienie z czasem
ISP_START - indeks (lub 'offset') początku przedziału czasu dla ceny ISP=1 - to po prostu poczatek pierwszego punktu
oferty (np godzina 0:00 dla rynku dnia następnego) , ISP_START=95 to 23:45
ISP_LEN - długość danego przedziału czasu ISP_LEN = 1 to dla nas 15 minut, ale czasami cena się powtarza, czyli
ISP_LEN=4 oznacza te samą cene przez 60minut