-- Esquema de base de datos - Sistema Web Control de Plagas en Plátano
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuario (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol           TEXT NOT NULL CHECK (rol IN ('campesino', 'profesional')),
    creado_en     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reporte (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id    INTEGER NOT NULL REFERENCES usuario(id),
    descripcion   TEXT NOT NULL,
    ubicacion     TEXT NOT NULL,
    tipo_plaga    TEXT,
    zona          TEXT,
    estado        TEXT NOT NULL DEFAULT 'Reportado'
                  CHECK (estado IN ('Reportado', 'En revisión', 'Diagnosticado', 'Resuelto')),
    creado_en     TEXT NOT NULL,
    actualizado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS foto (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    reporte_id     INTEGER NOT NULL REFERENCES reporte(id) ON DELETE CASCADE,
    nombre_archivo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS diagnostico (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    reporte_id     INTEGER NOT NULL UNIQUE REFERENCES reporte(id),
    profesional_id INTEGER NOT NULL REFERENCES usuario(id),
    texto          TEXT NOT NULL,
    recomendacion  TEXT NOT NULL,
    creado_en      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notificacion (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id  INTEGER NOT NULL REFERENCES usuario(id),
    reporte_id  INTEGER NOT NULL REFERENCES reporte(id),
    mensaje     TEXT NOT NULL,
    leida       INTEGER NOT NULL DEFAULT 0,
    creado_en   TEXT NOT NULL
);

-- Perfil adicional: conserva compatibilidad con los usuarios de las demos.
CREATE TABLE IF NOT EXISTS perfil (
    usuario_id INTEGER PRIMARY KEY REFERENCES usuario(id) ON DELETE CASCADE,
    cedula TEXT NOT NULL UNIQUE,
    telefono TEXT NOT NULL,
    direccion TEXT NOT NULL,
    departamento TEXT NOT NULL,
    municipio TEXT NOT NULL,
    vereda TEXT NOT NULL DEFAULT '',
    finca TEXT NOT NULL DEFAULT '',
    consentimiento_en TEXT NOT NULL
);

-- Solo se persiste la huella del identificador de sesión, nunca el token.
CREATE TABLE IF NOT EXISTS sesion_web (
    token_hash TEXT PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    vence_en INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sesion_usuario ON sesion_web(usuario_id);

CREATE TABLE IF NOT EXISTS evento_reporte (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reporte_id INTEGER NOT NULL REFERENCES reporte(id) ON DELETE CASCADE,
    estado TEXT NOT NULL,
    actor_id INTEGER REFERENCES usuario(id),
    creado_en TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_evento_reporte ON evento_reporte(reporte_id, id);
CREATE INDEX IF NOT EXISTS idx_reporte_usuario ON reporte(usuario_id, creado_en);
CREATE INDEX IF NOT EXISTS idx_reporte_estado ON reporte(estado, creado_en);

CREATE TABLE IF NOT EXISTS intento_acceso (
    clave TEXT NOT NULL,
    creado_en INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_intento_acceso ON intento_acceso(clave, creado_en);
