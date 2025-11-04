from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
from datetime import datetime
import sqlite3

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.secret_key = 'clave_secreta_terra_zen_2024'  # Clave más simple

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ========== BASE DE DATOS SIMPLE ==========

def get_db_path():
    return 'prospects.db'

def init_db():
    """Inicializa solo la tabla de prospectos"""
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
        print("✅ Base de datos de prospectos lista")
    except Exception as e:
        print(f"❌ Error en BD: {e}")

def load_prospects():
    """Carga todos los prospectos"""
    try:
        init_db()
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
        return prospects
    except Exception as e:
        print(f"Error cargando prospectos: {e}")
        return []

def save_prospect(prospect):
    """Guarda un nuevo prospecto"""
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
        print(f"Error guardando prospecto: {e}")
        return False

# ========== RUTAS PRINCIPALES ==========

@app.route('/')
def landing_demo():
    if 'language' not in session:
        session['language'] = 'espanol'
    
    propiedad = {
        'titulo': 'Terrenos en Monterrico',
        'descripcion': 'Terrenos de 15x30mts2 a 400 mts de la playa, excelente inversion para airbnb o para casa de vacaciones. Acceso facil para conectar servicios y directo a carretera.',
        'precio': '$26,700',
        'titulo2': 'Lots in Monterrico',                    
        'descripcion2': '15x30 m² lots located just 400 meters from the beach — an excellent investment for Airbnb or a vacation home. Easy access to utilities and direct connection to the main road.',
        'price': '$26,700',
        'imagenes': [
            'uploads/demo_casa1.jpg',
            'uploads/demo_casa2.jpg',
            'uploads/demo_casa3.jpg'
        ],
        'whatsapp': '50244851125'
    }
    return render_template('landing.html', propiedad=propiedad)

@app.route('/set_language/<language>')
def set_language(language):
    if language in ['espanol', 'ingles']:
        session['language'] = language
    return redirect(request.referrer or url_for('landing_demo'))

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

@app.route('/gracias')
def thank_you():
    language = session.get('language', 'espanol')
    return render_template('thank_you.html', language=language)

