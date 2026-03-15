-- ============================================
-- Schema COMPLETO Y FINAL - Sistema de Barbería
-- PostgreSQL 14+
-- ============================================
-- 
-- CONTEXTO: Este schema incluye TODAS las tablas necesarias para:
-- - Módulos Públicos: Equipo, Servicios, Galería, Agendamiento
-- - Módulos Admin: Dashboard, Finanzas, Reportes, Agenda, Clientes, 
--   Servicios, Equipo (CRUD), Configuraciones
--
-- Total de Tablas: 23
-- Última Actualización: 2024
-- ============================================

-- ============================================
-- PASO 1: ELIMINACIÓN DE TABLAS
-- (Orden correcto por dependencias)
-- ============================================

DROP TABLE IF EXISTS barber_ratings CASCADE;
DROP TABLE IF EXISTS service_barbers CASCADE;
DROP TABLE IF EXISTS barber_specialties CASCADE;
DROP TABLE IF EXISTS appointments_services CASCADE;
DROP TABLE IF EXISTS financial_transactions CASCADE;
DROP TABLE IF EXISTS category_transactions CASCADE;
DROP TABLE IF EXISTS type_transactions CASCADE;
DROP TABLE IF EXISTS appointments CASCADE;
DROP TABLE IF EXISTS status_appointments CASCADE;
DROP TABLE IF EXISTS gallery CASCADE;
DROP TABLE IF EXISTS gallery_categories CASCADE;
DROP TABLE IF EXISTS holidays CASCADE;
DROP TABLE IF EXISTS business_hours CASCADE;
DROP TABLE IF EXISTS notification_settings CASCADE;
DROP TABLE IF EXISTS business_settings CASCADE;
DROP TABLE IF EXISTS clients CASCADE;
DROP TABLE IF EXISTS services CASCADE;
DROP TABLE IF EXISTS type_services CASCADE;
DROP TABLE IF EXISTS specialties CASCADE;
DROP TABLE IF EXISTS barber_status CASCADE;
DROP TABLE IF EXISTS barbers CASCADE;

-- ============================================
-- PASO 2: CREACIÓN DE TABLAS DE CATÁLOGOS
-- ============================================

-- ============================================
-- Tabla: barber_status (Estados de Barberos)
-- ============================================
CREATE TABLE barber_status (
    id SERIAL,
    name VARCHAR(20) NOT NULL UNIQUE,
    color_code VARCHAR(7) NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_barber_status_id PRIMARY KEY(id),
    CONSTRAINT chk_status_color CHECK (color_code ~* '^#[0-9A-F]{6}$')
);

COMMENT ON TABLE barber_status IS 'Estados de barberos: Activo, Vacaciones, Inactivo';

-- ============================================
-- Tabla: specialties (Especialidades)
-- ============================================
CREATE TABLE specialties (
    id SERIAL,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_specialties_id PRIMARY KEY(id)
);

COMMENT ON TABLE specialties IS 'Catálogo de especialidades de barberos';

-- ============================================
-- Tabla: type_services (Tipos de Servicios)
-- ============================================
CREATE TABLE type_services (
    id SERIAL,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_type_services_id PRIMARY KEY(id)
);

COMMENT ON TABLE type_services IS 'Catálogo de tipos de servicios';

-- ============================================
-- Tabla: gallery_categories (Categorías de Galería)
-- ============================================
CREATE TABLE gallery_categories (
    id SERIAL,
    name VARCHAR(50) NOT NULL UNIQUE,
    slug VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_gallery_categories_id PRIMARY KEY(id)
);

COMMENT ON TABLE gallery_categories IS 'Catálogo de categorías para la galería';

-- ============================================
-- Tabla: status_appointments (Estados de Citas)
-- ============================================
CREATE TABLE status_appointments (
    id SERIAL,
    name VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_status_appointments_id PRIMARY KEY(id)
);

COMMENT ON TABLE status_appointments IS 'Catálogo de estados de citas';

-- ============================================
-- Tabla: type_transactions (Tipos de Transacciones)
-- ============================================
CREATE TABLE type_transactions (
    id SERIAL,
    name VARCHAR(30) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_type_transactions_id PRIMARY KEY(id)
);

COMMENT ON TABLE type_transactions IS 'Tipos de transacciones financieras';

-- ============================================
-- Tabla: category_transactions (Categorías de Transacciones)
-- ============================================
CREATE TABLE category_transactions (
    id SERIAL,
    name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_category_transactions_id PRIMARY KEY(id)
);

