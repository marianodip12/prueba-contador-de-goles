#!/usr/bin/env python3
"""
Extractor de YouTube usando yt-dlp
Integración del repositorio: github.com/yt-dlp/yt-dlp
"""

import os
import subprocess
from pathlib import Path
from typing import Optional


class YouTubeExtractor:
    """Wrapper para yt-dlp optimizado para Vercel"""
    
    def __init__(self):
        self.yt_dlp_path = self._find_yt_dlp()
    
    def _find_yt_dlp(self) -> str:
        """Encuentra el ejecutable de yt-dlp"""
        # Intentar encontrar en PATH
        result = subprocess.run(
            ["which", "yt-dlp"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        
        # Intentar instalación local de Python
        import shutil
        yt_dlp = shutil.which("yt-dlp")
        
        if yt_dlp:
            return yt_dlp
        
        raise RuntimeError("yt-dlp no encontrado. Ejecuta: pip install yt-dlp")
    
    def download(
        self, 
        url: str, 
        output_path: str = "/tmp",
        max_duration: int = 300,
        quality: str = "worst"
    ) -> Optional[str]:
        """
        Descarga un video de YouTube
        
        Args:
            url: URL del video
            output_path: Directorio de salida
            max_duration: Duración máxima en segundos
            quality: Calidad del video (worst/best)
            
        Returns:
            Ruta al archivo descargado o None si falla
        """
        output_template = os.path.join(output_path, "video.%(ext)s")
        
        # Comando yt-dlp optimizado para Vercel
        cmd = [
            self.yt_dlp_path,
            url,
            "-f", f"{quality}[ext=mp4]/worst",
            "-o", output_template,
            "--no-playlist",
            "--max-filesize", "100M",
            "--no-warnings",
            "--quiet",
            "--no-progress"
        ]
        
        print(f"🔽 Descargando: {url}")
        print(f"📁 Destino: {output_path}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                print(f"❌ Error en yt-dlp: {result.stderr}")
                return None
            
            # Buscar el archivo descargado
            for file in os.listdir(output_path):
                if file.startswith("video."):
                    full_path = os.path.join(output_path, file)
                    print(f"✅ Descargado: {full_path}")
                    return full_path
            
            return None
            
        except subprocess.TimeoutExpired:
            print("⏱️ Timeout al descargar video")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
