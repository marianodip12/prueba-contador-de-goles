# 🚀 INSTRUCCIONES RÁPIDAS

## ❌ Error que estabas teniendo:
> "The 'functions' property cannot be used in conjunction with the 'builds' property"

## ✅ Solución aplicada:
Se removió la propiedad `builds` del `vercel.json`. Ahora solo usa `functions`.

---

## 📝 Pasos para Deploy

### 1. Subir archivos a GitHub

**Opción A: Usando GitHub Web**
1. Ve a tu repo: https://github.com/marianodip12/prueba-contador-de-goles
2. Click en "Add file" → "Upload files"
3. Arrastra TODOS los archivos del ZIP descomprimido
4. **IMPORTANTE**: Marca "Replace existing files" si te pregunta
5. Commit message: "Fix vercel.json - remove builds property"
6. Click en "Commit changes"

**Opción B: Usando Git desde terminal**
```bash
# Descomprimir el ZIP
unzip handball-goal-counter.zip
cd handball-goal-counter

# Inicializar git si no existe
git init
git remote add origin https://github.com/marianodip12/prueba-contador-de-goles.git

# Agregar todos los archivos
git add .
git commit -m "Fix vercel.json - remove builds property"
git push -u origin main --force
```

### 2. Volver a Vercel

1. Ve a https://vercel.com/new
2. Importa el repositorio `marianodip12/prueba-contador-de-goles`
3. **Project Name**: `prueba-contador-de-goles` (o el que quieras)
4. **Framework Preset**: Next.js (debería detectarse automáticamente)
5. **Root Directory**: déjalo en blanco o pon `./`

### 3. Variables de Entorno (Opcional)

Click en "Environment Variables" y agrega:
- `PYTHON_VERSION` = `3.11`

### 4. Click en "Deploy"

¡Listo! Vercel construirá tu proyecto automáticamente.

---

## 🎯 Después del Deploy

### Probar la aplicación
1. Vercel te dará una URL como: `https://prueba-contador-de-goles-xxxx.vercel.app`
2. Abre la URL en el navegador
3. Verás un formulario donde puedes pegar una URL de YouTube
4. Click en "Analizar Video"

### Probar el API directamente
```bash
curl -X POST https://tu-app.vercel.app/api/analyze-video \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

---

## ⚠️ IMPORTANTE: Limitaciones

Este proyecto usa Python con dependencias pesadas (YOLOv8, OpenCV, PyTorch) que **NO funcionan completamente en Vercel** porque:

1. Vercel Serverless Functions tiene límite de **50MB** de tamaño
2. PyTorch + YOLOv8 pesan más de 500MB
3. El modelo YOLOv8 también pesa varios MB

### Soluciones recomendadas para producción:

**Opción 1: Usar Vercel solo para el frontend**
- Frontend en Vercel (Next.js)
- Backend en otro servicio que soporte Python (Railway, Render, AWS Lambda con layers)

**Opción 2: Usar API externa**
- Procesar videos en un servidor dedicado
- Vercel solo recibe la URL y reenvía la petición

**Opción 3: Usar Replicate.com o Hugging Face**
- Servicios que ya tienen YOLOv8 listo para usar
- Solo necesitas hacer requests HTTP

---

## 🐛 Si el deploy falla

Errores comunes:

### "Module not found"
- Verifica que `package.json` tenga las dependencias correctas
- En Vercel, ve a Settings → General → Build & Development Settings
- Build Command: `npm install && npm run build`

### "Function size too large"
- Las dependencias de Python son muy pesadas para Vercel
- Considera usar Railway o Render en su lugar

### "Timeout"
- Aumenta el `maxDuration` en `vercel.json` (máx 300 en plan Pro)

---

## 📞 Necesitas ayuda?

Si tienes problemas, verifica:
1. ✅ Todos los archivos están en GitHub
2. ✅ El `vercel.json` no tiene la propiedad `builds`
3. ✅ El `package.json` tiene las dependencias correctas
4. ✅ La estructura `/pages/api/` existe