COMMENT ON TABLE category_transactions IS 'Categorías de transacciones financieras';

-- ============================================
-- PASO 3: CREACIÓN DE TABLAS PRINCIPALES
-- ============================================

-- ============================================
-- Tabla: barbers (Barberos)
-- ============================================
CREATE TABLE barbers (
    id SERIAL,
    name VARCHAR(100) NOT NULL,
    nickname VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) NOT NULL,
    description TEXT,
    avatar TEXT,
    color_code VARCHAR(7) NOT NULL,
    status_id INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_barbers_id PRIMARY KEY(id),
    CONSTRAINT fk_barber_status FOREIGN KEY (status_id) 
        REFERENCES barber_status(id) ON DELETE RESTRICT,
    CONSTRAINT chk_color_code CHECK (color_code ~* '^#[0-9A-F]{6}$')
);

COMMENT ON TABLE barbers IS 'Barberos del negocio';
COMMENT ON COLUMN barbers.status_id IS 'Estado: 1=Activo, 2=Vacaciones, 3=Inactivo';
COMMENT ON COLUMN barbers.avatar IS 'URL de Cloudinary (500x500px, PNG/JPG)';

-- ============================================
-- Tabla: services (Servicios)
-- ============================================
CREATE TABLE services (
    id SERIAL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    short_description VARCHAR(200),
    price DECIMAL(10,2) NOT NULL,
    duration INTEGER NOT NULL,
    image_url TEXT,
    service_type_id INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_services_id PRIMARY KEY(id),
    CONSTRAINT fk_service_type FOREIGN KEY (service_type_id) 
        REFERENCES type_services(id) ON DELETE SET NULL,
    CONSTRAINT chk_duration CHECK (duration > 0),
    CONSTRAINT chk_price CHECK (price >= 0)
);

COMMENT ON TABLE services IS 'Servicios ofrecidos';
COMMENT ON COLUMN services.short_description IS 'Descripción corta para vista pública (max 200 chars)';
COMMENT ON COLUMN services.image_url IS 'URL de Cloudinary';

-- ============================================
-- Tabla: clients (Clientes)
-- ============================================
CREATE TABLE clients (
    id SERIAL,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_clients_id PRIMARY KEY(id),
    CONSTRAINT uk_clients_phone UNIQUE(phone),
    CONSTRAINT uk_clients_email UNIQUE(email)
);

COMMENT ON TABLE clients IS 'Clientes del negocio';
COMMENT ON COLUMN clients.notes IS 'Notas internas (solo visible para admin)';

-- ============================================
-- Tabla: appointments (Citas)
-- ============================================
CREATE TABLE appointments (
    id SERIAL,
    barber_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    status_id INTEGER NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    notes TEXT,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    total_duration INTEGER NOT NULL DEFAULT 0,
    confirmation_code VARCHAR(10) UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_appointments_id PRIMARY KEY(id),
    CONSTRAINT fk_appointments_barber FOREIGN KEY (barber_id) 
        REFERENCES barbers(id) ON DELETE RESTRICT,
    CONSTRAINT fk_appointments_client FOREIGN KEY (client_id) 
        REFERENCES clients(id) ON DELETE RESTRICT,
    CONSTRAINT fk_appointments_status FOREIGN KEY (status_id) 
        REFERENCES status_appointments(id) ON DELETE RESTRICT,
    CONSTRAINT uk_barber_datetime UNIQUE (barber_id, date, time)
);

COMMENT ON TABLE appointments IS 'Citas agendadas';
COMMENT ON COLUMN appointments.total_amount IS 'Suma de precios de servicios';
COMMENT ON COLUMN appointments.total_duration IS 'Suma de duraciones de servicios (minutos)';
COMMENT ON COLUMN appointments.confirmation_code IS 'Código único para consultar cita pública';

-- ============================================
-- Tabla: gallery (Galería)
-- ============================================
CREATE TABLE gallery (
    id SERIAL,
    title VARCHAR(100),
    image_url TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    barber_id INTEGER,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_gallery_id PRIMARY KEY(id),
    CONSTRAINT fk_gallery_category FOREIGN KEY (category_id) 
        REFERENCES gallery_categories(id) ON DELETE RESTRICT,
    CONSTRAINT fk_gallery_barber FOREIGN KEY (barber_id) 
        REFERENCES barbers(id) ON DELETE SET NULL
);

