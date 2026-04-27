# 🏐 Handball Goal Counter

Sistema automatizado de detección de goles desde videos de YouTube.

## 🚀 Deploy en Vercel

### Paso 1: Reemplazar archivos en GitHub

Sube TODOS los archivos de este ZIP a tu repositorio `marianodip12/prueba-contador-de-goles`, **reemplazando los existentes**.

### Paso 2: Configurar Variables de Entorno en Vercel

En el panel de Vercel, agrega:
- `PYTHON_VERSION` = `3.11`
- `ENABLE_SUPERPOWERS` = `1`

### Paso 3: Deploy

Click en **Deploy** en Vercel.

## 📋 Cambios Importantes

✅ **vercel.json corregido** - Removida la propiedad `builds` que causaba conflicto
✅ **Estructura Next.js correcta** - API routes en `/pages/api/`
✅ **UI agregada** - Página principal con formulario para probar

## 📡 API

**Endpoint:** `POST /api/analyze-video`

**Request:**
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

## ⚠️ Notas

- El modelo YOLOv8 (`yolov8n.pt`) debe descargarse manualmente y agregarse a `public/models/`
- Vercel tiene límite de 300s para funciones serverless
- Memoria máxima: 3008MB
