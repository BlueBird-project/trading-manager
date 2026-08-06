# Trading Manager (TM)

## About
The Trading Manager is a core component of the BlueBird project, responsible for enabling interaction with multiple energy markets and providing market-related intelligence to other system components, in particular the Flexibility Manager (FM) (TODO: link). It's primary function is to acquire energy price data, covering both energy production and
energy consumption, for defined time intervals and to deliver this information in a structured form suitable for further optimization and decision-making processes.

## UBFlex integration
This component integrates with [UBFlex](https://github.com/BlueBird-project/UBFlex), the BlueBird common interface for Knowledge Engine-based interoperability. UBFlex provides BlueBird-specific ontology definitions, graph-pattern configurations and related integration resources. This repository retains responsibility for its own domain logic and implementation. For UBFlex integration assets and documentation, see the [UBFlex repository](https://github.com/BlueBird-project/UBFlex).

The Flexibility Manager uses UBFlex for relevant exchanges with connected services while retaining responsibility for local asset modelling, optimisation, operational constraints and control actions.

## Repository structure
* TM main repository - implements KE Smart Client connector and provides REST service: [tm-service](https://github.com/BlueBird-project/trading-manager/tree/main/tm-service) 
* Docker container configuration: [compose](https://github.com/BlueBird-project/trading-manager/tree/main/compose) 
* [bidding-opt](https://github.com/BlueBird-project/trading-manager/tree/main/bidding-opt) - TODO:



