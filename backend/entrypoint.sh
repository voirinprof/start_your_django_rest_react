#!/bin/sh
set -e

echo "Attente de la disponibilité de PostgreSQL..."
until python -c "
import psycopg, os, sys
try:
    psycopg.connect(
        dbname=os.environ.get('POSTGRES_DB', 'geodb'),
        user=os.environ.get('POSTGRES_USER', 'geouser'),
        password=os.environ.get('POSTGRES_PASSWORD', 'geopassword'),
        host=os.environ.get('POSTGRES_HOST', 'db'),
        port=os.environ.get('POSTGRES_PORT', '5432'),
    )
except Exception as e:
    sys.exit(1)
"; do
  sleep 1
done

echo "PostgreSQL est prêt. Application des migrations..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

echo "Démarrage du serveur..."
exec "$@"
