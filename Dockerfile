FROM ubuntu:latest

RUN DEBIAN_FRONTEND=noninteractive \
  apt-get update \
  && apt-get install -y python3 pip libapache2-mod-wsgi-py3 apache2 cron curl

RUN DEBIAN_FRONTEND=noninteractive echo '* * * * * curl "http://localhost/check_hash"' | crontab -

WORKDIR /app

COPY requirements.txt requirements.txt

RUN DEBIAN_FRONTEND=noninteractive pip -V

RUN DEBIAN_FRONTEND=noninteractive pip install --break-system-packages -r requirements.txt

EXPOSE 80

COPY /app /app
RUN chown -R www-data:www-data /app


RUN rm -f /etc/apache2/sites-enabled/*
COPY VirtualHost.conf /etc/apache2/sites-enabled/VirtualHost.conf

COPY apache2.conf /etc/apache2/apache2.conf

COPY users.password /usr/local/apache/var/users.password
RUN chown www-data:www-data /usr/local/apache/var/users.password
RUN chmod 500 /usr/local/apache/var/users.password

COPY webdav /var/webdav
RUN chown www-data:www-data -R /var/webdav
RUN ln -s /var/webdav /app/conf

RUN a2enmod dav dav_fs auth_digest proxy_http

CMD service apache2 start && service cron start && uwsgi --ini /app/wsgi.ini
