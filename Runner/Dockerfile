FROM nginx:alpine
LABEL Author="CTF-HackConRD"

COPY src /usr/share/nginx/html
RUN sed -i 's/listen\s*80;/listen 8023;/g' /etc/nginx/conf.d/default.conf

EXPOSE 8023