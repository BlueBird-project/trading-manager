## Flexibility Manager

### Run

load env files :

- ./resources/.env
- ./resources/env/.env.fm

sample client: `./examples/fm_ki.py ` (working directory - project/repository root directory)

ANSWER and REACT knowledge interaction can be triggered from Trading Manager REST API (KI section):

``` 
http://{TM_HOST}:{TM_PORT}/api#/KI (swagger)
For example:
http://localhost:9090/api#/KI
```

## Digital Twin

### Run

load env files :

- ./resources/.env
- ./resources/env/.env.tm

sample client: `./examples/tm_ki.py ` (working directory - project/repository root directory)

ANSWER and REACT knowledge interaction can be triggered from Trading Manager REST API (KI section):

``` 
http://{TM_HOST}:{TM_PORT}/api#/KI (swagger)
For example:
http://localhost:9090/api#/KI
```