import os
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configuración
UPLOAD_FOLDER = Path(__file__).parent / "uploads"
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'webp'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
SERVER_URL = "http://127.0.0.1:5000"

# Crear carpeta de uploads si no existe
UPLOAD_FOLDER.mkdir(exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_url(filename):
    """Devuelve la URL pública del archivo"""
    return f"{SERVER_URL}/files/{filename}"

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Endpoint para subir archivos.
    Espera multipart/form-data con un campo 'file'
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Verificar tamaño
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File too large. Max: {MAX_FILE_SIZE / 1024 / 1024}MB'}), 400
        
        # Generar nombre seguro con timestamp
        ext = file.filename.rsplit('.', 1)[1].lower()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"blancos_{timestamp}_{secure_filename(file.filename.rsplit('.', 1)[0])}.{ext}"
        
        filepath = UPLOAD_FOLDER / filename
        file.save(str(filepath))
        
        return jsonify({
            'success': True,
            'filename': filename,
            'url': get_file_url(filename),
            'size': file_size,
            'uploaded_at': timestamp,
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files/<filename>', methods=['GET'])
def download_file(filename):
    """
    Endpoint para descargar/acceder archivos almacenados
    """
    try:
        # Validar que el filename sea seguro
        if '/' in filename or '\\' in filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        filepath = UPLOAD_FOLDER / filename
        if not filepath.exists():
            return jsonify({'error': f'File not found: {filename}'}), 404
        
        print(f"📥 Sirviendo archivo: {filename} desde {filepath}")
        
        # Servir el archivo con headers correctos
        response = send_from_directory(str(UPLOAD_FOLDER), filename)
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        print(f"❌ Error sirviendo {filename}: {e}")
        return jsonify({'error': str(e)}), 404

@app.route('/list', methods=['GET'])
def list_files():
    """
    Endpoint para listar todos los archivos subidos
    """
    try:
        files = []
        for filepath in UPLOAD_FOLDER.glob('*'):
            if filepath.is_file():
                stat = filepath.stat()
                files.append({
                    'filename': filepath.name,
                    'url': get_file_url(filepath.name),
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })
        
        return jsonify({
            'success': True,
            'count': len(files),
            'files': sorted(files, key=lambda x: x['modified'], reverse=True),
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'server_url': SERVER_URL,
        'upload_folder': str(UPLOAD_FOLDER),
        'max_file_size_mb': MAX_FILE_SIZE / 1024 / 1024,
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Endpoint raíz con información del servidor"""
    return jsonify({
        'name': 'Servidor Multimedia Blancos Primavera',
        'version': '1.0.0',
        'endpoints': {
            'POST /upload': 'Subir archivo (multipart/form-data con campo "file")',
            'GET /files/<filename>': 'Descargar archivo',
            'GET /list': 'Listar todos los archivos',
            'GET /health': 'Estado del servidor',
        },
    }), 200

if __name__ == '__main__':
    print(f"🚀 Servidor iniciando en {SERVER_URL}")
    print(f"📁 Carpeta de uploads: {UPLOAD_FOLDER}")
    print(f"📦 Tamaño máximo: {MAX_FILE_SIZE / 1024 / 1024}MB")
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False,
    )
