#!/usr/bin/env python3
"""
Sistema Principal de Procesamiento de Video
Integra: yt-dlp, YOLOv8, DeepSORT, SportSense
"""

import os
import sys
import json
import tempfile
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

try:
    import cv2
    import numpy as np
    from youtube_extractor import YouTubeExtractor
    from tracking_engine import TrackingEngine
    from goal_detector import GoalDetector
except ImportError as e:
    print(json.dumps({
        "error": f"Import error: {str(e)}",
        "type": "ImportError",
        "success": False
    }))
    sys.exit(1)


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
    
    def __init__(self, config_path: str = "config/handball_config.json"):
        self.config = self._load_config(config_path)
        
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
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
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
        import time
        start_time = time.time()
        
        video_path = self.youtube_extractor.download(
            youtube_url, 
            output_path=self.temp_dir,
            max_duration=self.config.get("max_video_duration", 300)
        )
        
        if not video_path or not os.path.exists(video_path):
            raise RuntimeError("Error al descargar el video")
        
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
        return result
    
    def _process_frames(self, video_path: str) -> Tuple[List[Dict], Dict]:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise RuntimeError(f"No se pudo abrir el video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_skip = self.config.get("frame_skip", 2)
        
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
            
            detections = self.tracking_engine.track(frame)
            goal_event = self.goal_detector.check_goal(
                detections=detections,
                frame=frame,
                timestamp=frame_count / fps
            )
            
            if goal_event:
                goals.append(goal_event)
            
            processed_count += 1
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
        except Exception:
            pass


def main(youtube_url: str) -> str:
    try:
        processor = HandballVideoProcessor()
        result = processor.process_video(youtube_url)
        return json.dumps(asdict(result), indent=2)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "type": type(e).__name__,
            "success": False
        }, indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "URL requerida", "success": False}))
        sys.exit(1)
    
    print(main(sys.argv[1]))
