## docker compose

sudo curl -L "https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-$(uname -s)-$(uname -m)"  -o /usr/local/bin/docker-compose
sudo mv /usr/local/bin/docker-compose /usr/bin/docker-compose
sudo chmod +x /usr/bin/docker-compose


## harbor online-installer

https://goharbor.io/docs/2.11.0/install-config/download-installer/


## nginx lets encrypt

https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-20-04

sudo apt install certbot python3-certbot-nginx

sudo certbot --nginx -d docker.beatsight.com

### perm & priv key

```
   ssl_certificate /etc/letsencrypt/live/reg.beatsight.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/reg.beatsight.com/privkey.pem;
```
