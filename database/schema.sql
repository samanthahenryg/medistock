-- ============================================================
-- MediStock - Schema de Base de Datos
-- Archivo: database/schema.sql
-- ============================================================

DROP TABLE IF EXISTS auditoria;
DROP TABLE IF EXISTS dispensaciones;
DROP TABLE IF EXISTS lotes;
DROP TABLE IF EXISTS medicamentos;
DROP TABLE IF EXISTS usuarios;

-- ============================================================
-- TABLA: usuarios
-- ============================================================
CREATE TABLE usuarios (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    NOT NULL UNIQUE,
    password    TEXT    NOT NULL,
    nombre      TEXT    NOT NULL,
    rol         TEXT    NOT NULL CHECK(rol IN ('admin', 'farmaceutico')),
    activo      INTEGER NOT NULL DEFAULT 1
);

-- ============================================================
-- TABLA: medicamentos
-- ============================================================
CREATE TABLE medicamentos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT    NOT NULL UNIQUE,
    descripcion     TEXT,
    tipo            TEXT    NOT NULL CHECK(tipo IN ('controlado', 'libre')),
    unidad_medida   TEXT    NOT NULL DEFAULT 'piezas'
);

-- ============================================================
-- TABLA: lotes
-- ============================================================
CREATE TABLE lotes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    medicamento_id   INTEGER NOT NULL,
    numero_lote      TEXT    NOT NULL,
    cantidad         INTEGER NOT NULL CHECK(cantidad >= 0),
    fecha_caducidad  DATE    NOT NULL,
    fecha_entrada    DATE    NOT NULL DEFAULT (DATE('now')),
    activo           INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id)
);

-- ============================================================
-- TABLA: dispensaciones
-- ============================================================
CREATE TABLE dispensaciones (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    farmaceutico_id INTEGER NOT NULL,
    paciente_nombre TEXT    NOT NULL,
    medicamento_id  INTEGER NOT NULL,
    lote_id         INTEGER NOT NULL,
    cantidad        INTEGER NOT NULL CHECK(cantidad > 0),
    numero_receta   TEXT,
    fecha_hora      DATETIME NOT NULL DEFAULT (DATETIME('now')),
    FOREIGN KEY (farmaceutico_id) REFERENCES usuarios(id),
    FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id),
    FOREIGN KEY (lote_id) REFERENCES lotes(id)
);

