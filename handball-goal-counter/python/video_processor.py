#!/usr/bin/env python3
"""
Sistema Principal de Procesamiento de Video
"""

import os
import sys
import json
import tempfile
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

import cv2
import numpy as np

from youtube_extractor import YouTubeExtractor
from tracking_engine import TrackingEngine
from goal_detector import GoalDetector


@dataclass
class ProcessingResult:
    video_url: str
    total_frames: int
    goals_detected: int
    goal_timestamps: List[float]
    processing_time: float
    confidence_scores: List[float]
    team_scores: Dict[str, int]
    metadata: Dict


class HandballVideoProcessor:
    
    def __init__(self):
        # Buscar config en varios lugares
        config_paths = [
            "config/handball_config.json",
            os.path.join(os.path.dirname(__file__), "..", "config", "handball_config.json"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "handball_config.json"),
        ]
        
        self.config = self._load_config(config_paths)
        
        # Buscar el modelo
        model_path = self._find_model()
        
        print(f"📂 Modelo: {model_path}", flush=True)
        print(f"⚙️  Config cargada: {len(self.config)} keys", flush=True)
        
        self.youtube_extractor = YouTubeExtractor()
        self.tracking_engine = TrackingEngine(
            model_path=model_path,
            confidence_threshold=self.config.get("confidence_threshold", 0.5)
        )
        self.goal_detector = GoalDetector(
            goal_zones=self.config.get("goal_zones", []),
            min_confidence=self.config.get("min_goal_confidence", 0.7)
        )
        
        self.temp_dir = tempfile.mkdtemp(prefix="handball_")
        print(f"📁 Temp dir: {self.temp_dir}", flush=True)
    
    def _find_model(self) -> str:
        """Busca el modelo YOLOv8 en varias ubicaciones"""
        possible_paths = [
            "models/yolov8n.pt",
            "./models/yolov8n.pt",
            os.path.join(os.path.dirname(__file__), "..", "models", "yolov8n.pt"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models", "yolov8n.pt"),
            "yolov8n.pt",  # Directorio actual
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return os.path.abspath(path)
        
        # Si no existe, ultralytics lo descarga automáticamente
        return "yolov8n.pt"
    
    def _load_config(self, paths: List[str]) -> Dict:
        for path in paths:
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                continue
        
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        return {
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
            "frame_skip": 5,  # Más agresivo para Render free tier
            "max_video_duration": 180,  # 3 minutos máximo
        }
    
    def process_video(self, youtube_url: str) -> ProcessingResult:
        import time
        start_time = time.time()
        
        print(f"📥 Descargando video...", flush=True)
        video_path = self.youtube_extractor.download(
            youtube_url, 
            output_path=self.temp_dir,
            max_duration=self.config.get("max_video_duration", 180)
        )
        
        if not video_path or not os.path.exists(video_path):
            raise RuntimeError("Error al descargar el video de YouTube")
        
        print(f"✅ Video descargado: {video_path}", flush=True)
        print(f"🎬 Procesando frames...", flush=True)
        
        goals, metadata = self._process_frames(video_path)
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
        
        self._cleanup()
        
        print(f"✅ Completado en {processing_time:.2f}s - {len(goals)} goles", flush=True)
        return result
    
    def _process_frames(self, video_path: str) -> Tuple[List[Dict], Dict]:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise RuntimeError(f"No se pudo abrir el video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_skip = self.config.get("frame_skip", 5)
        
        print(f"📹 {total_frames} frames @ {fps} FPS (skip={frame_skip})", flush=True)
        
        goals = []
        frame_count = 0
        processed_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_skip != 0:
                frame_count += 1
                continue
            
            try:
                detections = self.tracking_engine.track(frame)
                goal_event = self.goal_detector.check_goal(
                    detections=detections,
                    frame=frame,
                    timestamp=frame_count / fps
                )
                
                if goal_event:
                    goals.append(goal_event)
                    print(f"⚽ GOL en {goal_event['timestamp']:.2f}s", flush=True)
            except Exception as e:
                print(f"⚠️  Error frame {frame_count}: {e}", flush=True)
            
            processed_count += 1
            
            if processed_count % 50 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"⏳ {progress:.1f}% ({processed_count} frames)", flush=True)
            
            frame_count += 1
        
        cap.release()
        
        return goals, {
            "total_frames": total_frames,
            "processed_frames": processed_count,
            "fps": fps,
            "duration_seconds": total_frames / fps if fps > 0 else 0,
            "frame_skip": frame_skip
        }
    
    def _calculate_team_scores(self, goals: List[Dict]) -> Dict[str, int]:
        scores = {"team_a": 0, "team_b": 0, "unknown": 0}
        for goal in goals:
            team = goal.get("team", "unknown")
            scores[team] = scores.get(team, 0) + 1
        return scores
    
    def _cleanup(self):
        import shutil
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"⚠️  Cleanup error: {e}", flush=True)
