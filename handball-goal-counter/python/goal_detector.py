#!/usr/bin/env python3
"""Detector de Goles con Lógica Deportiva de Handball"""

import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
from collections import defaultdict


class GoalZone:
    """Representa una zona de portería"""
    
    def __init__(self, name: str, team: str, coordinates: List[List[int]]):
        self.name = name
        self.team = team
        self.polygon = np.array(coordinates, dtype=np.int32)
    
    def contains_point(self, point: Tuple[float, float]) -> bool:
        x, y = point
        result = cv2.pointPolygonTest(self.polygon, (float(x), float(y)), False)
        return result >= 0


class GoalDetector:
    """Detector de goles con validación de trayectoria"""
    
    def __init__(self, goal_zones: List[Dict], min_confidence: float = 0.7):
        self.zones = [
            GoalZone(z['name'], z['team'], z['coordinates'])
            for z in goal_zones
        ]
        self.min_confidence = min_confidence
        
        self.detected_goals = set()
        self.ball_positions = defaultdict(list)
        self.cooldown_frames = 30
        self.last_goal_frame = -self.cooldown_frames
        self.current_frame = 0
    
    def check_goal(
        self, 
        detections: List[Dict], 
        frame: np.ndarray,
        timestamp: float
    ) -> Optional[Dict]:
        self.current_frame += 1
        
        # Cooldown entre goles
        if (self.current_frame - self.last_goal_frame) < self.cooldown_frames:
            return None
        
        # Buscar la pelota
        ball_detections = [
            d for d in detections 
            if d.get('class_name') == 'sports_ball'
        ]
        
        if not ball_detections:
            return None
        
        ball = max(ball_detections, key=lambda x: x['confidence'])
        
        if ball['confidence'] < self.min_confidence:
            return None
        
        bbox = ball['bbox']
        ball_center = (
            (bbox[0] + bbox[2]) / 2,
            (bbox[1] + bbox[3]) / 2
        )
        
        track_id = ball.get('track_id', -1)
        
        # Guardar posición en historial
        self.ball_positions[track_id].append({
            'position': ball_center,
            'timestamp': timestamp,
            'frame': self.current_frame
        })
        
        if len(self.ball_positions[track_id]) > 10:
            self.ball_positions[track_id].pop(0)
        
        # Verificar cruce de portería
        goal_event = self._check_goal_crossing(
            ball_center, 
            track_id, 
            timestamp,
            ball['confidence']
        )
        
        if goal_event:
            self.last_goal_frame = self.current_frame
        
        return goal_event
    
    def _check_goal_crossing(
        self, 
        ball_center: Tuple[float, float],
        track_id: int,
        timestamp: float,
        confidence: float
    ) -> Optional[Dict]:
        for zone in self.zones:
            if zone.contains_point(ball_center):
                timestamp_rounded = round(timestamp, 1)
                goal_key = (track_id, timestamp_rounded)
                
                if goal_key in self.detected_goals:
                    return None
                
                if not self._validate_trajectory(track_id, zone):
                    continue
                
                self.detected_goals.add(goal_key)
                
                # El equipo que anota es el opuesto al dueño de la portería
                scoring_team = "team_b" if zone.team == "team_a" else "team_a"
                
                return {
                    'timestamp': timestamp,
                    'zone': zone.name,
                    'team': scoring_team,
                    'goal_owner': zone.team,
                    'confidence': confidence,
                    'ball_position': ball_center,
                    'track_id': track_id
                }
        
        return None
    
    def _validate_trajectory(self, track_id: int, zone: GoalZone) -> bool:
        """Valida que la pelota haya entrado desde afuera"""
        history = self.ball_positions.get(track_id, [])
        
        if len(history) < 3:
            return True
        
        recent_positions = history[-5:-1]
        
        outside_count = sum(
            1 for pos in recent_positions
            if not zone.contains_point(pos['position'])
        )
        
        return outside_count >= 2
