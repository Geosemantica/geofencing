FROM python:3.12.3 AS gf-svc

WORKDIR /gf
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

RUN apt-get update && apt-get install --no-install-recommends -y \
    ca-certificates \
    git \
    wget

RUN install -d /usr/share/postgresql-common/pgdg && \
    wget -O /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc https://www.postgresql.org/media/keys/ACCC4CF8.asc && \
    echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && apt-get install --no-install-recommends -y \
    postgresql-client-16

RUN apt-get remove --yes wget && \
    apt-get autoremove --yes && \
    apt-get clean --yes && \
    rm -rf /var/lib/apt/* /var/cache/apt/* /root/.cache

COPY . .
RUN mv /gf/app/main.py /gf

COPY datamodel ./datamodel
COPY alembic.ini ./alembic.ini
COPY postgresql/initial-dump.sql ./initial-dump.sql

COPY init.sh ./init.sh
RUN chmod +x ./init.sh

ENTRYPOINT ./init.sh
