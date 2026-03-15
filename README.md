# BarberSaaS — Backend API REST

API REST para gestión de una barbería. Construida con Django + DRF, base de datos PostgreSQL, imágenes en Cloudinary y autenticación JWT.

---

## Stack

| Tecnología | Versión |
|---|---|
| Python | 3.11+ |
| Django | 6.0.2 |
| Django REST Framework | 3.14+ |
| PostgreSQL | 16 |
| JWT (simplejwt) | 5.3.1 |
| Cloudinary | 1.36.0 |
| drf-spectacular (Swagger) | 0.27.x |
| Gunicorn (prod) | — |

---

## Requisitos previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y corriendo
- Git

Nada más. No necesitas Python, PostgreSQL, ni nada instalado localmente.

---

## Inicio rápido (desarrollo con Docker)

```bash
# 1. Clonar el repositorio
git clone <URL_DEL_REPO>
cd BarberSaaS/backend

# 2. Levantar la API + base de datos
docker compose -f docker-compose.dev.yml up
```

Listo. La API levanta en **http://localhost:8000**

| URL | Descripción |
|---|---|
| http://localhost:8000/api/docs/ | Swagger UI — documentación interactiva |
| http://localhost:8000/api/redoc/ | ReDoc — documentación alternativa |
| http://localhost:8000/admin/ | Panel de administración Django |

**Credenciales del admin:**
```
usuario: admin
password: admin123
```

Para detener:
```bash
docker compose -f docker-compose.dev.yml down
```

---

## Variables de entorno

El archivo `.env.dev` ya viene en el repositorio y está configurado para desarrollo local con Docker. **No necesitas cambiarlo.**

Si quieres ver qué contiene:
```bash
cat .env.dev
```

---

## Estructura del proyecto

```
backend/
├── Dockerfile              # imagen producción (Gunicorn)
├── Dockerfile.dev          # imagen desarrollo (runserver + hot reload)
├── docker-compose.yml      # producción
├── docker-compose.dev.yml  # desarrollo ← el que usas tú
├── entrypoint.dev.sh       # script de inicio del contenedor
├── init.sql                # schema completo de PostgreSQL (23 tablas + datos iniciales)
├── .env.dev                # variables de entorno para desarrollo ✅ en el repo
├── .env.production         # variables de producción ❌ NO está en el repo
├── requirements.txt        # dependencias Python
├── manage.py
├── pytest.ini
├── barbersaas/             # configuración Django (settings, urls, wsgi)
├── apps/                   # 8 módulos de la aplicación
│   ├── authentication/     # login, logout, JWT
│   ├── barbers/            # barberos y especialidades
│   ├── services/           # servicios y tipos
│   ├── clients/            # clientes
│   ├── appointments/       # citas, disponibilidad, agenda
│   ├── gallery/            # galería de imágenes
│   ├── finance/            # transacciones financieras
│   └── core/               # dashboard, reportes, configuraciones
├── utils/                  # permisos, paginación, validadores
└── tests/                  # 126 tests (pytest)
```

---

## Base de datos

PostgreSQL con **23 tablas**. El schema se ejecuta automáticamente al primer `docker compose up` desde `init.sql`.

| Grupo | Tablas |
|---|---|
| Catálogos | `barber_status`, `specialties`, `type_services`, `gallery_categories`, `status_appointments`, `type_transactions`, `category_transactions` |
| Principales | `barbers`, `services`, `clients`, `appointments`, `gallery`, `financial_transactions`, `business_settings`, `notification_settings` |
| Configuración | `business_hours`, `holidays` |
| Intermedias M:N | `barber_specialties`, `service_barbers`, `appointments_services` |

**Datos iniciales incluidos:** estados de barberos, especialidades, tipos de servicio, categorías de galería, estados de citas, horarios Lun–Sáb 09:00–19:00 (Dom cerrado).

---

## Endpoints

### Autenticación

