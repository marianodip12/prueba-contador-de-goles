#!/usr/bin/env python3
"""Extractor de YouTube usando yt-dlp"""

import os
import subprocess
import shutil
from typing import Optional


class YouTubeExtractor:
    
    def __init__(self):
        self.yt_dlp_path = self._find_yt_dlp()
    
    def _find_yt_dlp(self) -> str:
        yt_dlp = shutil.which("yt-dlp")
        if yt_dlp:
            return yt_dlp
        
        result = subprocess.run(
            ["which", "yt-dlp"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        
        raise RuntimeError("yt-dlp no encontrado")
    
    def download(
        self, 
        url: str, 
        output_path: str = "/tmp",
        max_duration: int = 300,
        quality: str = "worst"
    ) -> Optional[str]:
        output_template = os.path.join(output_path, "video.%(ext)s")
        
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
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                return None
            
            for file in os.listdir(output_path):
                if file.startswith("video."):
                    return os.path.join(output_path, file)
            
            return None
            
        except subprocess.TimeoutExpired:
            return None
        except Exception:
            return None
