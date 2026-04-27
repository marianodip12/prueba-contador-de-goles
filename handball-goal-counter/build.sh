#!/usr/bin/env bash
# Script de build para Render
# Instala dependencias y descarga el modelo YOLOv8

set -e

echo "🔄 Actualizar pip..."
pip install --upgrade pip setuptools wheel

echo "📦 Instalando dependencias base..."
pip install numpy==1.24.3 Pillow==10.1.0

echo "📦 Instalando OpenCV..."
pip install opencv-python-headless==4.8.0.75 --no-cache-dir

echo "📦 Instalando Flask..."
pip install Flask==3.0.0 gunicorn==21.2.0

echo "📦 Instalando yt-dlp..."
pip install yt-dlp==2023.11.16

echo "📦 Instalando PyTorch..."
pip install torch==2.1.0 torchvision==0.16.0 --no-cache-dir

echo "📦 Instalando YOLOv8..."
pip install ultralytics==8.0.200

echo "📥 Descargando modelo YOLOv8..."
mkdir -p models

if [ ! -f "models/yolov8n.pt" ]; then
    echo "⏳ Descargando yolov8n.pt (esto puede tardar 1-2 minutos)..."
    wget --no-verbose -O models/yolov8n.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
    echo "✅ Modelo descargado correctamente"
else
    echo "✅ Modelo ya existe"
fi

echo "✅ Build completado"