```
POST   /api/admin/auth/login/          # login → retorna access + refresh token
POST   /api/admin/auth/logout/         # invalida refresh token
GET    /api/admin/auth/me/             # perfil del usuario autenticado
POST   /api/admin/auth/refresh/        # renovar access token
```

**Login request:**
```json
POST /api/admin/auth/login/
{
  "username": "admin",
  "password": "admin123"
}
```

**Login response:**
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": { "id": 1, "username": "admin", "email": "..." }
}
```

Todos los endpoints `/api/admin/*` (excepto login) requieren el header:
```
Authorization: Bearer <access_token>
```

---

### Endpoints públicos (sin autenticación)

```
GET    /api/public/team/
GET    /api/public/team/{id}/
GET    /api/public/services/
GET    /api/public/services/{id}/
GET    /api/public/gallery/
GET    /api/public/gallery/{id}/
GET    /api/public/gallery/categories/
GET    /api/public/appointments/availability/?date=YYYY-MM-DD&service_ids=1,2&barber_id=1
POST   /api/public/appointments/book/
GET    /api/public/appointments/status/?code=ABC12345
```

---

### Admin — Barberos

```
GET    /api/admin/barbers/
GET    /api/admin/barbers/{id}/
POST   /api/admin/barbers/
PATCH  /api/admin/barbers/{id}/
DELETE /api/admin/barbers/{id}/
POST   /api/admin/barbers/{id}/upload-avatar/
GET    /api/admin/barbers/stats/
GET    /api/admin/barbers/specialties/
POST   /api/admin/barbers/specialties/
PATCH  /api/admin/barbers/specialties/{id}/
DELETE /api/admin/barbers/specialties/{id}/
```

---

### Admin — Servicios

```
GET    /api/admin/services/
GET    /api/admin/services/{id}/
POST   /api/admin/services/
PATCH  /api/admin/services/{id}/
DELETE /api/admin/services/{id}/
POST   /api/admin/services/{id}/upload-image/
GET    /api/admin/services/types/
POST   /api/admin/services/types/
PATCH  /api/admin/services/types/{id}/
DELETE /api/admin/services/types/{id}/
```

---

### Admin — Clientes

```
GET    /api/admin/clients/
GET    /api/admin/clients/{id}/
POST   /api/admin/clients/
PATCH  /api/admin/clients/{id}/
DELETE /api/admin/clients/{id}/
GET    /api/admin/clients/{id}/appointments/
```

---

### Admin — Galería

```
GET    /api/admin/gallery/images/
POST   /api/admin/gallery/images/
PATCH  /api/admin/gallery/images/{id}/
DELETE /api/admin/gallery/images/{id}/
POST   /api/admin/gallery/images/{id}/upload-image/
GET    /api/admin/gallery/categories/
POST   /api/admin/gallery/categories/
PATCH  /api/admin/gallery/categories/{id}/
DELETE /api/admin/gallery/categories/{id}/
```

---

### Admin — Dashboard

```
GET    /api/admin/dashboard/stats/
GET    /api/admin/dashboard/weekly-performance/
GET    /api/admin/dashboard/upcoming-appointments/?limit=4
```

---

### Admin — Finanzas

```
GET    /api/admin/finance/summary/
GET    /api/admin/finance/transactions/
POST   /api/admin/finance/transactions/
GET    /api/admin/finance/transactions/{id}/
PATCH  /api/admin/finance/transactions/{id}/
DELETE /api/admin/finance/transactions/{id}/
GET    /api/admin/finance/types/
POST   /api/admin/finance/types/
PATCH  /api/admin/finance/types/{id}/
DELETE /api/admin/finance/types/{id}/
GET    /api/admin/finance/categories/
POST   /api/admin/finance/categories/
PATCH  /api/admin/finance/categories/{id}/
DELETE /api/admin/finance/categories/{id}/
```

---

### Admin — Reportes

```
GET    /api/admin/reports/income-chart/?period=today|week|month|year
GET    /api/admin/reports/top-services/
GET    /api/admin/reports/top-barbers/
GET    /api/admin/reports/occupancy-heatmap/
```

---

### Admin — Agenda

```
GET    /api/admin/agenda/schedule/?date=YYYY-MM-DD
GET    /api/admin/agenda/appointments/{id}/
PATCH  /api/admin/agenda/appointments/{id}/change-status/
POST   /api/admin/agenda/quick-appointment/
```

---

### Admin — Configuraciones

```
GET    /api/admin/settings/business-info/
PATCH  /api/admin/settings/business-info/
POST   /api/admin/settings/upload-logo/
GET    /api/admin/settings/booking-rules/
PATCH  /api/admin/settings/booking-rules/
GET    /api/admin/settings/business-hours/
PUT    /api/admin/settings/business-hours/
PATCH  /api/admin/settings/business-hours/{day_of_week}/
GET    /api/admin/settings/holidays/
POST   /api/admin/settings/holidays/
DELETE /api/admin/settings/holidays/{id}/
GET    /api/admin/settings/notifications/
PATCH  /api/admin/settings/notifications/
```

---

## Agendar una cita (flujo completo)

**1. Consultar disponibilidad:**
```
GET /api/public/appointments/availability/
    ?date=2025-04-01
    &service_ids=1,2
    &barber_id=1         ← opcional
```

**2. Agendar:**
```json
POST /api/public/appointments/book/
{
  "client": {
    "full_name": "Juan Pérez",
    "phone": "555-1234",
    "email": "juan@email.com"
  },
  "date": "2025-04-01",
  "time": "10:00",
  "service_ids": [1, 2],
  "barber_id": 1,
  "notes": "Primera vez"
}
```

**Response:**
```json
{
  "success": true,
  "confirmation_code": "AB3XY789",
  "appointment": {
    "id": 42,
    "barber": "Carlos",
    "date": "2025-04-01",
    "time": "10:00",
    "services": ["Corte clásico", "Barba"],
    "total_amount": "250.00",
    "total_duration": 60
  }
}
```

**3. Consultar estado:**
```
GET /api/public/appointments/status/?code=AB3XY789
```

---

## Paginación

Los listados paginan por defecto con 10 items por página.

```
GET /api/admin/clients/?page=2&page_size=20
```

**Response:**
```json
{
  "count": 85,
  "next": "http://localhost:8000/api/admin/clients/?page=3",
  "previous": "http://localhost:8000/api/admin/clients/?page=1",
  "results": [ ... ]
}
```

---

## Tests

```bash
# Correr todos los tests
docker compose -f docker-compose.dev.yml exec api pytest

# Con cobertura
docker compose -f docker-compose.dev.yml exec api pytest --cov

# Un módulo específico
docker compose -f docker-compose.dev.yml exec api pytest tests/test_barbers.py -v
```

Cobertura actual: **85%** — 126 tests passing.

---

## Comandos útiles (dentro del contenedor)

```bash
# Abrir shell del contenedor
docker compose -f docker-compose.dev.yml exec api bash

# Crear superusuario
python manage.py createsuperuser

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Shell de Django
python manage.py shell

# Ver logs en tiempo real
docker compose -f docker-compose.dev.yml logs -f api
```

---

## Solución de problemas

**El contenedor no levanta / error de BD:**
```bash
# Bajar todo (incluyendo volúmenes) y volver a levantar
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up
```

**Puerto 8000 ocupado:**
```bash
# Verificar qué proceso usa el puerto
sudo lsof -i :8000
# O cambiar el puerto en docker-compose.dev.yml: "8001:8000"
```

**Error de permisos en entrypoint:**
```bash
git update-index --chmod=+x entrypoint.dev.sh
```

---

## CORS configurado para

```
http://localhost:5173   ← Vite (React)
http://localhost:3000   ← Create React App
```

Si tu frontend corre en otro puerto, abre un issue o edita `.env.dev`.