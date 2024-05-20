REPOSTAT=/Users/xiez/dev/beatsight/vendor/repostat/

run:
	export PYTHONPATH=$(REPOSTAT):$PYTHONPATH && python manage.py runserver 0.0.0.0:8081

shell:
	export PYTHONPATH=$(REPOSTAT):$PYTHONPATH && python manage.py shell

dbchange:
	export PYTHONPATH=$(REPOSTAT):$PYTHONPATH && python manage.py makemigrations

dbapply:
	export PYTHONPATH=$(REPOSTAT):$PYTHONPATH && python manage.py migrate

pull:
	export PYTHONPATH=$(REPOSTAT):$PYTHONPATH && python manage.py pull

clean:
	rm -rf db.sqlite3 && \
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete && \
	find . -path "*/migrations/*.pyc" -delete

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
