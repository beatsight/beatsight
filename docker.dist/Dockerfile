#-------------------- core server
FROM beatsight-core:nightly as core-serv

#-------------------- frontend dist
FROM beatsight-web:nightly as frontend

#-------------------- web app

#FROM python:3.9.6-slim-buster
FROM ubuntu:22.04

MAINTAINER zhengxie@beatsight.com

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    htop \
    supervisor \
    nginx \
    poppler-utils \
    git \
    procps \
    python3 \
    python3-pip \
&& rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    wget \
&& rm -rf /var/lib/apt/lists/*

# add our user and group first to make sure their IDs get assigned consistently
RUN groupadd -r ubuntu && useradd -r -m -g ubuntu ubuntu

# grab gosu for easy step-down from root
ARG GOSU_VERSION=1.17
ARG GOSU_SHA256=bbc4136d03ab138b1ad66fa4fc051bafc6cc7ffae632b069a53657279a450de3
ARG TINI_VERSION=0.19.0
ARG TINI_SHA256=93dcc18adc78c65a028a84799ecf8ad40c936fdfc5f2a57b1acda5a8117fa82c

RUN wget --quiet -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-amd64" \
  && echo "$GOSU_SHA256 /usr/local/bin/gosu" | sha256sum --check --status \
  && chmod +x /usr/local/bin/gosu

ENV HOME_DIR="/home/ubuntu"
ENV LOG_DIR="${HOME_DIR}/logs"
ENV BUILD_DIR="${HOME_DIR}/build"
ENV RUNTIME_DIR="${HOME_DIR}/runtime"
ENV INSTALL_DIR="${HOME_DIR}/beatsight"

# SET work dir
WORKDIR ${HOME_DIR}
RUN mkdir -p ${LOG_DIR}

# Install python requirements
#COPY docker.dist/pip.conf /etc/pip.conf
COPY requirements.txt ${INSTALL_DIR}/requirements.txt
RUN cd ${INSTALL_DIR} && pip3 install -r requirements.txt && cd -

# Set up application and its running environment
COPY docker.dist/utility/ ${BUILD_DIR}/
COPY docker.dist/runtime/ ${RUNTIME_DIR}/

# Update nginx/uswgi/..etc confs
RUN cd /etc/nginx/sites-enabled/ && rm default && ln -s ${RUNTIME_DIR}/beatsight.nginx.conf default && cd -
RUN chmod 755 ${BUILD_DIR}/django-install.sh \
    && chmod 755 ${BUILD_DIR}/entrypoint.py \
    && bash ${BUILD_DIR}/django-install.sh

COPY . ${INSTALL_DIR}
RUN chown -R ubuntu:ubuntu ${HOME_DIR}
RUN chmod -R 755 ${HOME_DIR}

WORKDIR ${INSTALL_DIR}

# compile .py files
RUN python3 ${BUILD_DIR}/compile.py --python-source=${INSTALL_DIR}

# Copy the binary to the production image from the builder stage.
COPY --from=core-serv /app/server ${INSTALL_DIR}/core-serv/server
COPY --from=core-serv /app/core.conf ${INSTALL_DIR}/core-serv/core.conf
COPY --from=frontend /app/dist ${INSTALL_DIR}/frontend/dist

EXPOSE 22/tcp 8000/tcp
#VOLUME ["${LOG_DIR}"]

ENTRYPOINT exec ${BUILD_DIR}/entrypoint.py "$0" "$@"
#ENTRYPOINT ["${BUILD_DIR}/entrypoint.py"]
CMD ["beatsight"]