COMMENT ON TABLE gallery IS 'Galería de trabajos realizados';
COMMENT ON COLUMN gallery.image_url IS 'URL de Cloudinary';

-- ============================================
-- Tabla: financial_transactions (Transacciones Financieras)
-- ============================================
CREATE TABLE financial_transactions (
    id SERIAL,
    type_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    appointment_id INTEGER,
    concept VARCHAR(200) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_financial_transactions_id PRIMARY KEY(id),
    CONSTRAINT fk_transactions_appointment FOREIGN KEY (appointment_id) 
        REFERENCES appointments(id) ON DELETE SET NULL,
    CONSTRAINT fk_transactions_type FOREIGN KEY (type_id) 
        REFERENCES type_transactions(id) ON DELETE RESTRICT,
    CONSTRAINT fk_transactions_category FOREIGN KEY (category_id) 
        REFERENCES category_transactions(id) ON DELETE RESTRICT,
    CONSTRAINT chk_amount_not_zero CHECK (amount != 0)
);

COMMENT ON TABLE financial_transactions IS 'Transacciones financieras (ingresos y egresos)';
COMMENT ON COLUMN financial_transactions.amount IS 'Positivo para ingresos, negativo para egresos';

-- ============================================
-- Tabla: business_settings (Configuración del Negocio)
-- ============================================
CREATE TABLE business_settings (
    id INTEGER DEFAULT 1,
    
    -- Información General
    business_name VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    logo_url TEXT,
    facebook_url VARCHAR(255),
    instagram_url VARCHAR(255),
    tiktok_url VARCHAR(255),
    
    -- Configuración de Citas (Deprecated - usar business_hours)
    opening_time TIME,
    closing_time TIME,
    time_slot_duration INTEGER NOT NULL DEFAULT 30,
    
    -- Reglas de Reservas
    booking_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    max_days_advance INTEGER DEFAULT 30,
    min_hours_before INTEGER DEFAULT 2,
    allow_cancellations BOOLEAN NOT NULL DEFAULT TRUE,
    cancellation_hours_before INTEGER DEFAULT 24,
    require_deposit BOOLEAN NOT NULL DEFAULT FALSE,
    deposit_amount DECIMAL(10,2) DEFAULT 0,
    
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_business_settings_id PRIMARY KEY(id),
    CONSTRAINT single_row CHECK (id = 1)
);

COMMENT ON TABLE business_settings IS 'Configuración general del negocio (solo 1 registro)';
COMMENT ON COLUMN business_settings.opening_time IS 'DEPRECATED - usar business_hours';
COMMENT ON COLUMN business_settings.closing_time IS 'DEPRECATED - usar business_hours';
COMMENT ON COLUMN business_settings.logo_url IS 'URL de Cloudinary';

-- ============================================
-- Tabla: business_hours (Horarios por Día)
-- ============================================
CREATE TABLE business_hours (
    id SERIAL,
    day_of_week INTEGER NOT NULL,
    is_working BOOLEAN NOT NULL DEFAULT TRUE,
    opening_time TIME,
    closing_time TIME,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_business_hours_id PRIMARY KEY(id),
    CONSTRAINT uk_day_of_week UNIQUE (day_of_week),
    CONSTRAINT chk_day_range CHECK (day_of_week >= 0 AND day_of_week <= 6)
);

COMMENT ON TABLE business_hours IS 'Horarios de operación por día de la semana';
COMMENT ON COLUMN business_hours.day_of_week IS '0=Domingo, 1=Lunes, 2=Martes, ..., 6=Sábado';

-- ============================================
-- Tabla: holidays (Días Feriados/Excepciones)
-- ============================================
CREATE TABLE holidays (
    id SERIAL,
    date DATE NOT NULL UNIQUE,
    reason VARCHAR(200) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_holidays_id PRIMARY KEY(id)
);

COMMENT ON TABLE holidays IS 'Días feriados o excepciones (no se trabaja)';

-- ============================================
-- Tabla: notification_settings (Configuración de Notificaciones)
-- ============================================
CREATE TABLE notification_settings (
    id INTEGER DEFAULT 1,
    sms_reminder_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    sms_hours_before INTEGER DEFAULT 24,
    email_promotions_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    whatsapp_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    whatsapp_number VARCHAR(20),
    whatsapp_connected BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_notification_settings_id PRIMARY KEY(id),
    CONSTRAINT single_row CHECK (id = 1)
);

COMMENT ON TABLE notification_settings IS 'Configuración de notificaciones automáticas';

