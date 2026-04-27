# 🏐 Sistema de Conteo de Goles - Handball

Sistema automatizado para detectar y contar goles de handball desde videos de YouTube usando YOLOv8, DeepSORT y yt-dlp.

## 🚀 Despliegue en Vercel

### Opción 1: Deploy directo (Recomendado)

1. **Instalar Vercel CLI**
```bash
npm i -g vercel
```

2. **Login en Vercel**
```bash
vercel login
```

3. **Deploy desde este directorio**
```bash
cd handball-goal-counter
vercel --prod
```

### Opción 2: Deploy desde GitHub

1. Sube este proyecto a un repositorio de GitHub
2. Ve a [vercel.com](https://vercel.com)
3. Click en "Import Project"
4. Selecciona tu repositorio
5. Configura las variables de entorno:
   - `PYTHON_VERSION`: `3.11`
   - `ENABLE_SUPERPOWERS`: `1`
6. Click en "Deploy"

## 📦 Estructura del Proyecto

```
handball-goal-counter/
├── api/
│   └── analyze-video.js       # API endpoint principal
├── python/
│   ├── video_processor.py     # Procesador principal
│   ├── youtube_extractor.py   # Descarga de YouTube (yt-dlp)
│   ├── tracking_engine.py     # YOLOv8 + DeepSORT
│   └── goal_detector.py       # Lógica de detección de goles
├── config/
│   └── handball_config.json   # Configuración del sistema
├── public/
│   └── models/
│       └── yolov8n.pt        # Modelo YOLOv8 (descargar)
├── vercel.json               # Configuración de Vercel
├── package.json              # Dependencias Node.js
└── requirements.txt          # Dependencias Python
```

## 🔧 Configuración

### Descargar el Modelo YOLOv8

Antes de deployar, descarga el modelo pre-entrenado:

```bash
cd public/models
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

### Variables de Entorno

Configura estas variables en Vercel:

- `PYTHON_VERSION`: `3.11`
- `ENABLE_SUPERPOWERS`: `1`

## 📡 Uso de la API

### Endpoint

```
POST /api/analyze-video
```

### Request Body

```json
{
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

### Ejemplo con cURL

```bash
curl -X POST https://tu-proyecto.vercel.app/api/analyze-video \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### Respuesta Exitosa

```json
{
  "success": true,
  "data": {
    "video_url": "https://www.youtube.com/watch?v=...",
    "total_frames": 4500,
    "goals_detected": 7,
    "goal_timestamps": [45.2, 89.7, 134.5, 201.3, 267.8, 312.4, 389.1],
    "processing_time": 187.34,
    "confidence_scores": [0.89, 0.92, 0.87, 0.94, 0.91, 0.88, 0.93],
    "team_scores": {
      "team_a": 4,
      "team_b": 3,
      "unknown": 0
    },
    "metadata": {
      "total_frames": 4500,
      "processed_frames": 2250,
      "fps": 30,
      "duration_seconds": 150,
      "frame_skip": 2
    }
  },
  "timestamp": "2026-04-27T14:30:00.000Z"
}
```

## 🧪 Testing Local

### 1. Instalar Dependencias

```bash
# Node.js
npm install

# Python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Ejecutar Localmente

```bash
# Iniciar servidor de desarrollo
vercel dev

# En otra terminal, hacer request
curl -X POST http://localhost:3000/api/analyze-video \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

### 3. Test del Procesador Python Directamente

```bash
python python/video_processor.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

## ⚙️ Configuración Avanzada

### Ajustar Zonas de Portería

Edita `config/handball_config.json`:

```json
{
  "goal_zones": [
    {
      "name": "left_goal",
      "team": "team_a",
      "coordinates": [
        [x1, y1],
        [x2, y2],
        [x3, y3],
        [x4, y4]
      ]
    }
  ]
}
```

### Optimizar Performance

- `frame_skip`: Mayor valor = más rápido pero menos preciso
- `confidence_threshold`: Mayor valor = menos detecciones falsas
- `max_video_duration`: Limitar duración del video

## 🔗 Repositorios Integrados

1. **Superpowers** (Orquestación): `github.com/vercel/superpowers`
2. **YOLOv8**: `github.com/ultralytics/ultralytics`
3. **yt-dlp**: `github.com/yt-dlp/yt-dlp`
4. **DeepSORT**: Implementación custom basada en paper original

## 📊 Limitaciones de Vercel

- **Timeout máximo**: 300 segundos (5 minutos)
- **Memoria máxima**: 3008 MB
- **Storage temporal**: 512 MB en `/tmp`
- **Tamaño de video**: Máximo 100 MB

## 🐛 Troubleshooting

### Error: "yt-dlp not found"

```bash
pip install yt-dlp
```

### Error: "Model not found"

Descarga el modelo YOLOv8:
```bash
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -P public/models/
```

### Error: "Timeout"

Reduce la duración del video o incrementa `frame_skip` en la configuración.

## 📝 Licencia

MIT License

## 👨‍💻 Autor

Senior Software Architect

---

**¡Éxito con tu deploy! 🚀**
