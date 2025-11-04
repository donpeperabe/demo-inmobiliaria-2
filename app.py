from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
from datetime import datetime
import sqlite3

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-please-change')  # Mejor para producción

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ✅ BASE DE DATOS SQLITE PERSISTENTE
def get_db_path():
    """Usa una ruta persistente en Render"""
    return '/tmp/prospects.db' if 'RENDER' in os.environ else 'prospects.db'

def init_db():
    """Inicializa la base de datos de forma robusta"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prospects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                email TEXT,
                telefono TEXT NOT NULL,
                fuente TEXT,
                fecha TEXT NOT NULL,
                propiedad TEXT,
                idioma TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"❌ Error inicializando BD: {e}")

def load_prospects():
    """Carga prospectos con manejo de errores"""
    try:
        init_db()  # Asegurar que la BD existe
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prospects ORDER BY fecha DESC')
        
        prospects = []
        for row in cursor.fetchall():
            prospects.append({
                'id': row[0],
                'nombre': row[1],
                'email': row[2],
                'telefono': row[3],
                'fuente': row[4],
                'fecha': row[5],
                'propiedad': row[6],
                'idioma': row[7]
            })
        
        conn.close()
        print(f"✅ {len(prospects)} prospectos cargados")
        return prospects
    except Exception as e:
        print(f"❌ Error cargando prospectos: {e}")
        return []

def save_prospect(prospect):
    """Guarda prospecto de forma robusta"""
    try:
        init_db()
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO prospects (nombre, email, telefono, fuente, fecha, propiedad, idioma)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            prospect['nombre'],
            prospect.get('email', ''),
            prospect['telefono'],
            prospect.get('fuente', 'direct'),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            prospect.get('propiedad', 'Terrenos en Monterrico'),
            prospect.get('idioma', 'espanol')
        ))
        
        conn.commit()
        conn.close()
        print(f"✅ Prospecto guardado: {prospect['nombre']}")
        return True
    except Exception as e:
        print(f"❌ Error guardando prospecto: {e}")
        return False

# 🔹 Ruta para ver estado de la BD (solo desarrollo)
@app.route('/debug/db')
def debug_db():
    if 'RENDER' not in os.environ:  # Solo en desarrollo
        prospects = load_prospects()
        db_info = {
            'total_prospects': len(prospects),
            'db_path': get_db_path(),
            'db_exists': os.path.exists(get_db_path()),
            'prospects': prospects
        }
        return json.dumps(db_info, ensure_ascii=False, indent=2)
    return "Solo disponible en desarrollo"

# 🔹 Ruta para la landing demo
@app.route('/')
def landing_demo():
    if 'language' not in session:
        session['language'] = 'espanol'
    
    propiedad = {
        'titulo': 'Terrenos en Monterrico',
        'descripcion': 'Terrenos de 15x30mts2 a 400 mts de la playa, excelente inversion para airbnb '
        'o para casa de vacaciones. Acceso facil para conectar servicios y directo a carretera.',
        'precio': '$26,700',
        'titulo2': 'Lots in Monterrico',                    
        'descripcion2': '15x30 m² lots located just 400 meters from the beach — '
        'an excellent investment for Airbnb or a vacation home. '
        'Easy access to utilities and direct connection to the main road.',
        'price': '$26,700',
       'imagenes': [
            'uploads/demo_casa1.jpg',
            'uploads/demo_casa2.jpg',
            'uploads/demo_casa3.jpg'
        ],
        'whatsapp': '50244851125'
    }
    return render_template('landing.html', propiedad=propiedad)

# 🔹 Ruta para cambiar idioma
@app.route('/set_language/<language>')
def set_language(language):
    if language in ['espanol', 'ingles']:
        session['language'] = language
    return redirect(request.referrer or url_for('landing_demo'))

# 🔹 Nueva ruta para formulario de prospectos
@app.route('/prospecto', methods=['GET', 'POST'])
def prospect_form():
    language = session.get('language', 'espanol')
    phone = request.args.get('phone', '')
    source = request.args.get('source', 'direct')
    
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            email = request.form.get('email', '')
            telefono = request.form['telefono']
            fuente = request.form.get('fuente', 'direct')
            
            prospecto = {
                'nombre': nombre,
                'email': email,
                'telefono': telefono,
                'fuente': fuente,
                'propiedad': 'Terrenos en Monterrico',
                'idioma': language
            }
            
            if save_prospect(prospecto):
                return redirect(url_for('thank_you'))
            else:
                return "Error al guardar el prospecto", 500
                
        except Exception as e:
            print(f"Error procesando formulario: {e}")
            return "Error interno del servidor", 500
    
    return render_template('prospect_form.html', phone=phone, source=source, language=language)

# 🔹 Ruta de agradecimiento
@app.route('/gracias')
def thank_you():
    language = session.get('language', 'espanol')
    return render_template('thank_you.html', language=language)

# 🔹 RUTAS ADMINISTRATIVAS
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('logged_in'):
        return redirect(url_for('admin_prospectos'))
        
    if request.method == 'POST':
        password = request.form['password']
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        if password == admin_password:
            session['logged_in'] = True
            return redirect(url_for('admin_prospectos'))
        else:
            # Tu código del popup elegante aquí
            return "Contraseña incorrecta"
    
    # Tu código del popup elegante aquí
    return "Página de login"

@app.route('/admin/prospectos')
def admin_prospectos():
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    prospects = load_prospects()
    return render_template('admin_prospectos.html', prospects=prospects)

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('landing_demo'))

# 🔹 Configuración para Render
if __name__ == '__main__':
    # Inicializar BD al iniciar
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
