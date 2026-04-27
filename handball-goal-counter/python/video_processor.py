#!/usr/bin/env python3
"""
Sistema Principal de Procesamiento de Video
Integra todos los componentes: yt-dlp, YOLOv8, DeepSORT, SportSense
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import cv2
import numpy as np
from dataclasses import dataclass, asdict

# Importaciones de los módulos integrados
from youtube_extractor import YouTubeExtractor
from tracking_engine import TrackingEngine
from goal_detector import GoalDetector


@dataclass
class ProcessingResult:
    """Resultado del procesamiento de video"""
    video_url: str
    total_frames: int
    goals_detected: int
    goal_timestamps: List[float]
    processing_time: float
    confidence_scores: List[float]
    team_scores: Dict[str, int]
    metadata: Dict


class HandballVideoProcessor:
    """
    Procesador principal que orquesta todos los componentes
    """
    
    def __init__(self, config_path: str = "config/handball_config.json"):
        """
        Inicializa el procesador con la configuración
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        self.config = self._load_config(config_path)
        
        # Inicializar componentes
        self.youtube_extractor = YouTubeExtractor()
        self.tracking_engine = TrackingEngine(
            model_path=self.config.get("model_path", "public/models/yolov8n.pt"),
            confidence_threshold=self.config.get("confidence_threshold", 0.5)
        )
        self.goal_detector = GoalDetector(
            goal_zones=self.config.get("goal_zones", []),
            min_confidence=self.config.get("min_goal_confidence", 0.7)
        )
        
        self.temp_dir = tempfile.mkdtemp(prefix="handball_")
        
    def _load_config(self, config_path: str) -> Dict:
        """Carga la configuración desde JSON"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Config no encontrada en {config_path}, usando defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Configuración por defecto para handball"""
        return {
            "model_path": "public/models/yolov8n.pt",
            "confidence_threshold": 0.5,
            "min_goal_confidence": 0.7,
            "goal_zones": [
                {
                    "name": "left_goal",
                    "team": "team_a",
                    "coordinates": [[50, 200], [250, 200], [250, 500], [50, 500]]
                },
                {
                    "name": "right_goal",
                    "team": "team_b",
                    "coordinates": [[1670, 200], [1870, 200], [1870, 500], [1670, 500]]
                }
            ],
            "frame_skip": 2,
            "max_video_duration": 300,
            "target_fps": 15
        }
    
    def process_video(self, youtube_url: str) -> ProcessingResult:
        """
        Procesa un video de YouTube completo
        
        Args:
            youtube_url: URL del video de YouTube
            
        Returns:
            ProcessingResult con los resultados del análisis
        """
        import time
        start_time = time.time()
        
        print(f"🎯 Iniciando procesamiento: {youtube_url}")
        
        # PASO 1: Extraer video de YouTube
        print("📥 Paso 1: Descargando video de YouTube...")
        video_path = self.youtube_extractor.download(
            youtube_url, 
            output_path=self.temp_dir,
            max_duration=self.config.get("max_video_duration", 300)
        )
        
        if not video_path or not os.path.exists(video_path):
            raise RuntimeError("Error al descargar el video")
        
        print(f"✅ Video descargado: {video_path}")
        
        # PASO 2: Procesar video frame por frame
        print("🎬 Paso 2: Procesando frames con YOLOv8 + DeepSORT...")
        goals, metadata = self._process_frames(video_path)
        
        # PASO 3: Calcular estadísticas
        print("📊 Paso 3: Calculando estadísticas...")
        team_scores = self._calculate_team_scores(goals)
        
        processing_time = time.time() - start_time
        
        result = ProcessingResult(
            video_url=youtube_url,
            total_frames=metadata.get("total_frames", 0),
            goals_detected=len(goals),
            goal_timestamps=[g["timestamp"] for g in goals],
            processing_time=processing_time,
            confidence_scores=[g["confidence"] for g in goals],
            team_scores=team_scores,
            metadata=metadata
        )
        
        # Limpiar archivos temporales
        self._cleanup()
        
        print(f"✅ Procesamiento completado en {processing_time:.2f}s")
        print(f"⚽ Goles detectados: {len(goals)}")
        
        return result
    
    def _process_frames(self, video_path: str) -> Tuple[List[Dict], Dict]:
        """
        Procesa todos los frames del video
        
        Returns:
            Tuple de (lista de goles, metadata)
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise RuntimeError(f"No se pudo abrir el video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_skip = self.config.get("frame_skip", 2)
        
        goals = []
        frame_count = 0
        processed_count = 0
        
        print(f"📹 Video: {total_frames} frames @ {fps} FPS")
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Saltar frames para optimizar
            if frame_count % frame_skip != 0:
                frame_count += 1
                continue
            
            # Tracking con YOLOv8 + DeepSORT
            detections = self.tracking_engine.track(frame)
            
            # Detectar goles
            goal_event = self.goal_detector.check_goal(
                detections=detections,
                frame=frame,
                timestamp=frame_count / fps
            )
            
            if goal_event:
                goals.append(goal_event)
                print(f"⚽ GOL detectado en {goal_event['timestamp']:.2f}s - "
                      f"Confianza: {goal_event['confidence']:.2%}")
            
            processed_count += 1
            
            # Progress
            if processed_count % 100 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"⏳ Progreso: {progress:.1f}% ({frame_count}/{total_frames})")
            
            frame_count += 1
        
        cap.release()
        
        metadata = {
            "total_frames": total_frames,
            "processed_frames": processed_count,
            "fps": fps,
            "duration_seconds": total_frames / fps,
            "frame_skip": frame_skip
        }
        
        return goals, metadata
    
    def _calculate_team_scores(self, goals: List[Dict]) -> Dict[str, int]:
        """Calcula puntajes por equipo"""
        scores = {"team_a": 0, "team_b": 0, "unknown": 0}
        
        for goal in goals:
            team = goal.get("team", "unknown")
            scores[team] = scores.get(team, 0) + 1
        
        return scores
    
    def _cleanup(self):
        """Limpia archivos temporales"""
        import shutil
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"🧹 Limpieza completada: {self.temp_dir}")
        except Exception as e:
            print(f"⚠️ Error en limpieza: {e}")


def main(youtube_url: str) -> str:
    """
    Función principal para ejecutar desde Vercel/Superpowers
    
    Args:
        youtube_url: URL del video de YouTube
        
    Returns:
        JSON string con los resultados
    """
    try:
        processor = HandballVideoProcessor()
        result = processor.process_video(youtube_url)
        
        # Convertir a JSON
        output = asdict(result)
        return json.dumps(output, indent=2)
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "type": type(e).__name__,
            "success": False
        }
        return json.dumps(error_result, indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python video_processor.py <youtube_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    result_json = main(url)
    print(result_json)
