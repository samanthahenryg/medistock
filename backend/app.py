# ============================================================
# MediStock - Aplicacion principal Flask
# Archivo: backend/app.py
# Descripcion: Punto de entrada del servidor. Define todas
#              las rutas (URLs) del sistema y su logica.
# Ejecutar: python app.py
# ============================================================

from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
import os
from datetime import date, datetime

# --- Configuracion de la aplicacion ---
app = Flask(
    __name__,
    template_folder='../frontend/templates',   # carpeta de HTMLs
    static_folder='../frontend/static'         # carpeta de CSS y JS
)

# Clave secreta para cifrar las sesiones (cambiala en produccion)
app.secret_key = 'medistock_clave_secreta_2026'

# Ruta a la base de datos SQLite
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'database.db')


# ============================================================
# FUNCION AUXILIAR: conectar a la base de datos
# Usamos row_factory para poder acceder a las columnas por nombre
# Ejemplo: fila['nombre'] en vez de fila[0]
# ============================================================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # acceso por nombre de columna
    return conn


# ============================================================
# FUNCION AUXILIAR: encriptar contrasena
# Usamos SHA-256 para no guardar contrasenas en texto plano
# ============================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ============================================================
# FUNCION AUXILIAR: verificar si hay sesion activa
# Se usa en rutas que requieren estar logueado
# ============================================================
def login_requerido(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesion para acceder.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


# ============================================================
# FUNCION AUXILIAR: verificar rol de administrador
# ============================================================
def admin_requerido(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        if session.get('rol') != 'admin':
            flash('No tienes permiso para acceder a esta seccion.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return wrapper


# ============================================================
# FUNCION AUXILIAR: registrar en auditoria
# Se llama cada vez que pasa algo importante en el sistema
# ============================================================
def registrar_auditoria(tipo_accion, descripcion, usuario_id=None,
                         medicamento_id=None, lote_id=None,
                         cantidad=None, paciente=None):
    db = get_db()
    db.execute('''
        INSERT INTO auditoria 
        (usuario_id, tipo_accion, descripcion, medicamento_id, lote_id, cantidad, paciente)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (usuario_id, tipo_accion, descripcion, medicamento_id, lote_id, cantidad, paciente))
    db.commit()
    db.close()


# ============================================================
# RUTA: / (raiz)
# Redirige al login si no hay sesion, al dashboard si hay
# ============================================================
@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# ============================================================
# RUTA: /login  GET y POST
# GET:  muestra el formulario de login
# POST: valida las credenciales y crea la sesion
# ============================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya tiene sesion activa, mandarlo al dashboard
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Validar que no vengan vacios
        if not username or not password:
            flash('Por favor ingresa usuario y contrasena.', 'error')
            return render_template('login.html')

        # Buscar el usuario en la base de datos
        db = get_db()
        usuario = db.execute(
            'SELECT * FROM usuarios WHERE username = ? AND activo = 1',
            (username,)
        ).fetchone()
        db.close()

        # Verificar si existe y si la contrasena es correcta
        if usuario and usuario['password'] == hash_password(password):
            # Guardar datos en la sesion
            session['usuario_id'] = usuario['id']
            session['username']   = usuario['username']
            session['nombre']     = usuario['nombre']
            session['rol']        = usuario['rol']

            # Registrar el login en auditoria
            registrar_auditoria(
                tipo_accion='LOGIN',
                descripcion=f'Usuario {username} inicio sesion exitosamente.',
                usuario_id=usuario['id']
            )

            flash(f'Bienvenido, {usuario["nombre"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Mensaje generico: no revelar si el usuario existe o no
            flash('Usuario o contrasena incorrectos.', 'error')
            return render_template('login.html')

    # GET: solo mostrar el formulario
    return render_template('login.html')


# ============================================================
# RUTA: /logout
# Cierra la sesion y redirige al login
# ============================================================
@app.route('/logout')
def logout():
    nombre = session.get('nombre', 'Usuario')
    usuario_id = session.get('usuario_id')
    session.clear()
    registrar_auditoria(
        tipo_accion='LOGOUT',
        descripcion=f'{nombre} cerro sesion.',
        usuario_id=usuario_id
    )
    flash('Sesion cerrada correctamente.', 'success')
    return redirect(url_for('login'))


# ============================================================
# RUTA: /dashboard
# Pagina principal despues del login
# Muestra resumen de inventario y alertas activas
# ============================================================
@app.route('/dashboard')
@login_requerido
def dashboard():
    db = get_db()
    hoy = date.today()

    # Contar total de medicamentos registrados
    total_medicamentos = db.execute(
        'SELECT COUNT(*) as total FROM medicamentos'
    ).fetchone()['total']

    # Obtener alertas: lotes proximos a vencer en los proximos 90 dias
    alertas = db.execute('''
        SELECT 
            m.nombre as medicamento,
            l.numero_lote,
            l.cantidad,
            l.fecha_caducidad,
            CAST((JULIANDAY(l.fecha_caducidad) - JULIANDAY('now')) AS INTEGER) as dias_restantes
        FROM lotes l
        JOIN medicamentos m ON l.medicamento_id = m.id
        WHERE l.activo = 1 
          AND l.cantidad > 0
          AND JULIANDAY(l.fecha_caducidad) - JULIANDAY('now') <= 90
        ORDER BY l.fecha_caducidad ASC
    ''').fetchall()

    # Contar lotes vencidos (para mostrar en el dashboard)
    lotes_vencidos = db.execute('''
        SELECT COUNT(*) as total FROM lotes
        WHERE activo = 1 AND fecha_caducidad < DATE('now')
    ''').fetchone()['total']

    db.close()

    return render_template('dashboard.html',
        total_medicamentos=total_medicamentos,
        alertas=alertas,
        lotes_vencidos=lotes_vencidos,
        hoy=hoy
    )


# ============================================================
# RUTA: /inventario  GET
# Muestra la lista de todos los medicamentos y sus lotes
# ============================================================
@app.route('/inventario')
@login_requerido
def inventario():
    db = get_db()

    # Obtener todos los medicamentos con su stock total
    medicamentos = db.execute('''
        SELECT 
            m.id,
            m.nombre,
            m.tipo,
            m.unidad_medida,
            COALESCE(SUM(l.cantidad), 0) as stock_total
        FROM medicamentos m
        LEFT JOIN lotes l ON m.id = l.medicamento_id 
                          AND l.activo = 1 
                          AND l.fecha_caducidad >= DATE('now')
        GROUP BY m.id
        ORDER BY m.nombre
    ''').fetchall()

    # Obtener todos los lotes activos con info del medicamento
    lotes = db.execute('''
        SELECT 
            l.id,
            l.numero_lote,
            l.cantidad,
            l.fecha_caducidad,
            l.fecha_entrada,
            m.nombre as medicamento,
            m.tipo,
            CAST((JULIANDAY(l.fecha_caducidad) - JULIANDAY('now')) AS INTEGER) as dias_restantes
        FROM lotes l
        JOIN medicamentos m ON l.medicamento_id = m.id
        WHERE l.activo = 1
        ORDER BY l.fecha_caducidad ASC
    ''').fetchall()

    db.close()
    return render_template('inventario.html',
        medicamentos=medicamentos,
        lotes=lotes
    )


# ============================================================
# RUTA: /inventario/entrada  GET y POST
# Solo accesible para administradores
# Registra la entrada de un nuevo lote de medicamento
# ============================================================
@app.route('/inventario/entrada', methods=['GET', 'POST'])
@admin_requerido
def entrada_medicamento():
    db = get_db()

    if request.method == 'POST':
        medicamento_id  = request.form.get('medicamento_id')
        numero_lote     = request.form.get('numero_lote', '').strip()
        cantidad        = request.form.get('cantidad')
        fecha_caducidad = request.form.get('fecha_caducidad')

        # Validar que todos los campos obligatorios esten llenos
        if not all([medicamento_id, numero_lote, cantidad, fecha_caducidad]):
            flash('Todos los campos son obligatorios.', 'error')
            medicamentos = db.execute('SELECT * FROM medicamentos ORDER BY nombre').fetchall()
            db.close()
            return render_template('entrada.html', medicamentos=medicamentos)

        # Validar que la cantidad sea positiva
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            flash('La cantidad debe ser un numero mayor a cero.', 'error')
            medicamentos = db.execute('SELECT * FROM medicamentos ORDER BY nombre').fetchall()
            db.close()
            return render_template('entrada.html', medicamentos=medicamentos)

        # Validar que la fecha de caducidad sea futura
        if fecha_caducidad <= str(date.today()):
            flash('La fecha de caducidad debe ser una fecha futura.', 'error')
            medicamentos = db.execute('SELECT * FROM medicamentos ORDER BY nombre').fetchall()
            db.close()
            return render_template('entrada.html', medicamentos=medicamentos)

        # Insertar el nuevo lote en la base de datos
        db.execute('''
            INSERT INTO lotes (medicamento_id, numero_lote, cantidad, fecha_caducidad)
            VALUES (?, ?, ?, ?)
        ''', (medicamento_id, numero_lote, cantidad, fecha_caducidad))
        db.commit()

        # Obtener nombre del medicamento para la auditoria
        med = db.execute(
            'SELECT nombre FROM medicamentos WHERE id = ?', (medicamento_id,)
        ).fetchone()

        # Registrar la entrada en auditoria
        registrar_auditoria(
            tipo_accion='ENTRADA',
            descripcion=f'Entrada de {cantidad} unidades de {med["nombre"]}, lote {numero_lote}, vence {fecha_caducidad}.',
            usuario_id=session['usuario_id'],
            medicamento_id=medicamento_id,
            cantidad=cantidad
        )

        flash(f'Lote {numero_lote} registrado correctamente.', 'success')
        db.close()
        return redirect(url_for('inventario'))

    # GET: mostrar formulario de entrada
    medicamentos = db.execute('SELECT * FROM medicamentos ORDER BY nombre').fetchall()
    db.close()
    return render_template('entrada.html', medicamentos=medicamentos)


# ============================================================
# RUTA: /inventario/salida  GET y POST
# Accesible para farmaceuticos y administradores
# Registra la dispensacion de un medicamento a un paciente
# Aplica algoritmo FIFO automaticamente
# ============================================================
@app.route('/inventario/salida', methods=['GET', 'POST'])
@login_requerido
def salida_medicamento():
    db = get_db()

    if request.method == 'POST':
        medicamento_id  = request.form.get('medicamento_id')
        cantidad        = request.form.get('cantidad')
        paciente_nombre = request.form.get('paciente_nombre', '').strip()
        numero_receta   = request.form.get('numero_receta', '').strip()

        # Validar campos obligatorios basicos
        if not all([medicamento_id, cantidad, paciente_nombre]):
            flash('Medicamento, cantidad y nombre del paciente son obligatorios.', 'error')
            medicamentos = db.execute(
                'SELECT * FROM medicamentos ORDER BY nombre'
            ).fetchall()
            db.close()
            return render_template('salida.html', medicamentos=medicamentos)

        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            flash('La cantidad debe ser un numero mayor a cero.', 'error')
            medicamentos = db.execute('SELECT * FROM medicamentos ORDER BY nombre').fetchall()
            db.close()
            return render_template('salida.html', medicamentos=medicamentos)

        # Verificar si el medicamento es controlado (requiere receta)
        med = db.execute(
            'SELECT * FROM medicamentos WHERE id = ?', (medicamento_id,)
        ).fetchone()

        if med['tipo'] == 'controlado' and not numero_receta:
            flash('Este medicamento es controlado. Debes ingresar el numero de receta.', 'error')
            medicamentos = db.execute('SELECT * FROM medicamentos ORDER BY nombre').fetchall()
            db.close()
            return render_template('salida.html', medicamentos=medicamentos)

        # --- ALGORITMO FIFO ---
        # Obtener el lote con la fecha de caducidad mas proxima
        # que tenga suficiente stock y no este vencido
        lote = db.execute('''
            SELECT * FROM lotes
            WHERE medicamento_id = ?
              AND activo = 1
              AND cantidad >= ?
              AND fecha_caducidad >= DATE('now')
            ORDER BY fecha_caducidad ASC
            LIMIT 1
        ''', (medicamento_id, cantidad)).fetchone()

        if not lote:
            # Verificar si hay stock pero insuficiente
            stock_total = db.execute('''
                SELECT COALESCE(SUM(cantidad), 0) as total 
                FROM lotes 
                WHERE medicamento_id = ? AND activo = 1 AND fecha_caducidad >= DATE('now')
            ''', (medicamento_id,)).fetchone()['total']

            if stock_total > 0:
                flash(f'Stock insuficiente. Solo hay {stock_total} unidades disponibles.', 'error')
            else:
                flash('No hay stock disponible de este medicamento.', 'error')

            medicamentos = db.execute('SELECT * FROM medicamentos ORDER BY nombre').fetchall()
            db.close()
            return render_template('salida.html', medicamentos=medicamentos)

        # Descontar la cantidad del lote seleccionado por FIFO
        nueva_cantidad = lote['cantidad'] - cantidad
        db.execute(
            'UPDATE lotes SET cantidad = ? WHERE id = ?',
            (nueva_cantidad, lote['id'])
        )

        # Si el lote queda en 0, marcarlo como inactivo
        if nueva_cantidad == 0:
            db.execute('UPDATE lotes SET activo = 0 WHERE id = ?', (lote['id'],))

        # Registrar la dispensacion en la tabla dispensaciones
        db.execute('''
            INSERT INTO dispensaciones 
            (farmaceutico_id, paciente_nombre, medicamento_id, lote_id, cantidad, numero_receta)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session['usuario_id'], paciente_nombre, medicamento_id,
              lote['id'], cantidad, numero_receta or None))
        db.commit()

        # Registrar en auditoria
        registrar_auditoria(
            tipo_accion='SALIDA',
            descripcion=f'Dispensacion de {cantidad} unidades de {med["nombre"]}, '
                        f'lote {lote["numero_lote"]}, a paciente {paciente_nombre}.',
            usuario_id=session['usuario_id'],
            medicamento_id=medicamento_id,
            lote_id=lote['id'],
            cantidad=cantidad,
            paciente=paciente_nombre
        )

        flash(f'Dispensacion registrada. Lote {lote["numero_lote"]} utilizado (FIFO).', 'success')
        db.close()
        return redirect(url_for('inventario'))

    # GET: mostrar formulario de salida
    medicamentos = db.execute('''
        SELECT m.*, COALESCE(SUM(l.cantidad), 0) as stock_total
        FROM medicamentos m
        LEFT JOIN lotes l ON m.id = l.medicamento_id 
                          AND l.activo = 1 
                          AND l.fecha_caducidad >= DATE('now')
        GROUP BY m.id
        HAVING stock_total > 0
        ORDER BY m.nombre
    ''').fetchall()
    db.close()
    return render_template('salida.html', medicamentos=medicamentos)


# ============================================================
# RUTA: /alertas
# Muestra el panel de farmacovigilancia con semaforo
# Solo admin
# ============================================================
@app.route('/alertas')
@admin_requerido
def alertas():
    db = get_db()

    lotes_alertas = db.execute('''
        SELECT 
            m.nombre as medicamento,
            m.tipo,
            l.numero_lote,
            l.cantidad,
            l.fecha_caducidad,
            CAST((JULIANDAY(l.fecha_caducidad) - JULIANDAY('now')) AS INTEGER) as dias_restantes
        FROM lotes l
        JOIN medicamentos m ON l.medicamento_id = m.id
        WHERE l.activo = 1
        ORDER BY l.fecha_caducidad ASC
    ''').fetchall()

    db.close()
    return render_template('alertas.html', lotes=lotes_alertas)


# ============================================================
# RUTA: /auditoria
# Muestra el historial completo de transacciones
# Solo admin, solo lectura
# ============================================================
@app.route('/auditoria')
@admin_requerido
def auditoria():
    db = get_db()

    registros = db.execute('''
        SELECT 
            a.*,
            u.nombre as nombre_usuario,
            m.nombre as nombre_medicamento
        FROM auditoria a
        LEFT JOIN usuarios u ON a.usuario_id = u.id
        LEFT JOIN medicamentos m ON a.medicamento_id = m.id
        ORDER BY a.fecha_hora DESC
        LIMIT 200
    ''').fetchall()

    db.close()
    return render_template('auditoria.html', registros=registros)


# ============================================================
# RUTA: /reportes
# Reportes dinamicos de consumo filtrados por periodo y tipo
# Solo admin
# ============================================================
@app.route('/reportes')
@admin_requerido
def reportes():
    db = get_db()

    fecha_inicio    = request.args.get('fecha_inicio', '')
    fecha_fin       = request.args.get('fecha_fin', '')
    tipo_filtro     = request.args.get('tipo', 'todos')
    medicamento_id  = request.args.get('medicamento_id', '')

    query = '''
        SELECT 
            d.*,
            u.nombre as farmaceutico,
            m.nombre as medicamento,
            m.tipo as tipo_medicamento,
            l.numero_lote
        FROM dispensaciones d
        JOIN usuarios u ON d.farmaceutico_id = u.id
        JOIN medicamentos m ON d.medicamento_id = m.id
        JOIN lotes l ON d.lote_id = l.id
        WHERE 1=1
    '''
    params = []

    if fecha_inicio:
        query += ' AND DATE(d.fecha_hora) >= ?'
        params.append(fecha_inicio)
    if fecha_fin:
        query += ' AND DATE(d.fecha_hora) <= ?'
        params.append(fecha_fin)
    if tipo_filtro != 'todos':
        query += ' AND m.tipo = ?'
        params.append(tipo_filtro)
    if medicamento_id:
        query += ' AND d.medicamento_id = ?'
        params.append(medicamento_id)

    query += ' ORDER BY d.fecha_hora DESC'

    dispensaciones = db.execute(query, params).fetchall()
    medicamentos   = db.execute('SELECT * FROM medicamentos ORDER BY nombre').fetchall()
    db.close()

    return render_template('reportes.html',
        dispensaciones=dispensaciones,
        medicamentos=medicamentos,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        tipo_filtro=tipo_filtro,
        medicamento_id=medicamento_id
    )


# ============================================================
# SCRIPT DE INICIO: crear la BD y el usuario admin
# Se ejecuta solo la primera vez con: python app.py --init
# ============================================================
def inicializar_bd():
    """Crea las tablas y el usuario admin por defecto."""
    import sys
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')

    conn = sqlite3.connect(DB_PATH)
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn.executescript(sql)

    # Actualizar la contrasena del admin con el hash correcto
    conn.execute(
        'UPDATE usuarios SET password = ? WHERE username = ?',
        (hash_password('admin123'), 'admin')
    )
    conn.execute(
        'UPDATE usuarios SET password = ? WHERE username = ?',
        (hash_password('farma123'), 'farmaceutico')
    )
    conn.commit()
    conn.close()
    print('Base de datos inicializada correctamente.')
    print('Usuario: admin | Contrasena: admin123')
    print('Usuario: farmaceutico | Contrasena: farma123')


# ============================================================
# PUNTO DE ENTRADA
# ============================================================
if __name__ == '__main__':
    import sys
    if '--init' in sys.argv:
        inicializar_bd()
    else:
        # debug=True muestra errores en el navegador (solo para desarrollo)
        app.run(debug=True, port=5000)
        