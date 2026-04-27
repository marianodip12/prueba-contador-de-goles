#!/usr/bin/env python3
"""
Handball Goal Counter - Aplicación Flask para Render
Sistema todo-en-uno: Frontend + Backend + Procesamiento Python
"""

import os
import sys
import json
import traceback
from flask import Flask, render_template, request, jsonify

# Agregar directorio python al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

app = Flask(__name__)

# Configuración
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max


@app.route('/')
def index():
    """Página principal con UI"""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check para Render"""
    return jsonify({
        "status": "healthy",
        "service": "handball-goal-counter",
        "version": "1.0.0"
    })


@app.route('/api/check-deps')
def check_deps():
    """Verifica que todas las dependencias estén disponibles"""
    deps_status = {
        "opencv": False,
        "numpy": False,
        "ultralytics": False,
        "yt_dlp": False,
        "model_file": False,
        "errors": []
    }
    
    try:
        import cv2
        deps_status["opencv"] = True
        deps_status["opencv_version"] = cv2.__version__
    except ImportError as e:
        deps_status["errors"].append(f"OpenCV: {str(e)}")
    
    try:
        import numpy
        deps_status["numpy"] = True
        deps_status["numpy_version"] = numpy.__version__
    except ImportError as e:
        deps_status["errors"].append(f"NumPy: {str(e)}")
    
    try:
        from ultralytics import YOLO
        deps_status["ultralytics"] = True
    except ImportError as e:
        deps_status["errors"].append(f"Ultralytics: {str(e)}")
    
    try:
        import yt_dlp
        deps_status["yt_dlp"] = True
        deps_status["yt_dlp_version"] = yt_dlp.version.__version__
    except ImportError as e:
        deps_status["errors"].append(f"yt-dlp: {str(e)}")
    
    # Verificar modelo
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'yolov8n.pt')
    deps_status["model_file"] = os.path.exists(model_path)
    deps_status["model_path"] = model_path
    
    return jsonify(deps_status)


@app.route('/api/analyze-video', methods=['POST'])
def analyze_video():
    """Endpoint principal para analizar videos"""
    try:
        data = request.get_json()
        
        if not data or 'youtube_url' not in data:
            return jsonify({
                "success": False,
                "error": "Falta el parámetro 'youtube_url'"
            }), 400
        
        youtube_url = data['youtube_url']
        
        # Validar URL
        import re
        youtube_regex = r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+'
        if not re.match(youtube_regex, youtube_url):
            return jsonify({
                "success": False,
                "error": "URL de YouTube inválida"
            }), 400
        
        # Importar y ejecutar el procesador
        from video_processor import HandballVideoProcessor
        
        print(f"🎯 Iniciando análisis: {youtube_url}", flush=True)
        
        processor = HandballVideoProcessor()
        result = processor.process_video(youtube_url)
        
        # Convertir dataclass a dict
        from dataclasses import asdict
        result_dict = asdict(result)
        
        return jsonify({
            "success": True,
            "data": result_dict
        })
        
    except ImportError as e:
        error_trace = traceback.format_exc()
        print(f"❌ ImportError: {error_trace}", flush=True)
        return jsonify({
            "success": False,
            "error": f"Dependencia faltante: {str(e)}",
            "type": "ImportError",
            "hint": "Verifica /api/check-deps para ver qué falta"
        }), 500
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ Error: {error_trace}", flush=True)
        return jsonify({
            "success": False,
            "error": str(e),
            "type": type(e).__name__,
            "trace": error_trace if app.debug else None
        }), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint no encontrado"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Error interno del servidor"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Iniciando servidor en puerto {port}", flush=True)
    print(f"🔧 Debug mode: {debug}", flush=True)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
