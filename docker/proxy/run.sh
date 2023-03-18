#!/usr/bin/env sh

set -e

echo "Checking for ssl-dhparams.pem"
if [ ! -f "/vol/proxy/ssl-dhparams.pem" ]; then
  echo "ssl-dhparams.pem does not exist. Creating it..."
  openssl dhparam -out /vol/proxy/ssl-dhparams.pem 2048
  echo "ssl-dhparams.pem created at /vol/proxy/"
fi

# avoid replacing nginx variables with envsubst
export host=\$host
export request_uri=\$request_uri
export remote_addr=\$remote_addr
export proxy_add_x_forwarded_for=\$proxy_add_x_forwarded_for
export scheme=\$scheme

# if fullchain.pem already exists then ssl has already been set up and nginx.tsl.conf ought to be run
# otherwise run nginx.conf
echo "checking for fullchain.pem"
if [ ! -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
  echo "No SSL certificate, enabling HTTP only..."
  envsubst < /etc/nginx/nginx.conf > /etc/nginx/conf.d/default.conf
else
  echo "SSL certificate exists, enabling HTTPS..."
  envsubst < /etc/nginx/nginx.ssl.conf > /etc/nginx/conf.d/default.conf
fi

nginx -g 'daemon off;'