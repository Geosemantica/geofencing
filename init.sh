cd /gf
alembic upgrade head
echo Restoring initial dump for:
echo user: $POSTGRES_USER
echo host: $POSTGRES_HOST:$POSTGRES_PORT
echo db:   $POSTGRES_DATABASE
echo "initial-dump.sql"

psql postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DATABASE \
       --file=/gf/initial-dump.sql

gunicorn main:app \
           --bind=0.0.0.0:8000 \
           --timeout 600 \
           --log-level=debug \
           --worker-class uvicorn.workers.UvicornWorker
