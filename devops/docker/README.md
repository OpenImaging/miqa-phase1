# Docker deployment

Deploy MIQA system with Docker.

## Prerequisite
* Docker 18.03+

## Populate variables
* Make a copy of .env.template file and rename it to .env file
* Populate and update fields. *GIRDER_ADMIN_PASS* needs to be at least 6 characters long

## Build
* At current directory
* `docker-compose build`
* `docker-compose up` should finish without error
* MIQA should be available at localhost
