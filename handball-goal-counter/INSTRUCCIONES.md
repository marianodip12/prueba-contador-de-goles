# 🚀 PASOS RÁPIDOS PARA QUE FUNCIONE EN RENDER

## ❌ Tu error actual:
> "Python process exited with code 1"

Esto pasa porque faltan dependencias o el modelo YOLOv8.

## ✅ Solución: Este nuevo ZIP

He creado una versión **completamente reescrita** específicamente para Render que:

1. ✅ Usa **Flask** (más simple que Next.js + Python)
2. ✅ **Descarga automáticamente** el modelo YOLOv8 al hacer build
3. ✅ Usa **yt-dlp como librería Python** (no como comando shell)
4. ✅ Tiene un **endpoint de diagnóstico** para ver qué falla
5. ✅ Configuración optimizada para el plan Free de Render

---

## 📝 PASOS EXACTOS

### 1️⃣ Subir archivos a GitHub

**Borra TODO** lo que tienes en el repo `marianodip12/prueba-contador-de-goles` y sube los archivos de este ZIP.

**Opción rápida desde la web:**
1. Ve a tu repo en GitHub
2. Click en cada archivo y bórralos (o usa Git para borrar todo)
3. Click en "Add file" → "Upload files"
4. Arrastra TODOS los archivos descomprimidos del ZIP
5. Commit: "Reescritura completa para Render"

**Opción terminal:**
```bash
# Borrar todo del repo local
cd prueba-contador-de-goles
rm -rf *

# Copiar nuevos archivos
cp -r /ruta/al/handball-render/* .
cp /ruta/al/handball-render/.gitignore .

# Push
git add .
git commit -m "Reescritura completa para Render"
git push origin main --force
```

### 2️⃣ Configurar Render

1. Ve a https://dashboard.render.com
2. Si ya tienes el servicio creado, ve a **Settings** y modifica:

   - **Build Command**: `bash build.sh`
   - **Start Command**: `gunicorn app:app --timeout 600 --workers 1 --threads 2`

3. Si NO lo has creado:
   - "New +" → "Web Service"
   - Conecta el repo
   - Usa los comandos de arriba

### 3️⃣ Variables de Entorno

En **Environment** (Render dashboard):

```
PYTHON_VERSION = 3.11.0
FLASK_DEBUG = false
```

### 4️⃣ Deploy

Click en "Manual Deploy" → "Deploy latest commit"

**Esto puede tardar 5-10 minutos** porque:
- Instala PyTorch (~500MB)
- Instala OpenCV
- Descarga el modelo YOLOv8 (~6MB)

---

## 🔍 CÓMO VERIFICAR QUE FUNCIONA

Una vez deployed, visita en este orden:

### 1. Health Check
```
https://prueba-contador-de-goles-1.onrender.com/health
```
Debería responder:
```json
{"status": "healthy", "service": "handball-goal-counter"}
```

### 2. Verificar Dependencias (¡IMPORTANTE!)
```
https://prueba-contador-de-goles-1.onrender.com/api/check-deps
```

Esto te dirá exactamente qué está instalado:
```json
{
  "opencv": true,
  "numpy": true,
  "ultralytics": true,
  "yt_dlp": true,
  "model_file": true,
  "errors": []
}
```

Si algo dice `false`, ese es el problema. Mírame el JSON que sale ahí y te ayudo.

### 3. Probar la UI
```
https://prueba-contador-de-goles-1.onrender.com/
```

---

## ⚠️ NOTAS IMPORTANTES SOBRE RENDER FREE

1. **Se duerme después de 15 minutos** sin uso
2. **Tarda ~30 segundos en despertar** la primera vez
3. **Solo 512MB de RAM** - YOLOv8 puede tener problemas con videos grandes
4. **Build puede tardar 10 minutos** la primera vez

### Si tienes problemas de memoria:

Edita `config/handball_config.json`:
```json
{
  "frame_skip": 10,        // Procesar menos frames
  "max_video_duration": 60 // Solo 1 minuto
}
```

---

## 🎯 SI AÚN NO FUNCIONA

Mándame:

1. **Los logs de Render** (Dashboard → Tu servicio → Logs)
2. **El JSON de** `/api/check-deps`
3. **El JSON del error** que aparece en pantalla

Con eso te lo soluciono al toque. 💪

---

## 📞 Contacto rápido para debug

Si ves un error específico, búscalo aquí:

| Error | Solución |
|-------|----------|
| "ImportError: No module named 'cv2'" | Falta OpenCV - revisa requirements.txt |
| "ImportError: No module named 'ultralytics'" | Falta YOLOv8 - revisa requirements.txt |
| "FileNotFoundError: yolov8n.pt" | El build.sh no descargó el modelo |
| "Out of memory" | Sube a plan Starter o reduce frame_skip |
| "Timeout" | Aumenta --timeout en start command |
| "yt-dlp error" | Video privado o restringido geográficamente |
