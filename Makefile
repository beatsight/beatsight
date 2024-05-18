# ##################################################
action:
	@echo action $(filter-out $@,$(MAKECMDGOALS))

%:
    @:

test:
	nose2

html:
	python -m analysis.repostat  . output/repostat.output

# seahub:
# 	python -m analysis.repostat  /seahub output/seahub.output

json:
	python -m analysis.repostat  /$(filter-out $@,$(MAKECMDGOALS)) output/xxx.output

# docker dev ----------------------------------------
docker.build:
	docker-compose -f docker/docker-compose.dev.yaml build app

docker.up:
	COMPOSE_PROJECT_NAME=beatsight docker-compose -f docker/docker-compose.dev.yaml up app

docker.sh:
	COMPOSE_PROJECT_NAME=beatsight docker-compose -f docker/docker-compose.dev.yaml exec app bash

docker.down:
	COMPOSE_PROJECT_NAME=beatsight docker-compose -f docker/docker-compose.dev.yaml down
