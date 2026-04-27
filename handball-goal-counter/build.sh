#!/usr/bin/env bash
# Script de build para Render
# Instala dependencias y descarga el modelo YOLOv8

set -e

echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📥 Descargando modelo YOLOv8..."
mkdir -p models

if [ ! -f "models/yolov8n.pt" ]; then
    wget -O models/yolov8n.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
    echo "✅ Modelo descargado correctamente"
else
    echo "✅ Modelo ya existe"
fi

echo "🔧 Verificando instalación de yt-dlp..."
which yt-dlp || pip install yt-dlp

echo "✅ Build completado"
