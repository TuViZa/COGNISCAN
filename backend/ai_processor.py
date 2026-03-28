import cv2
import mediapipe as mp
import librosa
import numpy as np
from transformers import pipeline
import torch
from typing import Dict, Tuple
import tempfile
import os

class AIProcessor:
    def __init__(self):
        # Initialize MediaPipe for face detection and mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize BERT for NLP analysis
        self.nlp_pipeline = pipeline(
            "feature-extraction",
            model="bert-base-uncased",
            tokenizer="bert-base-uncased"
        )
        
        # Audio processing parameters
        self.sample_rate = 22050
        self.n_mfcc = 13
        
    def extract_audio_features(self, audio_path: str) -> Dict:
        """
        Extract audio features using Librosa
        """
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc)
            
            # Extract pitch (fundamental frequency)
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = []
            for i in range(pitches.shape[1]):
                index = magnitudes[:, i].argmax()
                pitch = pitches[index, i]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            # Calculate pitch statistics
            if pitch_values:
                pitch_mean = np.mean(pitch_values)
                pitch_std = np.std(pitch_values)
                pitch_range = np.max(pitch_values) - np.min(pitch_values)
            else:
                pitch_mean = pitch_std = pitch_range = 0
            
            # Extract tempo and rhythm features
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            # Calculate speech rate (beats per minute)
            speech_rate = len(beats) / (len(y) / sr) * 60
            
            # Detect pauses (silence detection)
            rms = librosa.feature.rms(y=y)[0]
            silence_threshold = 0.01
            pause_frames = np.where(rms < silence_threshold)[0]
            pause_count = len(pause_frames)
            pause_duration = len(pause_frames) / sr if pause_count > 0 else 0
            
            return {
                "mfcc_features": mfccs.tolist(),
                "pitch_mean": float(pitch_mean),
                "pitch_std": float(pitch_std),
                "pitch_range": float(pitch_range),
                "tempo": float(tempo),
                "speech_rate": float(speech_rate),
                "pause_count": int(pause_count),
                "pause_duration": float(pause_duration),
                "rms_energy": float(np.mean(rms))
            }
            
        except Exception as e:
            print(f"Error extracting audio features: {e}")
            return {}
    
    def analyze_facial_expressions(self, video_path: str) -> Dict:
        """
        Analyze facial expressions and micro-expressions using MediaPipe
        """
        try:
            cap = cv2.VideoCapture(video_path)
            frame_count = 0
            expression_data = []
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process with MediaPipe
                results = self.face_mesh.process(rgb_frame)
                
                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0]
                    
                    # Extract key facial points for expression analysis
                    # Eye aspect ratio for blink detection
                    left_eye = self._calculate_eye_aspect_ratio(landmarks, [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246])
                    right_eye = self._calculate_eye_aspect_ratio(landmarks, [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382])
                    
                    # Mouth aspect ratio for speech detection
                    mouth_aspect = self._calculate_mouth_aspect_ratio(landmarks)
                    
                    # Face symmetry analysis
                    symmetry_score = self._calculate_face_symmetry(landmarks)
                    
                    expression_data.append({
                        "frame": frame_count,
                        "left_eye": left_eye,
                        "right_eye": right_eye,
                        "mouth_aspect": mouth_aspect,
                        "symmetry": symmetry_score
                    })
                
                frame_count += 1
            
            cap.release()
            
            # Calculate aggregate statistics
            if expression_data:
                avg_eye_aspect = np.mean([d["left_eye"] + d["right_eye"] for d in expression_data]) / 2
                avg_mouth_aspect = np.mean([d["mouth_aspect"] for d in expression_data])
                avg_symmetry = np.mean([d["symmetry"] for d in expression_data])
                
                # Detect anomalies
                eye_contact_stability = np.std([d["left_eye"] + d["right_eye"] for d in expression_data]) / 2
                mouth_movement_variance = np.std([d["mouth_aspect"] for d in expression_data])
                
                return {
                    "eye_contact_stability": float(eye_contact_stability),
                    "mouth_movement_variance": float(mouth_movement_variance),
                    "facial_symmetry": float(avg_symmetry),
                    "blink_rate": self._calculate_blink_rate(expression_data),
                    "expression_consistency": self._calculate_expression_consistency(expression_data)
                }
            else:
                return {}
                
        except Exception as e:
            print(f"Error analyzing facial expressions: {e}")
            return {}
    
    def analyze_speech_content(self, transcript: str) -> Dict:
        """
        Analyze speech content using BERT for semantic analysis
        """
        try:
            # Get BERT embeddings
            features = self.nlp_pipeline(transcript)
            
            # Calculate various linguistic features
            words = transcript.split()
            sentences = transcript.split('.')
            
            # Basic linguistic metrics
            word_count = len(words)
            sentence_count = len([s for s in sentences if s.strip()])
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
            
            # Vocabulary richness (type-token ratio)
            unique_words = set(words)
            ttr = len(unique_words) / word_count if word_count > 0 else 0
            
            # Semantic coherence (simplified - using BERT features variance)
            if len(features) > 1:
                feature_array = np.array(features)
                semantic_coherence = 1.0 / (1.0 + np.std(feature_array))
            else:
                semantic_coherence = 0.5
            
            return {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_sentence_length": float(avg_sentence_length),
                "vocabulary_richness": float(ttr),
                "semantic_coherence": float(semantic_coherence),
                "complexity_score": self._calculate_complexity_score(transcript)
            }
            
        except Exception as e:
            print(f"Error analyzing speech content: {e}")
            return {}
    
    def _calculate_eye_aspect_ratio(self, landmarks, eye_indices):
        """Calculate eye aspect ratio for blink detection"""
        try:
            points = []
            for idx in eye_indices:
                landmark = landmarks.landmark[idx]
                points.extend([landmark.x, landmark.y])
            
            points = np.array(points).reshape(-1, 2)
            
            # Calculate distances
            vertical1 = np.linalg.norm(points[1] - points[5])
            vertical2 = np.linalg.norm(points[2] - points[4])
            horizontal = np.linalg.norm(points[0] - points[3])
            
            ear = (vertical1 + vertical2) / (2.0 * horizontal)
            return ear
        except:
            return 0.0
    
    def _calculate_mouth_aspect_ratio(self, landmarks):
        """Calculate mouth aspect ratio for speech detection"""
        try:
            # Mouth landmarks
            mouth_indices = [61, 84, 17, 314, 405, 291, 375, 321, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]
            points = []
            for idx in mouth_indices[:6]:  # Simplified for demo
                landmark = landmarks.landmark[idx]
                points.extend([landmark.x, landmark.y])
            
            points = np.array(points).reshape(-1, 2)
            
            vertical = np.linalg.norm(points[1] - points[4])
            horizontal = np.linalg.norm(points[0] - points[3])
            
            mar = vertical / horizontal
            return mar
        except:
            return 0.0
    
    def _calculate_face_symmetry(self, landmarks):
        """Calculate facial symmetry score"""
        try:
            # Compare left and right face landmarks
            left_points = []
            right_points = []
            
            # Simplified symmetry check using a few key points
            pairs = [(33, 263), (133, 362), (155, 385), (285, 384)]  # Eye and cheek points
            
            for left_idx, right_idx in pairs:
                left_landmark = landmarks.landmark[left_idx]
                right_landmark = landmarks.landmark[right_idx]
                left_points.append([left_landmark.x, left_landmark.y])
                right_points.append([right_landmark.x, right_landmark.y])
            
            left_points = np.array(left_points)
            right_points = np.array(right_points)
            
            # Mirror right points and compare with left
            right_mirrored = right_points.copy()
            right_mirrored[:, 0] = 1.0 - right_mirrored[:, 0]
            
            symmetry_score = 1.0 / (1.0 + np.mean(np.linalg.norm(left_points - right_mirrored, axis=1)))
            return symmetry_score
        except:
            return 0.5
    
    def _calculate_blink_rate(self, expression_data):
        """Calculate blink rate from eye aspect ratio data"""
        if not expression_data:
            return 0.0
        
        blink_threshold = 0.25
        blinks = 0
        
        for i in range(1, len(expression_data)):
            prev_ear = (expression_data[i-1]["left_eye"] + expression_data[i-1]["right_eye"]) / 2
            curr_ear = (expression_data[i]["left_eye"] + expression_data[i]["right_eye"]) / 2
            
            if prev_ear > blink_threshold and curr_ear <= blink_threshold:
                blinks += 1
        
        # Blinks per minute (assuming 30 fps video)
        duration_minutes = len(expression_data) / (30 * 60)
        blink_rate = blinks / duration_minutes if duration_minutes > 0 else 0
        return blink_rate
    
    def _calculate_expression_consistency(self, expression_data):
        """Calculate how consistent facial expressions are"""
        if not expression_data:
            return 0.5
        
        # Calculate variance in facial features
        mouth_variance = np.var([d["mouth_aspect"] for d in expression_data])
        symmetry_variance = np.var([d["symmetry"] for d in expression_data])
        
        # Lower variance = more consistent
        consistency = 1.0 / (1.0 + mouth_variance + symmetry_variance)
        return consistency
    
    def _calculate_complexity_score(self, transcript):
        """Calculate linguistic complexity score"""
        try:
            words = transcript.split()
            
            # Count complex words (more than 6 characters)
            complex_words = [w for w in words if len(w) > 6]
            complexity_ratio = len(complex_words) / len(words) if words else 0
            
            # Count conjunctions and connectors (simplified)
            connectors = ['and', 'but', 'or', 'because', 'however', 'therefore', 'although', 'since']
            connector_count = sum(1 for w in words if w.lower() in connectors)
            connector_ratio = connector_count / len(words) if words else 0
            
            # Combined complexity score
            complexity_score = (complexity_ratio + connector_ratio) / 2
            return complexity_score
        except:
            return 0.0
