# MediStock
Sistema web para el control de inventario de medicamentos en farmacias hospitalarias.

Ingenieria de Software I y Programación WEB

---

## ¿Qué hace?

- Controla el inventario de medicamentos por lote
- Dispensa medicamentos usando algoritmo FIFO automático
- Alerta cuando un lote está próximo a vencer (30, 60 y 90 días)
- Requiere receta para medicamentos controlados
- Registra un historial de auditoría inmutable de todas las acciones

---

## Tecnologías

- Python + Flask
- HTML + CSS + JavaScript
- SQLite

---

## Instalación

```bash
# Clonar el repo
git clone https://github.com/samanthahenryg/medistock.git
cd medistock

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install flask

# Inicializar base de datos
cd backend
python3 app.py --init

# Iniciar servidor
python3 app.py
```

Abrir en: http://localhost:5001

---

## Credenciales de prueba

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin123` | Administrador |
| `farmaceutico` | `farma123` | Farmacéutico |

---

## Equipo

| Nombre | Rol |
|---|---|
| Samantha Henry Gonzalez | Backend / Base de datos |
| Angel Valencia Saavedra | Frontend |
| Rolando Gonzalez Bejar | DevOps / QA |