-- ============================================================
-- TABLA: auditoria
-- ============================================================
CREATE TABLE auditoria (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id   INTEGER,
    tipo_accion  TEXT    NOT NULL,
    descripcion  TEXT    NOT NULL,
    medicamento_id INTEGER,
    lote_id      INTEGER,
    cantidad     INTEGER,
    paciente     TEXT,
    fecha_hora   DATETIME NOT NULL DEFAULT (DATETIME('now')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- ============================================================
-- USUARIOS (passwords se actualizan con --init)
-- ============================================================
INSERT INTO usuarios (username, password, nombre, rol)
VALUES ('admin', 'HASH_AQUI', 'Administrador del Sistema', 'admin');

INSERT INTO usuarios (username, password, nombre, rol)
VALUES ('farmaceutico', 'HASH_AQUI', 'Farmacéutico de Prueba', 'farmaceutico');

-- ============================================================
-- MEDICAMENTOS DE PRUEBA
-- ============================================================
INSERT INTO medicamentos (nombre, descripcion, tipo, unidad_medida) VALUES
    ('Paracetamol 500mg',  'Analgésico y antipirético de uso común',        'libre',      'piezas'),
    ('Morfina 10mg',       'Analgésico opioide de uso controlado',           'controlado', 'ampolletas'),
    ('Amoxicilina 500mg',  'Antibiótico de amplio espectro',                 'libre',      'cápsulas'),
    ('Ibuprofeno 400mg',   'Antiinflamatorio no esteroideo',                 'libre',      'piezas'),
    ('Metformina 850mg',   'Hipoglucemiante oral para diabetes tipo 2',      'libre',      'tabletas'),
    ('Diazepam 5mg',       'Benzodiacepina de uso controlado',               'controlado', 'tabletas');

-- ============================================================
-- LOTES CON FECHAS VARIADAS PARA LA DEMO
-- Semáforo: rojo (<=30 días), amarillo (31-60), verde (61-90), vencido (<hoy)
-- ============================================================

-- Paracetamol: 1 lote vencido, 1 rojo, 1 amarillo, 1 verde
INSERT INTO lotes (medicamento_id, numero_lote, cantidad, fecha_caducidad, fecha_entrada) VALUES
    (1, 'PAR-2024-001',  0,   DATE('now', '-10 days'),  DATE('now', '-200 days')),  -- vencido/agotado
    (1, 'PAR-2025-002',  45,  DATE('now', '+15 days'),  DATE('now', '-30 days')),   -- ROJO
    (1, 'PAR-2025-003',  120, DATE('now', '+45 days'),  DATE('now', '-10 days')),   -- AMARILLO
    (1, 'PAR-2026-004',  200, DATE('now', '+80 days'),  DATE('now', '-5 days'));     -- VERDE

-- Morfina: 1 rojo, 1 amarillo
INSERT INTO lotes (medicamento_id, numero_lote, cantidad, fecha_caducidad, fecha_entrada) VALUES
    (2, 'MOR-2025-001',  8,   DATE('now', '+20 days'),  DATE('now', '-60 days')),   -- ROJO
    (2, 'MOR-2025-002',  15,  DATE('now', '+55 days'),  DATE('now', '-20 days'));    -- AMARILLO

-- Amoxicilina: 1 vencido con stock (para mostrar en alertas), 1 verde
INSERT INTO lotes (medicamento_id, numero_lote, cantidad, fecha_caducidad, fecha_entrada) VALUES
    (3, 'AMO-2024-001',  30,  DATE('now', '-5 days'),   DATE('now', '-180 days')),  -- VENCIDO con stock
    (3, 'AMO-2026-001',  90,  DATE('now', '+75 days'),  DATE('now', '-2 days'));     -- VERDE

-- Ibuprofeno: 1 amarillo, 1 lejos de vencer
INSERT INTO lotes (medicamento_id, numero_lote, cantidad, fecha_caducidad, fecha_entrada) VALUES
    (4, 'IBU-2025-001',  60,  DATE('now', '+50 days'),  DATE('now', '-15 days')),   -- AMARILLO
    (4, 'IBU-2026-001',  150, DATE('now', '+200 days'), DATE('now', '-3 days'));     -- OK

-- Metformina: 1 rojo
INSERT INTO lotes (medicamento_id, numero_lote, cantidad, fecha_caducidad, fecha_entrada) VALUES
    (5, 'MET-2025-001',  25,  DATE('now', '+10 days'),  DATE('now', '-90 days'));    -- ROJO

-- Diazepam: 1 verde
INSERT INTO lotes (medicamento_id, numero_lote, cantidad, fecha_caducidad, fecha_entrada) VALUES
    (6, 'DIA-2026-001',  20,  DATE('now', '+70 days'),  DATE('now', '-7 days'));     -- VERDE

-- Marcar lote vencido/agotado como inactivo
UPDATE lotes SET activo = 0 WHERE numero_lote = 'PAR-2024-001';

-- ============================================================
-- DISPENSACIONES DE EJEMPLO (historial para reportes)
-- ============================================================
INSERT INTO dispensaciones (farmaceutico_id, paciente_nombre, medicamento_id, lote_id, cantidad, numero_receta, fecha_hora) VALUES
    (2, 'Juan García López',      1, 2,  10, NULL,          DATETIME('now', '-5 days')),
    (2, 'María Torres Ruiz',      3, 7,   6, NULL,          DATETIME('now', '-4 days')),
    (1, 'Carlos Mendoza Pérez',   2, 5,   2, 'REC-2026-001', DATETIME('now', '-3 days')),
    (2, 'Ana Flores Sánchez',     4, 9,  20, NULL,          DATETIME('now', '-2 days')),
    (2, 'Roberto Díaz Herrera',   1, 3,  30, NULL,          DATETIME('now', '-1 days')),
    (1, 'Laura Vega Morales',     6, 12,  1, 'REC-2026-002', DATETIME('now', '-1 days')),
    (2, 'Pedro Ramírez Cruz',     5, 11,  5, NULL,          DATETIME('now'));

-- ============================================================
-- AUDITORIA INICIAL DE EJEMPLO
-- ============================================================
INSERT INTO auditoria (usuario_id, tipo_accion, descripcion, medicamento_id, lote_id, cantidad, paciente, fecha_hora) VALUES
    (1, 'LOGIN',   'Usuario admin inició sesión exitosamente.',                                                          NULL, NULL, NULL, NULL,                   DATETIME('now', '-6 days')),
    (1, 'ENTRADA', 'Entrada de 200 unidades de Paracetamol 500mg, lote PAR-2026-004, vence en 80 días.',               1,    4,    200,  NULL,                   DATETIME('now', '-5 days')),
    (2, 'LOGIN',   'Usuario farmaceutico inició sesión exitosamente.',                                                   NULL, NULL, NULL, NULL,                   DATETIME('now', '-5 days')),
    (2, 'SALIDA',  'Dispensación de 10 unidades de Paracetamol 500mg, lote PAR-2025-002, a paciente Juan García.',     1,    2,    10,   'Juan García López',    DATETIME('now', '-5 days')),
    (2, 'SALIDA',  'Dispensación de 6 unidades de Amoxicilina 500mg, lote AMO-2024-001, a paciente María Torres.',     3,    7,    6,    'María Torres Ruiz',    DATETIME('now', '-4 days')),
    (1, 'SALIDA',  'Dispensación de 2 ampolletas de Morfina 10mg, lote MOR-2025-001, a paciente Carlos Mendoza.',      2,    5,    2,    'Carlos Mendoza Pérez', DATETIME('now', '-3 days')),
    (2, 'LOGOUT',  'Farmacéutico de Prueba cerró sesión.',                                                               NULL, NULL, NULL, NULL,                   DATETIME('now', '-2 days')),
    (1, 'LOGOUT',  'Administrador del Sistema cerró sesión.',                                                            NULL, NULL, NULL, NULL,                   DATETIME('now', '-1 days'));
