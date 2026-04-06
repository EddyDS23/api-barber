#!/bin/sh

echo "================================================"
echo " BarberSaaS API - Ambiente de Desarrollo"
echo "================================================"

echo "Aplicando migraciones..."
python manage.py migrate


echo "Ejecutando init.sql solo si es primera vez..."
TABLE_EXISTS=$(PGPASSWORD=$POSTGRES_PASSWORD psql \
  -h db -U $POSTGRES_USER -d $POSTGRES_DB \
  -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='barbers';")

if [ "$TABLE_EXISTS" = "0" ]; then
  echo "Primera vez: aplicando schema..."
  PGPASSWORD=$POSTGRES_PASSWORD psql \
    -h db -U $POSTGRES_USER -d $POSTGRES_DB \
    -f /app/init.sql
else
  echo "Schema ya existe, omitiendo init.sql"
fi

echo "Creando superusuario si no existe..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@barbersaas.com', 'admin123')
    print('Superusuario creado: admin / admin123')
else:
    print('Superusuario ya existe')
"

echo "Servidor iniciando en http://localhost:8000"
echo "Swagger en http://localhost:8000/api/docs/"
exec python manage.py runserver 0.0.0.0:8000
