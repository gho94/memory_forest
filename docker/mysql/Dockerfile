FROM mysql:8.0

ENV MYSQL_ROOT_PASSWORD=mysql
ENV MYSQL_DATABASE=myapp
ENV MYSQL_USER=app_user
ENV MYSQL_PASSWORD=mysql

COPY init.sql /docker-entrypoint-initdb.d/

EXPOSE 3306