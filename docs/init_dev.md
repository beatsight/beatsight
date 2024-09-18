sudo apt-get update

sudo apt install git nginx

wget https://go.dev/dl/go1.23.1.linux-amd64.tar.gz
tar xf go1.23.1.linux-amd64.tar.gz
sudo mv go /usr/local/

vi  ~/.profile

export PATH=$PATH:/usr/local/go/bin
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin


source ~/.profile

## ssh key

ssh-keygen

## beatsight

git clone git@github.com:xiez/beatsight.git
sudo apt-get install python3-pip
pip3 install -r requirements.txt

## vendor/repostat

mkdir -p beatsight/vendor && cd beatsight/vendor
git clone git@github.com:xiez/repostat.git

## data/id_rsa

cd ~/beatsight

ssh-keygen
/home/ubuntu/beatsight/data/id_rsa

### add key to gitlab

## clone beatsight/web

cd
git clone git@github.com:xiez/beatsight-web.git
cd beatsight-web
make pull

## clone beatsight/core

cd
git clone git@github.com:xiez/beatsight-core.git


## TODO: init data

## static files

```
sudo chown -R www-data:www-data /home/ubuntu/beatsight/static/
sudo chmod -R 755 /home/ubuntu/beatsight/static/
```

## migarte

export PYTHONPATH=/home/ubuntu/beatsight/vendor/repostat/:$PYTHONPATH
python3 manage.py  migrate

curl http://localhost:9998

---


## celery

sudo apt-get install redis-server
sudo systemctl start redis-server

---

## supervisor

sudo apt install supervisor

cd /etc/supervisor/conf.d
sudo ln -s ~/beatsight/conf/supervisord.conf.tmpl beatsight.conf

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
