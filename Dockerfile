FROM ubuntu:latest

RUN DEBIAN_FRONTEND=noninteractive ls

RUN DEBIAN_FRONTEND=noninteractive \
  apt-get update \
  && apt-get install -y python3 \
  && apt-get install -y pip \
  && apt-get install -y libapache2-mod-wsgi-py3



WORKDIR /app

COPY requirements.txt requirements.txt

RUN DEBIAN_FRONTEND=noninteractive pip -V

RUN DEBIAN_FRONTEND=noninteractive pip install -r requirements.txt

EXPOSE 80

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y apache2

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

CMD service apache2 start && uwsgi --ini /app/wsgi.ini
