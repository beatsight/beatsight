FROM python:3.10-slim-bookworm
MAINTAINER xiez1989@gmail.com

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

USER 0

RUN apt-get update -y --fix-missing
RUN apt-get install -y build-essential gcc
RUN apt-get install -y git procps
RUN apt-get install -y nano gettext

WORKDIR /Users/xiez/dev/beatsight

COPY requirements.txt requirements.txt
COPY requirements-dev.txt requirements-dev.txt

RUN pip install --ignore-installed -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements-dev.txt
#RUN pip install --ignore-installed -r requirements-dev.txt

#RUN mkdir vendor
#COPY vendor/repostat/requirements.txt vendor/requirements.txt
#COPY vendor/repostat/requirements-dev.txt vendor/requirements-dev.txt



EXPOSE 22/tcp 80/tcp 8080/tcp


