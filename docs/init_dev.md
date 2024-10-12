## Env

sudo apt-get update
sudo apt install git nginx supervisor

wget https://go.dev/dl/go1.23.1.linux-amd64.tar.gz
tar xf go1.23.1.linux-amd64.tar.gz
sudo mv go /usr/local/

vi  ~/.profile

export PATH=$PATH:/usr/local/go/bin
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin

source ~/.profile


## clone beatsight/core

git clone git@github.com:xiez/beatsight-core.git
cd beatsight-core
make dist

## clone beatsight/web

git clone git@github.com:xiez/beatsight-web.git
cd beatsight-web
make pull

## beatsight

git clone --recurse-submodules git@github.com:xiez/beatsight.git
sudo apt-get install python3-pip
pip3 install -r requirements.txt

## beatsight data dir

sudo mkdir /beatsight-data
sudo chown ubuntu:ubuntu /beatsight-data

ssh-keygen

/beatsight-data/id_rsa

### add key to gitlab


## TODO: init data

## static files

```
sudo chown -R www-data:www-data /home/ubuntu/beatsight/static/
sudo chmod -R 755 /home/ubuntu/beatsight/static/
```

## migarte

export PYTHONPATH=/home/ubuntu/dev/beatsight/vendor/repostat/:$PYTHONPATH
python3 manage.py  migrate
python3 manage.py collectstatic

curl http://localhost:9998

---


## celery

sudo apt-get install redis-server
sudo systemctl start redis-server

## rabbitmq

https://www.rabbitmq.com/docs/install-debian

---

## supervisor

sudo apt install supervisor

cd /etc/supervisor/conf.d
sudo ln -s /home/ubuntu/dev/beatsight/conf/supervisord.conf.tmpl beatsight.conf

ubuntu@ip-172-31-33-136:/etc/supervisor/conf.d$ sudo ln -s ~/beatsight_www/conf/supervisord.conf www.conf

sudo supervisorctl update

sudo chown ubuntu:ubuntu ~/beatsight/logs -R

## nginx

cd /etc/nginx/sites-enabled/
ubuntu@stg:/etc/nginx/sites-enabled$ sudo rm default
sudo ln -s ~/beatsight/conf/nginx.conf.tmpl beatsight.conf

## lets encrypt

sudo apt install certbot python3-certbot-nginx

sudo certbot --nginx -d stg.beatsight.com
sudo certbot --nginx -d www.beatsight.com

sudo certbot --nginx -d stg.beatsight.com -d demo.beatsight.com
