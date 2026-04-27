#!/usr/bin/env python3
"""Extractor de YouTube usando yt-dlp como librería Python"""

import os
from typing import Optional


class YouTubeExtractor:
    
    def __init__(self):
        try:
            import yt_dlp
            self.yt_dlp = yt_dlp
        except ImportError:
            raise ImportError("yt-dlp no está instalado. Ejecuta: pip install yt-dlp")
    
    def download(
        self, 
        url: str, 
        output_path: str = "/tmp",
        max_duration: int = 180,
        quality: str = "worst"
    ) -> Optional[str]:
        """Descarga video usando yt-dlp como librería Python (más confiable)"""
        
        output_template = os.path.join(output_path, "video.%(ext)s")
        
        ydl_opts = {
            'format': f'{quality}[ext=mp4]/worst[ext=mp4]/worst',
            'outtmpl': output_template,
            'noplaylist': True,
            'max_filesize': 100 * 1024 * 1024,  # 100MB
            'quiet': True,
            'no_warnings': True,
            'no_progress': True,
            'socket_timeout': 30,
        }
        
        try:
            with self.yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Obtener info primero para validar duración
                info = ydl.extract_info(url, download=False)
                
                duration = info.get('duration', 0)
                if duration > max_duration:
                    print(f"⚠️  Video muy largo: {duration}s > {max_duration}s", flush=True)
                
                # Descargar
                ydl.download([url])
            
            # Buscar el archivo descargado
            for file in os.listdir(output_path):
                if file.startswith("video."):
                    full_path = os.path.join(output_path, file)
                    size_mb = os.path.getsize(full_path) / (1024 * 1024)
                    print(f"✅ Descargado: {file} ({size_mb:.1f}MB)", flush=True)
                    return full_path
            
            return None
            
        except Exception as e:
            print(f"❌ Error en yt-dlp: {e}", flush=True)
            return None
