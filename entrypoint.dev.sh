#!/bin/sh

echo "================================================"
echo " BarberSaaS API - Ambiente de Desarrollo"
echo "================================================"

echo "Aplicando migraciones..."
python manage.py migrate


echo "Ejecutando init.sql..."
PGPASSWORD=$POSTGRES_PASSWORD psql \
  -h db \
  -U $POSTGRES_USER \
  -d $POSTGRES_DB \
  -f /app/init.sql

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