-- ============================================
-- PASO 4: TABLAS INTERMEDIAS (Muchos a Muchos)
-- ============================================

-- ============================================
-- Tabla: barber_specialties (Barberos ↔ Especialidades)
-- ============================================
CREATE TABLE barber_specialties (
    id SERIAL,
    barber_id INTEGER NOT NULL,
    specialty_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_barber_specialties_id PRIMARY KEY(id),
    CONSTRAINT fk_barber_specialty_barber FOREIGN KEY (barber_id) 
        REFERENCES barbers(id) ON DELETE CASCADE,
    CONSTRAINT fk_barber_specialty_specialty FOREIGN KEY (specialty_id) 
        REFERENCES specialties(id) ON DELETE CASCADE,
    CONSTRAINT uk_barber_specialty UNIQUE (barber_id, specialty_id)
);

COMMENT ON TABLE barber_specialties IS 'Relación muchos a muchos: barberos y sus especialidades';

-- ============================================
-- Tabla: service_barbers (Servicios ↔ Barberos)
-- ============================================
CREATE TABLE service_barbers (
    id SERIAL,
    service_id INTEGER NOT NULL,
    barber_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_service_barbers_id PRIMARY KEY(id),
    CONSTRAINT fk_service_barbers_service FOREIGN KEY (service_id) 
        REFERENCES services(id) ON DELETE CASCADE,
    CONSTRAINT fk_service_barbers_barber FOREIGN KEY (barber_id) 
        REFERENCES barbers(id) ON DELETE CASCADE,
    CONSTRAINT uk_service_barber UNIQUE (service_id, barber_id)
);

COMMENT ON TABLE service_barbers IS 'Relación muchos a muchos: servicios y barberos que los realizan';

-- ============================================
-- Tabla: appointments_services (Servicios de la Cita)
-- ============================================
CREATE TABLE appointments_services (
    id SERIAL,
    appointment_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    price_snapshot DECIMAL(10,2) NOT NULL,
    duration_snapshot INTEGER NOT NULL,
    
    CONSTRAINT pk_appointments_services_id PRIMARY KEY(id),
    CONSTRAINT fk_appointment_service_appointment FOREIGN KEY (appointment_id) 
        REFERENCES appointments(id) ON DELETE CASCADE,
    CONSTRAINT fk_appointment_service_service FOREIGN KEY (service_id) 
        REFERENCES services(id) ON DELETE RESTRICT,
    CONSTRAINT chk_positive_price CHECK (price_snapshot >= 0),
    CONSTRAINT chk_positive_duration CHECK (duration_snapshot > 0)
);

COMMENT ON TABLE appointments_services IS 'Servicios incluidos en cada cita con snapshot de precios';
COMMENT ON COLUMN appointments_services.price_snapshot IS 'Precio del servicio al momento de la cita';
COMMENT ON COLUMN appointments_services.duration_snapshot IS 'Duración del servicio al momento de la cita';

-- ============================================
-- PASO 5: TABLA FUTURA
-- ============================================

-- ============================================
-- Tabla: barber_ratings (Calificaciones - FUTURO)
-- ============================================
CREATE TABLE barber_ratings (
    id SERIAL,
    barber_id INTEGER NOT NULL,
    appointment_id INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT pk_barber_ratings_id PRIMARY KEY(id),
    CONSTRAINT fk_rating_barber FOREIGN KEY (barber_id) 
        REFERENCES barbers(id) ON DELETE CASCADE,
    CONSTRAINT fk_rating_appointment FOREIGN KEY (appointment_id) 
        REFERENCES appointments(id) ON DELETE CASCADE,
    CONSTRAINT chk_rating_value CHECK (rating >= 1 AND rating <= 5),
    CONSTRAINT uk_rating_appointment UNIQUE (appointment_id)
);

COMMENT ON TABLE barber_ratings IS 'Calificaciones de barberos por clientes (funcionalidad futura v2.0)';

-- ============================================
-- PASO 6: ÍNDICES
-- ============================================

-- Barber Status
CREATE INDEX idx_barber_status_name ON barber_status(name);

-- Specialties
CREATE INDEX idx_specialties_name ON specialties(name);

-- Type Services
CREATE INDEX idx_type_services_name ON type_services(name);
CREATE INDEX idx_type_services_order ON type_services(display_order);

-- Gallery Categories
CREATE INDEX idx_gallery_categories_slug ON gallery_categories(slug);
CREATE INDEX idx_gallery_categories_order ON gallery_categories(display_order);

