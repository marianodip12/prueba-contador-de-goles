#!/usr/bin/env python3
"""Motor de Tracking con YOLOv8 + DeepSORT"""

import numpy as np
import cv2
from typing import List, Dict, Tuple
from collections import defaultdict, deque

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None


class DeepSORTTracker:
    
    def __init__(self, max_age=30, min_hits=3, iou_threshold=0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.tracks = {}
        self.next_id = 0
        self.track_history = defaultdict(lambda: deque(maxlen=30))
    
    def update(self, detections: List[Dict]) -> List[Dict]:
        if not detections:
            return []
        
        matched_tracks = []
        
        for det in detections:
            bbox = det['bbox']
            class_id = det['class_id']
            
            best_iou = 0
            best_track_id = None
            
            for track_id, track in self.tracks.items():
                iou = self._calculate_iou(bbox, track['bbox'])
                if iou > best_iou and iou > self.iou_threshold:
                    best_iou = iou
                    best_track_id = track_id
            
            if best_track_id is not None:
                track_id = best_track_id
            else:
                track_id = self.next_id
                self.next_id += 1
            
            self.tracks[track_id] = {
                'bbox': bbox,
                'class_id': class_id,
                'age': 0,
                'hits': self.tracks.get(track_id, {}).get('hits', 0) + 1
            }
            
            center = self._get_center(bbox)
            self.track_history[track_id].append(center)
            
            matched_tracks.append({
                **det,
                'track_id': track_id,
                'trajectory': list(self.track_history[track_id])
            })
        
        self._age_tracks()
        return matched_tracks
    
    def _calculate_iou(self, box1, box2) -> float:
        x1, y1, x2, y2 = box1
        x1_p, y1_p, x2_p, y2_p = box2
        
        xi1 = max(x1, x1_p)
        yi1 = max(y1, y1_p)
        xi2 = min(x2, x2_p)
        yi2 = min(y2, y2_p)
        
        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        box1_area = (x2 - x1) * (y2 - y1)
        box2_area = (x2_p - x1_p) * (y2_p - y1_p)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0
    
    def _get_center(self, bbox) -> Tuple[float, float]:
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def _age_tracks(self):
        to_delete = []
        for track_id in list(self.tracks.keys()):
            self.tracks[track_id]['age'] += 1
            if self.tracks[track_id]['age'] > self.max_age:
                to_delete.append(track_id)
        for track_id in to_delete:
            del self.tracks[track_id]


class TrackingEngine:
    
    def __init__(self, model_path: str, confidence_threshold: float = 0.5):
        if YOLO is None:
            raise ImportError("ultralytics no está instalado")
        
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self.tracker = DeepSORTTracker()
        
        self.relevant_classes = {
            0: 'person',
            32: 'sports_ball'
        }
    
    def track(self, frame: np.ndarray) -> List[Dict]:
        results = self.model(frame, verbose=False)[0]
        
        detections = []
        
        for box in results.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            
            if class_id not in self.relevant_classes:
                continue
            
            if confidence < self.confidence_threshold:
                continue
            
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            
            detections.append({
                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                'confidence': confidence,
                'class_id': class_id,
                'class_name': self.relevant_classes[class_id]
            })
        
        return self.tracker.update(detections)