# ========== ADMIN SIMPLE ==========

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Login simple para el admin"""
    # Si ya está logueado, redirigir al panel
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_prospectos'))
    
    if request.method == 'POST':
        password = request.form['password']
        # Contraseña simple por ahora
        if password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_prospectos'))
        else:
            # Mostrar error
            return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Admin Login - Terra Zen</title>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
                <style>
                    body { 
                        font-family: 'Poppins', sans-serif; 
                        background: linear-gradient(135deg, #0a0a0a, #1a1a1a);
                        display: flex; justify-content: center; align-items: center;
                        min-height: 100vh; margin: 0; padding: 20px;
                    }
                    .login-container { 
                        background: #111; border: 1px solid #444; border-radius: 16px;
                        padding: 40px; max-width: 400px; width: 100%; text-align: center;
                        box-shadow: 0 0 40px rgba(255, 215, 0, 0.3);
                    }
                    h2 { color: #ffd700; margin-bottom: 10px; }
                    p { color: #ccc; margin-bottom: 25px; }
                    .form-group { margin-bottom: 20px; text-align: left; }
                    label { display: block; color: #ffd700; margin-bottom: 8px; font-weight: 600; }
                    input { 
                        width: 100%; padding: 12px 15px; background: #222; border: 1px solid #444;
                        border-radius: 8px; color: #fff; font-size: 1rem; transition: all 0.3s;
                    }
                    input:focus { outline: none; border-color: #ffd700; box-shadow: 0 0 10px rgba(255, 215, 0, 0.3); }
                    .btn-submit {
                        width: 100%; padding: 14px; background: linear-gradient(135deg, #ffd700, #ff6b00);
                        color: #000; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600;
                        cursor: pointer; transition: all 0.3s; margin-top: 10px;
                    }
                    .btn-submit:hover {
                        background: linear-gradient(135deg, #ff6b00, #ffd700);
                        box-shadow: 0 0 20px rgba(255, 215, 0, 0.4); transform: translateY(-2px);
                    }
                    .error { 
                        color: #ff6b6b; background: rgba(255,107,107,0.1); padding: 10px; 
                        border-radius: 8px; margin-bottom: 20px; border: 1px solid #ff6b6b;
                    }
                    .user-info { 
                        margin-top: 20px; padding: 15px; background: #1a1a1a; 
                        border-radius: 8px; border: 1px solid #444; font-size: 0.9rem;
                    }
                    .lock-icon {
                        font-size: 2rem;
                        color: #ffd700;
                        margin-bottom: 15px;
                    }
                </style>
            </head>
            <body>
                <div class="login-container">
                    <div class="lock-icon">
                        <i class="fas fa-lock"></i>
                    </div>
                    <h2>Acceso Administrativo</h2>
                    <p>Ingrese la contraseña para continuar</p>
                    
                    <div class="error">
                        <i class="fas fa-exclamation-circle"></i> Contraseña incorrecta
                    </div>
                    
                    <form method="post">
                        <div class="form-group">
                            <label for="password">
                                <i class="fas fa-key"></i> Contraseña
                            </label>
                            <input type="password" id="password" name="password" placeholder="Ingrese la contraseña" required>
                        </div>
                        <button type="submit" class="btn-submit">
                            <i class="fas fa-sign-in-alt"></i> Acceder
                        </button>
                    </form>
                    
                    <div class="user-info">
                        <strong>Contraseña:</strong> admin123
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <a href="/" style="color: #ffd700; text-decoration: none;">
                            <i class="fas fa-arrow-left"></i> Volver al sitio
                        </a>
                    </div>
                </div>
            </body>
            </html>
            '''
    
    # GET request - Mostrar formulario de login
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Login - Terra Zen</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            body { 
                font-family: 'Poppins', sans-serif; 
                background: linear-gradient(135deg, #0a0a0a, #1a1a1a);
                display: flex; justify-content: center; align-items: center;
                min-height: 100vh; margin: 0; padding: 20px;
            }
            .login-container { 
                background: #111; border: 1px solid #444; border-radius: 16px;
                padding: 40px; max-width: 400px; width: 100%; text-align: center;
                box-shadow: 0 0 40px rgba(255, 215, 0, 0.3);
            }
            h2 { color: #ffd700; margin-bottom: 10px; }
            p { color: #ccc; margin-bottom: 25px; }
            .form-group { margin-bottom: 20px; text-align: left; }
            label { display: block; color: #ffd700; margin-bottom: 8px; font-weight: 600; }
            input { 
                width: 100%; padding: 12px 15px; background: #222; border: 1px solid #444;
                border-radius: 8px; color: #fff; font-size: 1rem; transition: all 0.3s;
            }
            input:focus { outline: none; border-color: #ffd700; box-shadow: 0 0 10px rgba(255, 215, 0, 0.3); }
            .btn-submit {
                width: 100%; padding: 14px; background: linear-gradient(135deg, #ffd700, #ff6b00);
                color: #000; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600;
                cursor: pointer; transition: all 0.3s; margin-top: 10px;
            }
            .btn-submit:hover {
                background: linear-gradient(135deg, #ff6b00, #ffd700);
                box-shadow: 0 0 20px rgba(255, 215, 0, 0.4); transform: translateY(-2px);
            }
            .user-info { 
                margin-top: 20px; padding: 15px; background: #1a1a1a; 
                border-radius: 8px; border: 1px solid #444; font-size: 0.9rem;
            }
            .lock-icon {
                font-size: 2rem;
                color: #ffd700;
                margin-bottom: 15px;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="lock-icon">
                <i class="fas fa-lock"></i>
            </div>
            <h2>Acceso Administrativo</h2>
            <p>Ingrese la contraseña para continuar</p>
            
            <form method="post">
                <div class="form-group">
                    <label for="password">
                        <i class="fas fa-key"></i> Contraseña
                    </label>
                    <input type="password" id="password" name="password" placeholder="Ingrese la contraseña" required>
                </div>
                <button type="submit" class="btn-submit">
                    <i class="fas fa-sign-in-alt"></i> Acceder
                </button>
            </form>
            
            <div class="user-info">
                <strong>Contraseña:</strong> admin123
            </div>
            
            <div style="margin-top: 20px;">
                <a href="/" style="color: #ffd700; text-decoration: none;">
                    <i class="fas fa-arrow-left"></i> Volver al sitio
                </a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/prospectos')
def admin_prospectos():
    """Panel de administración de prospectos"""
    # Verificar si está logueado
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    prospects = load_prospects()
    return render_template('admin_prospectos.html', prospects=prospects)

@app.route('/admin/logout')
def admin_logout():
    """Cerrar sesión del admin"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('landing_demo'))

# ========== INICIALIZACIÓN ==========
# Inicializar la base de datos al importar
init_db()

# ========== CONFIGURACIÓN RENDER ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