-- Barbers
CREATE INDEX idx_barbers_status ON barbers(status_id);
CREATE INDEX idx_barbers_name ON barbers(name);
CREATE INDEX idx_barbers_email ON barbers(email) WHERE email IS NOT NULL;
CREATE INDEX idx_barbers_nickname ON barbers(nickname);

-- Services
CREATE INDEX idx_services_active ON services(is_active) WHERE is_active = true;
CREATE INDEX idx_services_price ON services(price);
CREATE INDEX idx_services_type ON services(service_type_id);
CREATE INDEX idx_services_name ON services(name);

-- Clients
CREATE INDEX idx_clients_phone ON clients(phone);
CREATE INDEX idx_clients_email ON clients(email) WHERE email IS NOT NULL;
CREATE INDEX idx_clients_name ON clients(full_name);

-- Appointments
CREATE INDEX idx_appointments_barber ON appointments(barber_id);
CREATE INDEX idx_appointments_client ON appointments(client_id);
CREATE INDEX idx_appointments_status ON appointments(status_id);
CREATE INDEX idx_appointments_date ON appointments(date);
CREATE INDEX idx_appointments_date_time ON appointments(date, time);
CREATE INDEX idx_appointments_confirmation ON appointments(confirmation_code) 
    WHERE confirmation_code IS NOT NULL;

-- Gallery
CREATE INDEX idx_gallery_category ON gallery(category_id);
CREATE INDEX idx_gallery_active ON gallery(is_active) WHERE is_active = true;
CREATE INDEX idx_gallery_barber ON gallery(barber_id) WHERE barber_id IS NOT NULL;
CREATE INDEX idx_gallery_order ON gallery(display_order);

-- Financial Transactions
CREATE INDEX idx_transactions_date ON financial_transactions(date);
CREATE INDEX idx_transactions_type ON financial_transactions(type_id);
CREATE INDEX idx_transactions_category ON financial_transactions(category_id);
CREATE INDEX idx_transactions_appointment ON financial_transactions(appointment_id) 
    WHERE appointment_id IS NOT NULL;

-- Business Hours
CREATE INDEX idx_business_hours_day ON business_hours(day_of_week);
CREATE INDEX idx_business_hours_working ON business_hours(is_working) 
    WHERE is_working = TRUE;

-- Holidays
CREATE INDEX idx_holidays_date ON holidays(date);

-- Barber Specialties
CREATE INDEX idx_barber_specialties_barber ON barber_specialties(barber_id);
CREATE INDEX idx_barber_specialties_specialty ON barber_specialties(specialty_id);

-- Service Barbers
CREATE INDEX idx_service_barbers_service ON service_barbers(service_id);
CREATE INDEX idx_service_barbers_barber ON service_barbers(barber_id);

-- Appointments Services
CREATE INDEX idx_appointments_services_appointment ON appointments_services(appointment_id);
CREATE INDEX idx_appointments_services_service ON appointments_services(service_id);

-- Barber Ratings
CREATE INDEX idx_ratings_barber ON barber_ratings(barber_id);

-- ============================================
-- PASO 7: FUNCIÓN PARA ACTUALIZAR updated_at
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- PASO 8: TRIGGERS PARA updated_at
-- ============================================

CREATE TRIGGER trg_barbers_updated_at
    BEFORE UPDATE ON barbers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_services_updated_at
    BEFORE UPDATE ON services
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_appointments_updated_at
    BEFORE UPDATE ON appointments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_financial_transactions_updated_at
    BEFORE UPDATE ON financial_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_business_settings_updated_at
    BEFORE UPDATE ON business_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_business_hours_updated_at
    BEFORE UPDATE ON business_hours
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_notification_settings_updated_at
    BEFORE UPDATE ON notification_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- PASO 9: DATOS INICIALES
-- ============================================

-- Estados de Barberos
INSERT INTO barber_status (name, color_code, description) VALUES
    ('Activo', '#10b981', 'Trabajando normalmente'),
    ('Vacaciones', '#f59e0b', 'En descanso temporal'),
    ('Inactivo', '#ef4444', 'No está trabajando actualmente');

