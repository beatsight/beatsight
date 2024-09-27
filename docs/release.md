# 发布流程

以版本 1.2.0 为例子

## 1. build images

### core

➜  beatsight-core git:(master) ✗ make docker.dist VERSION=v1.2.0

### frontend

make docker.dist VERSION=v1.2.0

### backend

make docker.dist VERSION=v1.2.0

### test image

make test.dist

### upload to dockerhub

## 2. beatsight-docker installer

bump version to v1.2.0 in `.env` file

create tag v1.2.0


## 3. 下载安装

### 首次安装

1. git clone beatsight-docker repo

2. git fetch and checkout tag v1.2.0

3. ./install.sh

4. ./start.sh & ./stop.sh

5. superuser: `docker compose run web python3 manage.py  createsuperuser`

### 旧版本升级（小版本）

1. git fetch and checkout tag v1.2.3

2. ./install.sh

3. ./start.sh & ./stop.sh


### 旧版本升级（大版本）

1. git fetch and checkout tag v1.3.0

2. ./install.sh

3. ./upgrades/v1.2-1.3.sh

4. ./start.sh & ./stop.sh


### 旧版本升级（跨大版本）

1. git fetch and checkout tag v1.4.0

2. ./install.sh

3. ./upgrades/v1.2-1.3.sh & ./upgrades/v1.3-1.4.sh

4. ./start.sh & ./stop.sh


