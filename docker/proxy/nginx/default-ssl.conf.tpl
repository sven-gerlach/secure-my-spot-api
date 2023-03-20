server {
    listen 80;
    server_name ${DOMAIN};

    location /.well-known/acme-challenge/ {
        root /vol/www/;
    }

    location / {
        rewrite ^ https://$host$request_uri? permanent;
    }
}

server {
    listen 443 ssl;
    server_name ${DOMAIN};

    ssl_certificate         /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key     /etc/letsencrypt/live/${DOMAIN}/privkey.pem;

    include /etc/nginx/options-ssl-nginx.conf;

    ssl_dhparam /vol/proxy/ssl-dhparams.pem;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location /static {
        alias /vol/static;
    }

    location / {
        proxy_pass              http://${APP_HOST}:${APP_PORT};
        proxy_set_header        Host $host;
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header        X-Forwarded-Proto $scheme;
        client_max_body_size    10M;
    }
}