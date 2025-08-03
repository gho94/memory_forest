FROM mysql:8.0

ENV MYSQL_ROOT_PASSWORD=mysql
ENV MYSQL_DATABASE=memory_forest
ENV MYSQL_USER=kcc
ENV MYSQL_PASSWORD=kcc

COPY init.sql /docker-entrypoint-initdb.d/

EXPOSE 3306