-- Especialidades comunes
INSERT INTO specialties (name, description) VALUES
    ('Esculpido de Barba', 'Experto en diseño y mantenimiento de barbas'),
    ('Navaja Libre', 'Maestro en el uso de navaja tradicional'),
    ('Cortes Clásicos', 'Especialista en cortes tradicionales'),
    ('Fades y Degradados', 'Experto en técnicas modernas de degradado'),
    ('Diseños y Figuras', 'Creación de diseños artísticos en cabello'),
    ('Cortes Infantiles', 'Especialista en cortes para niños'),
    ('Afeitado Tradicional', 'Afeitado con navaja y toalla caliente');

-- Tipos de servicios
INSERT INTO type_services (name, description, display_order) VALUES
    ('Corte', 'Servicios de corte de cabello', 1),
    ('Barba', 'Servicios de barba y bigote', 2),
    ('Tratamiento', 'Tratamientos capilares y faciales', 3),
    ('Combo', 'Paquetes combinados de servicios', 4),
    ('Especial', 'Servicios especiales y únicos', 5);

-- Categorías de galería
INSERT INTO gallery_categories (name, slug, description, display_order) VALUES
    ('Todos', 'todos', 'Todos los trabajos', 1),
    ('Fades y Degradados', 'fades', 'Cortes con técnica de degradado', 2),
    ('Cortes Clásicos', 'cortes_clasicos', 'Cortes tradicionales y elegantes', 3),
    ('Barbas y Perfilados', 'barbas', 'Trabajo de barba y perfilado', 4);

-- Estados de citas
INSERT INTO status_appointments (name) VALUES 
    ('Pendiente'),
    ('Confirmada'),
    ('En progreso'),
    ('Completada'),
    ('Cancelada'),
    ('No asistió');

-- Tipos de transacciones
INSERT INTO type_transactions (name) VALUES 
    ('Ingreso'),
    ('Egreso');

-- Categorías de transacciones
INSERT INTO category_transactions (name) VALUES 
    ('Servicio'),
    ('Propina'),
    ('Producto'),
    ('Salario'),
    ('Renta'),
    ('Servicios básicos'),
    ('Insumos'),
    ('Mantenimiento'),
    ('Otro');

-- Configuración inicial del negocio
INSERT INTO business_settings (
    business_name, 
    address, 
    phone, 
    email,
    opening_time,
    closing_time,
    time_slot_duration,
    booking_enabled,
    max_days_advance,
    min_hours_before,
    allow_cancellations,
    cancellation_hours_before,
    require_deposit,
    deposit_amount
) VALUES (
    'Mi Barbería', 
    'Calle Principal #123, Centro', 
    '555-0000', 
    'info@mibarberia.com',
    '09:00:00',
    '19:00:00',
    30,
    TRUE,
    30,
    2,
    TRUE,
    24,
    FALSE,
    0
);

-- Horarios por día (Lun-Sáb trabajando, Dom cerrado)
INSERT INTO business_hours (day_of_week, is_working, opening_time, closing_time) VALUES
    (0, FALSE, NULL, NULL),              -- Domingo (cerrado)
    (1, TRUE, '09:00:00', '19:00:00'),   -- Lunes
    (2, TRUE, '09:00:00', '19:00:00'),   -- Martes
    (3, TRUE, '09:00:00', '19:00:00'),   -- Miércoles
    (4, TRUE, '09:00:00', '19:00:00'),   -- Jueves
    (5, TRUE, '09:00:00', '19:00:00'),   -- Viernes
    (6, TRUE, '09:00:00', '20:00:00');   -- Sábado (horario extendido)

-- Días feriados (ejemplos)
INSERT INTO holidays (date, reason) VALUES
    ('2024-01-01', 'Año Nuevo'),
    ('2024-12-25', 'Navidad'),
    ('2024-12-24', 'Nochebuena');

-- Configuración de notificaciones
INSERT INTO notification_settings (
    sms_reminder_enabled,
    sms_hours_before,
    email_promotions_enabled,
    whatsapp_enabled,
    whatsapp_number,
    whatsapp_connected
) VALUES (
    FALSE,
    24,
    FALSE,
    FALSE,
    NULL,
    FALSE
);

-- ============================================
-- PASO 10: VERIFICACIÓN FINAL
-- ============================================

-- Verificar que todas las tablas fueron creadas
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE';
    
    RAISE NOTICE 'Total de tablas creadas: %', table_count;
    
    IF table_count = 23 THEN
        RAISE NOTICE '✅ Schema creado exitosamente - 23 tablas';
    ELSE
        RAISE WARNING '⚠️  Se esperaban 23 tablas, se encontraron: %', table_count;
    END IF;
END $$;
