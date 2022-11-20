FROM nginx:stable-alpine

RUN mkdir /var/gunicorn

RUN chmod 777 /var/gunicorn

COPY ./dockerfiles/nginx.conf /etc/nginx/nginx.conf
COPY ./dockerfiles/mime.types /etc/nginx/mime.types
