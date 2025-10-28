from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por una clave segura

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Archivo para almacenar prospectos
PROSPECTS_FILE = 'prospects.json'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Cargar prospectos existentes - CORREGIDO
def load_prospects():
    try:
        if os.path.exists(PROSPECTS_FILE) and os.path.getsize(PROSPECTS_FILE) > 0:
            with open(PROSPECTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error cargando prospectos: {e}")
        # Si hay error, crear archivo nuevo
        with open(PROSPECTS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []

# Guardar nuevos prospectos - CORREGIDO
def save_prospect(prospect):
    try:
        prospects = load_prospects()
        # Generar ID único
        prospect['id'] = len(prospects) + 1
        prospects.append(prospect)
        
        with open(PROSPECTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(prospects, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error guardando prospecto: {e}")
        return False

# 🔹 Ruta para la landing demo
@app.route('/')
def landing_demo():
    # Inicializar idioma por defecto si no existe
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
    # Obtener idioma de la sesión
    language = session.get('language', 'espanol')
    
    # Obtener número de teléfono desde parámetro URL (si viene de WhatsApp)
    phone = request.args.get('phone', '')
    source = request.args.get('source', 'direct')
    
    if request.method == 'POST':
        try:
            # Procesar el formulario
            nombre = request.form['nombre']
            email = request.form.get('email', '')  # Email es opcional ahora
            telefono = request.form['telefono']
            fuente = request.form.get('fuente', 'direct')
            
            # Crear objeto prospecto
            prospecto = {
                'nombre': nombre,
                'email': email,
                'telefono': telefono,
                'fuente': fuente,
                'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'propiedad': 'Terrenos en Monterrico',
                'idioma': language  # Guardar el idioma del prospecto
            }
            
            # Guardar prospecto
            if save_prospect(prospecto):
                # Redirigir a página de éxito
                return redirect(url_for('thank_you'))
            else:
                return "Error al guardar el prospecto", 500
                
        except Exception as e:
            print(f"Error procesando formulario: {e}")
            return "Error interno del servidor", 500
    
    return render_template('prospect_form.html', phone=phone, source=source, language=language)

# 🔹 Ruta de agradecimiento después del formulario
@app.route('/gracias')
def thank_you():
    # Obtener idioma de la sesión
    language = session.get('language', 'espanol')
    return render_template('thank_you.html', language=language)

# 🔹 Ruta administrativa para ver prospectos
@app.route('/admin/prospectos')
def admin_prospectos():
    prospects = load_prospects()
    return render_template('admin_prospectos.html', prospects=prospects)

# 🔹 Ruta para limpiar/resetear archivo de prospectos (solo desarrollo)
@app.route('/admin/reset_prospects')
def reset_prospects():
    if os.path.exists(PROSPECTS_FILE):
        os.remove(PROSPECTS_FILE)
    return "Archivo de prospectos reseteado"

# 🔹 Configuración correcta para Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)



