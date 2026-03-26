-- ============================================================
-- MediStock - Schema de Base de Datos
-- Archivo: database/schema.sql
-- Descripcion: Crea todas las tablas necesarias para el sistema
-- Ejecutar: python init_db.py  (o directamente en SQLite)
-- ============================================================

-- Eliminar tablas si ya existen (util para reiniciar en desarrollo)
DROP TABLE IF EXISTS auditoria;
DROP TABLE IF EXISTS dispensaciones;
DROP TABLE IF EXISTS lotes;
DROP TABLE IF EXISTS medicamentos;
DROP TABLE IF EXISTS usuarios;

-- ============================================================
-- TABLA: usuarios
-- Guarda los usuarios del sistema con su rol
-- Roles posibles: 'admin' o 'farmaceutico'
-- ============================================================
CREATE TABLE usuarios (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    NOT NULL UNIQUE,        -- nombre de usuario para login
    password    TEXT    NOT NULL,               -- contrasena encriptada (hash)
    nombre      TEXT    NOT NULL,               -- nombre completo del usuario
    rol         TEXT    NOT NULL CHECK(rol IN ('admin', 'farmaceutico')),
    activo      INTEGER NOT NULL DEFAULT 1      -- 1 = activo, 0 = desactivado
);

-- ============================================================
-- TABLA: medicamentos
-- Catalogo de medicamentos registrados en el sistema
-- tipo: 'controlado' requiere receta, 'libre' no requiere
-- ============================================================
CREATE TABLE medicamentos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT    NOT NULL UNIQUE,    -- nombre del medicamento
    descripcion     TEXT,                       -- descripcion opcional
    tipo            TEXT    NOT NULL CHECK(tipo IN ('controlado', 'libre')),
    unidad_medida   TEXT    NOT NULL DEFAULT 'piezas'  -- ej: piezas, mg, ml
);

-- ============================================================
-- TABLA: lotes
-- Cada lote es una entrada especifica de un medicamento
-- Un medicamento puede tener varios lotes con distintas
-- fechas de caducidad y cantidades
-- ============================================================
CREATE TABLE lotes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    medicamento_id   INTEGER NOT NULL,
    numero_lote      TEXT    NOT NULL,          -- numero de lote del fabricante
    cantidad         INTEGER NOT NULL CHECK(cantidad >= 0),  -- stock disponible
    fecha_caducidad  DATE    NOT NULL,          -- formato: YYYY-MM-DD
    fecha_entrada    DATE    NOT NULL DEFAULT (DATE('now')), -- cuando entro al sistema
    activo           INTEGER NOT NULL DEFAULT 1, -- 0 = vencido o agotado
    FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id)
);

-- ============================================================
-- TABLA: dispensaciones
-- Registra cada vez que se entrega un medicamento a un paciente
-- Esta tabla es el historial de salidas del inventario
-- ============================================================
CREATE TABLE dispensaciones (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    farmaceutico_id INTEGER NOT NULL,           -- quien despacho
    paciente_nombre TEXT    NOT NULL,           -- nombre del paciente
    medicamento_id  INTEGER NOT NULL,
    lote_id         INTEGER NOT NULL,           -- que lote se uso (FIFO)
    cantidad        INTEGER NOT NULL CHECK(cantidad > 0),
    numero_receta   TEXT,                       -- obligatorio si es controlado
    fecha_hora      DATETIME NOT NULL DEFAULT (DATETIME('now')),
    FOREIGN KEY (farmaceutico_id) REFERENCES usuarios(id),
    FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id),
    FOREIGN KEY (lote_id) REFERENCES lotes(id)
);

-- ============================================================
-- TABLA: auditoria
-- Registro INMUTABLE de todas las acciones del sistema
-- IMPORTANTE: esta tabla solo acepta INSERT, nunca UPDATE/DELETE
-- Guarda absolutamente todo: entradas, salidas, logins, errores
-- ============================================================
CREATE TABLE auditoria (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id   INTEGER,                       -- quien hizo la accion
    tipo_accion  TEXT    NOT NULL,              -- 'ENTRADA', 'SALIDA', 'LOGIN', 'ERROR'
    descripcion  TEXT    NOT NULL,              -- descripcion detallada de lo que paso
    medicamento_id INTEGER,                     -- medicamento involucrado (si aplica)
    lote_id      INTEGER,                       -- lote involucrado (si aplica)
    cantidad     INTEGER,                       -- cantidad movida (si aplica)
    paciente     TEXT,                          -- paciente (si aplica)
    fecha_hora   DATETIME NOT NULL DEFAULT (DATETIME('now')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- ============================================================
-- DATOS INICIALES
-- Insertar un usuario administrador por defecto para poder
-- entrar al sistema la primera vez
-- usuario: admin | contrasena: admin123
-- (la contrasena se reemplaza por el hash en init_db.py)
-- ============================================================
INSERT INTO usuarios (username, password, nombre, rol)
VALUES ('admin', 'HASH_AQUI', 'Administrador del Sistema', 'admin');

-- Medicamento de ejemplo para probar el sistema
INSERT INTO medicamentos (nombre, descripcion, tipo, unidad_medida)
VALUES 
    ('Paracetamol 500mg', 'Analgesico y antipiretico', 'libre', 'piezas'),
    ('Morfina 10mg', 'Analgesico opioide de uso controlado', 'controlado', 'ampolletas'),
    ('Amoxicilina 500mg', 'Antibiotico de amplio espectro', 'libre', 'capsulas');

INSERT INTO usuarios (username, password, nombre, rol)
VALUES ('farmaceutico', 'HASH_AQUI', 'Farmaceutico de Prueba', 'farmaceutico');