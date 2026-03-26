# MediStock 
### Sistema de Gestión de Farmacia Hospitalaria

> Aplicación web para el control automatizado de inventario de medicamentos con trazabilidad lote por lote, algoritmo FIFO, alertas de caducidad y registro de auditoría inmutable.

**Equipo de Desarrollo — UAG / Arizona State University**  
Ingeniería de Software · Marzo–Mayo 2026

| Nombre | Rol |
|--------|-----|
| Samantha Henry Gonzalez | Lead Backend Developer |
| Angel Valencia Saavedra | Frontend Developer |
| Rolando Gonzalez Bejar | DevOps / DB Engineer |
| Marco Leon | QA Engineer / Tester |

---

## Descripción

MediStock resuelve dos problemas críticos en la gestión manual de medicamentos hospitalarios:

- **Pérdidas económicas** por no detectar medicamentos próximos a vencer
- **Riesgos de seguridad** para el paciente por dispensación errónea

El sistema implementa control de inventario por lote con algoritmo FIFO, semáforo de farmacovigilancia a 90/60/30 días, y un registro de auditoría que no puede modificarse.

---

## Tecnologías

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.10+ con Flask |
| Frontend | HTML5 + CSS3 + JavaScript vanilla |
| Base de datos | SQLite3 |
| Control de versiones | Git + GitHub |

---

## Estructura del Proyecto

```
medistock/
├── backend/
│   └── app.py              # Aplicación Flask principal — todas las rutas y lógica
├── frontend/
│   ├── templates/          # Páginas HTML (Jinja2)
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── inventario.html
│   │   ├── entrada.html
│   │   ├── salida.html
│   │   ├── alertas.html
│   │   ├── auditoria.html
│   │   └── reportes.html
│   └── static/
│       ├── style.css       # Estilos globales
│       └── script.js       # Interacciones del cliente
├── database/
│   ├── schema.sql          # Script de creación de tablas y datos iniciales
│   └── database.db         # Archivo SQLite (generado al inicializar)
├── docs/
│   ├── SPMP_MediStock.docx
│   ├── SRS_MediStock.docx
│   └── SCM_MediStock.docx
└── README.md
```

---

## Instalación y Configuración

### Requisitos previos

- Python 3.10 o superior
- pip

### Pasos

**1. Clonar el repositorio**
```bash
git clone https://github.com/<tu-usuario>/medistock.git
cd medistock
```

**2. Crear y activar el entorno virtual**
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

**3. Instalar dependencias**
```bash
pip install flask
```

**4. Inicializar la base de datos**
```bash
cd backend
python app.py --init
```

Esto crea las tablas, inserta los medicamentos de ejemplo y configura los usuarios por defecto.

**5. Iniciar el servidor**
```bash
python app.py
```

Abrir en el navegador: [http://localhost:5000](http://localhost:5000)

---

## Credenciales de Prueba

| Usuario | Contraseña | Rol | Permisos |
|---------|-----------|-----|----------|
| `admin` | `admin123` | Administrador | Acceso total: inventario, alertas, auditoría, reportes |
| `farmaceutico` | `farma123` | Farmacéutico | Solo dispensación de medicamentos |

---

## Funcionalidades

### Módulos implementados

| Módulo | Ruta | Rol requerido |
|--------|------|---------------|
| Login / Logout | `/login` | — |
| Dashboard | `/dashboard` | Cualquiera |
| Inventario | `/inventario` | Cualquiera |
| Entrada de medicamentos | `/inventario/entrada` | Admin |
| Salida / Dispensación | `/inventario/salida` | Cualquiera |
| Alertas de caducidad | `/alertas` | Admin |
| Auditoría | `/auditoria` | Admin |
| Reportes dinámicos | `/reportes` | Admin |

### Algoritmo FIFO

Al registrar una salida, el sistema selecciona automáticamente el lote con la **fecha de caducidad más próxima** que tenga stock suficiente. Esto garantiza que los medicamentos más antiguos se dispensen primero, reduciendo pérdidas por vencimiento.

### Semáforo de farmacovigilancia

Las alertas se clasifican por días restantes hasta la caducidad:

-  **Rojo** — 0 a 30 días
-  **Amarillo** — 31 a 60 días
-  **Verde** — 61 a 90 días

### Auditoría inmutable

Cada acción del sistema genera un registro automático en la tabla `auditoria`. Esta tabla solo acepta `INSERT` — nunca `UPDATE` ni `DELETE`. Se registran: `LOGIN`, `LOGOUT`, `ENTRADA`, `SALIDA`.

### Medicamentos controlados

Los medicamentos de tipo `controlado` (ej. Morfina) requieren obligatoriamente un número de receta para poder ser dispensados.

---

## Base de Datos

### Tablas

| Tabla | Descripción |
|-------|-------------|
| `usuarios` | Usuarios del sistema con rol (`admin` / `farmaceutico`) |
| `medicamentos` | Catálogo de medicamentos con tipo (`libre` / `controlado`) |
| `lotes` | Entradas de inventario por lote con fecha de caducidad |
| `dispensaciones` | Historial de salidas con referencia al lote FIFO usado |
| `auditoria` | Registro inmutable de todas las acciones del sistema |

### Reiniciar la base de datos

```bash
cd backend
python app.py --init
```

>  Esto elimina todos los datos existentes y recrea las tablas desde cero.

---

## Medicamentos de Ejemplo

Al inicializar, el sistema incluye tres medicamentos de prueba:

| Nombre | Tipo | Unidad |
|--------|------|--------|
| Paracetamol 500mg | Libre | Piezas |
| Morfina 10mg | Controlado | Ampolletas |
| Amoxicilina 500mg | Libre | Cápsulas |

---

## Control de Versiones

El proyecto sigue las convenciones definidas en el `SCM_MediStock.docx`:

- Ramas: `feature/<CR-ID>-<descripcion>` para nuevas funcionalidades
- Commits semánticos: `feat:`, `fix:`, `chore:`, `docs:`
- Todo merge a `main` requiere revisión de al menos un compañero (Pull Request)

---

## Sprints

| Sprint | Período | Estado |
|--------|---------|--------|
| Sprint 0 — Configuración | 17–21 mar |  Completo |
| Sprint 1 — Autenticación y BD | 24 mar – 4 abr |  En curso |
| Sprint 2 — Inventario y FIFO | 7–25 abr |  Siguiente |
| Sprint 3 — Alertas y Reportes | 28 abr – 16 may |  Pendiente |
| Sprint 4 — Cierre y Entrega | 19–23 may |  Pendiente |

---

*MediStock — Ingeniería de Software · UAG / Arizona State University · 2026*
