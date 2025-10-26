from flask import Flask, render_template
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 🔹 Ruta para la landing demo
@app.route('/')
def landing_demo():
    propiedad = {
        'titulo': 'Terrenos en Monterrico',
        'descripcion': 'Terrenos de 15x30mts2 a 400 mts de la playa, excelente inversion para airbnb '
        'o para casa de vacaciones. Acceso facil para conectar servicios y directo a carretera.',
        'precio': '$26,700',
        'title': 'Lots in Monterrico',
        'description': '15x30 m² lots located just 400 meters from the beach — '
        'an excellent investment for Airbnb or a vacation home. '
        'Easy access to utilities and direct connection to the main road.',
        'price': '$26,700' ,
       'imagenes': [
            'uploads/demo_casa1.jpg',
            'uploads/demo_casa2.jpg',
            'uploads/demo_casa3.jpg'
        ],
        'whatsapp': '50244851125'  # tu número en formato internacional sin +
    }
    return render_template('landing.html', propiedad=propiedad)

# 🔹 Configuración correcta para Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

