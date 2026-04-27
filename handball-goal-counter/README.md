# 🏐 Handball Goal Counter - Versión Render

Sistema automatizado de detección de goles desde videos de YouTube optimizado para **Render.com**.

## 🚀 Deploy en Render

### Paso 1: Subir a GitHub

Reemplaza TODOS los archivos en tu repositorio `marianodip12/prueba-contador-de-goles` con los de este ZIP.

### Paso 2: Configurar en Render

1. Ve a https://dashboard.render.com
2. Click en **"New +" → "Web Service"**
3. Conecta tu repositorio de GitHub
4. Configura así:

**Build & Deploy Settings:**

| Campo | Valor |
|-------|-------|
| **Name** | `handball-goal-counter` |
| **Region** | Oregon (USA) o Frankfurt (EU) |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `bash build.sh` |
| **Start Command** | `gunicorn app:app --timeout 600 --workers 1 --threads 2` |
| **Plan** | `Free` (puedes empezar) |

### Paso 3: Variables de Entorno

En la sección "Environment" agrega:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `FLASK_DEBUG` | `false` |

### Paso 4: Click en "Create Web Service"

Render hará:
1. ✅ Instalar dependencias Python
2. ✅ Descargar el modelo YOLOv8 automáticamente
3. ✅ Iniciar el servidor

## 🔍 Verificar que todo funciona

Después del deploy, visita estas URLs:

1. **Página principal**: `https://tu-app.onrender.com/`
2. **Health check**: `https://tu-app.onrender.com/health`
3. **Verificar dependencias**: `https://tu-app.onrender.com/api/check-deps`

El endpoint `/api/check-deps` te dirá exactamente qué está instalado y qué falta.

## ⚠️ Importante: Plan Free de Render

- ✅ 750 horas/mes gratis
- ⚠️ Se "duerme" después de 15 min de inactividad
- ⚠️ Tarda ~30s en despertar la primera vez
- ⚠️ Solo 512MB de RAM (puede ser limitante para YOLOv8)

**Recomendación**: Si vas a procesar videos seguido, considera el plan **Starter ($7/mes)** que tiene más RAM.

## 📡 API Endpoints

### `POST /api/analyze-video`

```json
{
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "data": {
    "goals_detected": 5,
    "goal_timestamps": [12.5, 45.2, 78.9, 102.3, 145.6],
    "team_scores": {
      "team_a": 3,
      "team_b": 2
    },
    "processing_time": 187.34
  }
}
```

### `GET /api/check-deps`

Verifica que todas las dependencias estén instaladas correctamente.

### `GET /health`

Health check para monitoreo.

## 🐛 Troubleshooting

### Error: "Python process exited with code 1"
Visita `/api/check-deps` para ver qué dependencia falta.

### Error: "Out of memory"
- Reduce `frame_skip` a 10 en `config/handball_config.json`
- Considera upgrade a plan Starter

### Error: "Timeout"
- El video es muy largo, reduce `max_video_duration`
- Aumenta `--timeout` en el start command

### El servicio no responde
- Render Free se duerme después de 15 min
- La primera request tarda ~30s en despertar
- Hacer un GET a `/health` para despertarlo

## 📊 Estructura del Proyecto

```
handball-render/
├── app.py                      # Aplicación Flask principal
├── build.sh                    # Script de build (descarga YOLOv8)
├── render.yaml                 # Configuración de Render
├── requirements.txt            # Dependencias Python
├── runtime.txt                 # Versión de Python
├── python/
│   ├── video_processor.py     # Procesador principal
│   ├── youtube_extractor.py   # yt-dlp wrapper
│   ├── tracking_engine.py     # YOLOv8 + DeepSORT
│   └── goal_detector.py       # Lógica de goles
├── templates/
│   └── index.html             # UI principal
├── config/
│   └── handball_config.json   # Configuración
└── models/                    # YOLOv8 (descargado en build)
```

## 🎯 Diferencias con la versión Vercel

| Característica | Vercel | Render |
|---------------|--------|--------|
| Python pesado | ❌ Limitado a 50MB | ✅ Sin límite |
| YOLOv8 | ❌ No funciona | ✅ Funciona |
| OpenCV | ❌ Muy pesado | ✅ Funciona |
| Tiempo de ejecución | 300s máx | Ilimitado |
| Costo | Free tier limitado | Free tier 750h/mes |

---

**Este proyecto está específicamente optimizado para Render** y soluciona los errores que tenías en Vercel.
