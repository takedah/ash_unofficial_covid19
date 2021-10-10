FROM nginx:stable-alpine

COPY ./dockerfiles/nginx.conf /etc/nginx/nginx.conf

ENV PORT=49152

CMD sed -i -e 's/$REPLACE/'"$PORT"'/g' /etc/nginx/nginx.conf && nginx -g 'daemon off;'
