# 🚀 INSTRUCCIONES DE DEPLOYMENT - VERCEL

## Paso 1: Preparar el Proyecto

1. **Descomprimir el ZIP**
   ```bash
   unzip handball-goal-counter.zip
   cd handball-goal-counter
   ```

2. **Descargar el Modelo YOLOv8** (IMPORTANTE)
   ```bash
   cd public/models
   wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
   cd ../..
   ```
   
   O descárgalo manualmente y colócalo en `public/models/yolov8n.pt`

## Paso 2: Deploy en Vercel

### Opción A: Deploy Directo (Más Rápido)

1. **Instalar Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login en Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

4. **Seguir las instrucciones en pantalla:**
   - Set up and deploy? → Y
   - Which scope? → Selecciona tu cuenta
   - Link to existing project? → N
   - Project name? → handball-goal-counter (o el que prefieras)
   - Directory? → ./ (presiona Enter)
   - Override settings? → N

### Opción B: Deploy desde GitHub

1. **Crear repositorio en GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Handball Goal Counter"
   git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
   git push -u origin main
   ```

2. **Importar en Vercel**
   - Ve a https://vercel.com/new
   - Click en "Import Git Repository"
   - Selecciona tu repositorio
   - Click en "Import"

3. **Configurar Variables de Entorno**
   - `PYTHON_VERSION`: `3.11`
   - `ENABLE_SUPERPOWERS`: `1`

4. **Deploy**
   - Click en "Deploy"

## Paso 3: Verificar el Deploy

1. **Esperar a que termine el build** (puede tardar 3-5 minutos)

2. **Visitar la URL de tu proyecto**
   ```
   https://tu-proyecto.vercel.app
   ```

3. **Probar el endpoint**
   ```bash
   curl -X POST https://tu-proyecto.vercel.app/api/analyze-video \
     -H "Content-Type: application/json" \
     -d '{"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
   ```

## Paso 4: Configuración Adicional (Opcional)

### Ajustar las Zonas de Portería

Edita `config/handball_config.json` y modifica las coordenadas de las zonas:

```json
{
  "goal_zones": [
    {
      "name": "left_goal",
      "team": "team_a",
      "coordinates": [
        [50, 200],    // Esquina superior izquierda
        [250, 200],   // Esquina superior derecha
        [250, 500],   // Esquina inferior derecha
        [50, 500]     // Esquina inferior izquierda
      ]
    }
  ]
}
```

### Optimizar Performance

En `config/handball_config.json`:
- `frame_skip`: Aumentar para procesar más rápido (ej: 3 o 4)
- `confidence_threshold`: Aumentar para menos falsos positivos (ej: 0.6 o 0.7)
- `max_video_duration`: Limitar duración máxima del video

## 🧪 Testing

### Test Local

```bash
# Instalar dependencias
npm install
pip install -r requirements.txt

# Iniciar servidor local
vercel dev

# En otra terminal
curl -X POST http://localhost:3000/api/analyze-video \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

### Test del Procesador Python Directo

```bash
python python/video_processor.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

## 📊 Monitoreo

Ver logs en tiempo real:
```bash
vercel logs
```

## ⚠️ Troubleshooting

### Error: "Model not found"
- Asegúrate de haber descargado `yolov8n.pt` en `public/models/`

### Error: "yt-dlp not found"
- Vercel instalará automáticamente desde `requirements.txt`
- Si falla, verifica que `yt-dlp==2023.11.16` esté en requirements.txt

### Error: "Function timeout"
- Reduce `max_video_duration` en la configuración
- Aumenta `frame_skip` para procesar menos frames

### Error: "Memory limit exceeded"
- Usa videos más cortos (máx 5 minutos)
- Aumenta `frame_skip` a 3 o 4

## 📞 Soporte

Para más información, consulta:
- README.md en el proyecto
- Documentación de Vercel: https://vercel.com/docs
- GitHub Issues (si lo subes a GitHub)

---

**¡Tu API está lista para producción! 🎉**
