REPOSTAT=/Users/xiez/dev/beatsight/vendor/repostat/

run:
	export PYTHONPATH=$(REPOSTAT):$PYTHONPATH && python manage.py runserver 0.0.0.0:8081

css:
	npx tailwindcss -i ./static-local/assets/css/input.css -o ./static-local/assets/css/output.css --watch

shell:
	export PYTHONPATH=$(REPOSTAT):$PYTHONPATH && python manage.py shell

sql:
	export PYTHONPATH=$(REPOSTAT):$PYTHONPATH && python manage.py makemigrations

mig:
	export PYTHONPATH=$(REPOSTAT):$PYTHONPATH && python manage.py migrate

pull:
	export PYTHONPATH=$(REPOSTAT):$PYTHONPATH && python manage.py pull

curl:
	curl http://localhost:8081/stats/ |  python -mjson.tool

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

docker.build.web:
	docker-compose -f docker/docker-compose.dev.yaml build web

docker.up:
	COMPOSE_PROJECT_NAME=beatsight docker-compose -f docker/docker-compose.dev.yaml up

docker.up.app:
	COMPOSE_PROJECT_NAME=beatsight docker-compose -f docker/docker-compose.dev.yaml up app

docker.up.celery:
	COMPOSE_PROJECT_NAME=beatsight docker-compose -f docker/docker-compose.dev.yaml up celery

docker.up.beat:
	COMPOSE_PROJECT_NAME=beatsight docker-compose -f docker/docker-compose.dev.yaml up beat

docker.up.web:
	COMPOSE_PROJECT_NAME=beatsight docker-compose -f docker/docker-compose.dev.yaml up web

docker.sh:
	COMPOSE_PROJECT_NAME=beatsight docker-compose -f docker/docker-compose.dev.yaml exec app bash

docker.sh.web:
	COMPOSE_PROJECT_NAME=beatsight docker-compose -f docker/docker-compose.dev.yaml exec web bash

docker.down:
	COMPOSE_PROJECT_NAME=beatsight docker-compose -f docker/docker-compose.dev.yaml down
