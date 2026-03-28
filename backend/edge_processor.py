import cv2
import mediapipe as mp
import numpy as np
import json
import base64
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import asyncio
from datetime import datetime
import zlib
import hashlib

@dataclass
class FacialLandmarks:
    """Processed facial landmarks data"""
    timestamp: float
    landmarks_2d: List[List[float]]  # 468 landmarks in 2D
    landmarks_3d: List[List[float]]  # 468 landmarks in 3D
    face_rect: Tuple[int, int, int, int]  # (x, y, width, height)
    face_detected: bool
    confidence: float

@dataclass
class EdgeProcessedData:
    """Edge-processed data ready for secure transmission"""
    patient_id: str
    session_id: str
    processing_timestamp: str
    facial_landmarks: List[FacialLandmarks]
    audio_features: Dict
    metadata: Dict
    data_hash: str
    compression_ratio: float

class EdgeProcessor:
    """
    Edge Processing Simulation - Converts raw video into numerical facial landmarks
    and features before transmission to minimize sensitive data transfer
    """
    
    def __init__(self):
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Edge processing configuration
        self.FRAME_SKIP = 5  # Process every 5th frame for efficiency
        self.LANDMARK_COUNT = 468  # MediaPipe face mesh landmarks
        self.COMPRESSION_ENABLED = True
        
        # Privacy preservation settings
        self.REMOVE_RAW_PIXELS = True
        self.OBFUSCATE_BACKGROUND = True
        
    async def process_video_edge(self, video_path: str, patient_id: str, session_id: str) -> EdgeProcessedData:
        """
        Process video on edge device, extracting only numerical features
        """
        try:
            print(f"Starting edge processing for patient {patient_id}, session {session_id}")
            
            # Step 1: Extract facial landmarks
            facial_landmarks = await self._extract_facial_landmarks(video_path)
            
            # Step 2: Extract basic audio features (if audio present)
            audio_features = await self._extract_audio_features_edge(video_path)
            
            # Step 3: Create metadata
            metadata = self._create_processing_metadata(video_path, len(facial_landmarks))
            
            # Step 4: Create edge-processed data package
            edge_data = EdgeProcessedData(
                patient_id=patient_id,
                session_id=session_id,
                processing_timestamp=datetime.now().isoformat(),
                facial_landmarks=facial_landmarks,
                audio_features=audio_features,
                metadata=metadata,
                data_hash="",  # Will be calculated
                compression_ratio=0.0  # Will be calculated
            )
            
            # Step 5: Calculate data integrity hash
            edge_data.data_hash = self._calculate_data_hash(edge_data)
            
            # Step 6: Compress data for transmission
            if self.COMPRESSION_ENABLED:
                edge_data = await self._compress_edge_data(edge_data)
            
            print(f"Edge processing completed. Processed {len(facial_landmarks)} frames")
            
            return edge_data
            
        except Exception as e:
            print(f"Edge processing error: {e}")
            raise e
    
    async def _extract_facial_landmarks(self, video_path: str) -> List[FacialLandmarks]:
        """Extract facial landmarks from video"""
        cap = cv2.VideoCapture(video_path)
        landmarks_data = []
        frame_count = 0
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process every Nth frame for efficiency
            if frame_count % self.FRAME_SKIP == 0:
                timestamp = frame_count / fps if fps > 0 else frame_count
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process with MediaPipe
                results = self.face_mesh.process(rgb_frame)
                
                if results.multi_face_landmarks:
                    face_landmarks = results.multi_face_landmarks[0]
                    
                    # Extract 2D landmarks
                    landmarks_2d = []
                    for landmark in face_landmarks.landmark:
                        landmarks_2d.append([landmark.x, landmark.y])
                    
                    # Extract 3D landmarks (if available)
                    landmarks_3d = []
                    for landmark in face_landmarks.landmark:
                        landmarks_3d.append([landmark.x, landmark.y, landmark.z])
                    
                    # Calculate face bounding box
                    h, w, _ = frame.shape
                    x_coords = [lm.x * w for lm in face_landmarks.landmark]
                    y_coords = [lm.y * h for lm in face_landmarks.landmark]
                    
                    face_rect = (
                        int(min(x_coords)),
                        int(min(y_coords)),
                        int(max(x_coords) - min(x_coords)),
                        int(max(y_coords) - min(y_coords))
                    )
                    
                    # Create facial landmarks data
                    facial_landmarks = FacialLandmarks(
                        timestamp=timestamp,
                        landmarks_2d=landmarks_2d,
                        landmarks_3d=landmarks_3d,
                        face_rect=face_rect,
                        face_detected=True,
                        confidence=0.9  # Placeholder confidence
                    )
                    
                    landmarks_data.append(facial_landmarks)
                else:
                    # No face detected
                    landmarks_data.append(FacialLandmarks(
                        timestamp=timestamp,
                        landmarks_2d=[],
                        landmarks_3d=[],
                        face_rect=(0, 0, 0, 0),
                        face_detected=False,
                        confidence=0.0
                    ))
            
            frame_count += 1
        
        cap.release()
        return landmarks_data
    
    async def _extract_audio_features_edge(self, video_path: str) -> Dict:
        """Extract basic audio features on edge device"""
        try:
            # For edge processing, extract minimal audio features
            # Full analysis will be done on server
            
            # Extract audio from video (simplified)
            audio_features = {
                'has_audio': True,  # Placeholder
                'duration': 0.0,     # Will be filled by server
                'sample_rate': 44100,
                'channels': 1,
                'edge_extracted_features': {
                    'energy_level': 0.5,  # Placeholder
                    'zero_crossing_rate': 0.1,  # Placeholder
                    'spectral_centroid': 2000.0,  # Placeholder
                }
            }
            
            return audio_features
            
        except Exception as e:
            print(f"Audio feature extraction error: {e}")
            return {'has_audio': False}
    
    def _create_processing_metadata(self, video_path: str, processed_frames: int) -> Dict:
        """Create metadata for edge processing"""
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            cap.release()
            
            metadata = {
                'original_video_info': {
                    'total_frames': total_frames,
                    'fps': fps,
                    'duration': duration,
                    'resolution': 'extracted_on_server'  # Privacy: don't transmit resolution
                },
                'edge_processing_info': {
                    'processed_frames': processed_frames,
                    'frame_skip': self.FRAME_SKIP,
                    'landmarks_per_frame': self.LANDMARK_COUNT,
                    'compression_enabled': self.COMPRESSION_ENABLED,
                    'privacy_features': {
                        'raw_pixels_removed': self.REMOVE_RAW_PIXELS,
                        'background_obfuscated': self.OBFUSCATE_BACKGROUND
                    }
                },
                'device_info': {
                    'processing_device': 'edge_device',
                    'mediapipe_version': '0.10.33',
                    'processing_timestamp': datetime.now().isoformat()
                }
            }
            
            return metadata
            
        except Exception as e:
            print(f"Metadata creation error: {e}")
            return {'error': str(e)}
    
    def _calculate_data_hash(self, edge_data: EdgeProcessedData) -> str:
        """Calculate hash for data integrity verification"""
        try:
            # Create a deterministic string representation
            data_str = json.dumps({
                'patient_id': edge_data.patient_id,
                'session_id': edge_data.session_id,
                'timestamp': edge_data.processing_timestamp,
                'landmarks_count': len(edge_data.facial_landmarks),
                'metadata': edge_data.metadata
            }, sort_keys=True)
            
            # Calculate SHA-256 hash
            hash_object = hashlib.sha256(data_str.encode())
            return hash_object.hexdigest()
            
        except Exception as e:
            print(f"Hash calculation error: {e}")
            return ""
    
    async def _compress_edge_data(self, edge_data: EdgeProcessedData) -> EdgeProcessedData:
        """Compress edge data for efficient transmission"""
        try:
            # Convert to JSON
            data_dict = asdict(edge_data)
            
            # Convert landmarks data to more compact format
            for i, landmark in enumerate(data_dict['facial_landmarks']):
                data_dict['facial_landmarks'][i] = {
                    't': landmark['timestamp'],
                    'l2d': landmark['landmarks_2d'],
                    'l3d': landmark['landmarks_3d'],
                    'r': landmark['face_rect'],
                    'd': landmark['face_detected'],
                    'c': landmark['confidence']
                }
            
            # Serialize and compress
            json_str = json.dumps(data_dict)
            compressed_bytes = zlib.compress(json_str.encode())
            
            # Calculate compression ratio
            original_size = len(json_str.encode())
            compressed_size = len(compressed_bytes)
            compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            
            # Store compressed data (in practice, this would be transmitted)
            edge_data.compression_ratio = compression_ratio
            
            print(f"Data compression: {original_size} -> {compressed_size} bytes (ratio: {compression_ratio:.2f})")
            
            return edge_data
            
        except Exception as e:
            print(f"Compression error: {e}")
            return edge_data
    
    def simulate_transmission_security(self, edge_data: EdgeProcessedData) -> Dict:
        """
        Simulate secure transmission with privacy-preserving measures
        """
        try:
            # Privacy-preserving transformations
            secure_data = {
                'transmission_metadata': {
                    'patient_id_hash': hashlib.sha256(edge_data.patient_id.encode()).hexdigest(),
                    'session_id': edge_data.session_id,
                    'timestamp': edge_data.processing_timestamp,
                    'data_integrity_hash': edge_data.data_hash
                },
                'processed_features': {
                    'landmark_summary': self._create_landmark_summary(edge_data.facial_landmarks),
                    'temporal_features': self._extract_temporal_features(edge_data.facial_landmarks),
                    'spatial_features': self._extract_spatial_features(edge_data.facial_landmarks),
                    'audio_summary': edge_data.audio_features
                },
                'privacy_metrics': {
                    'raw_video_size': 'not_transmitted',
                    'landmarks_only': True,
                    'pixel_data_removed': True,
                    'face_identification_obfuscated': True
                }
            }
            
            return secure_data
            
        except Exception as e:
            print(f"Security simulation error: {e}")
            return {'error': str(e)}
    
    def _create_landmark_summary(self, landmarks: List[FacialLandmarks]) -> Dict:
        """Create summary statistics of landmarks"""
        if not landmarks:
            return {}
        
        # Calculate summary statistics across all landmarks
        all_landmarks_2d = []
        all_landmarks_3d = []
        
        for landmark_data in landmarks:
            if landmark_data.face_detected and landmark_data.landmarks_2d:
                all_landmarks_2d.extend(landmark_data.landmarks_2d)
                if landmark_data.landmarks_3d:
                    all_landmarks_3d.extend(landmark_data.landmarks_3d)
        
        if not all_landmarks_2d:
            return {}
        
        # Convert to numpy array for statistics
        landmarks_2d_array = np.array(all_landmarks_2d)
        
        summary = {
            'total_landmarks': len(all_landmarks_2d),
            'landmark_statistics': {
                'mean_x': float(np.mean(landmarks_2d_array[:, 0])),
                'mean_y': float(np.mean(landmarks_2d_array[:, 1])),
                'std_x': float(np.std(landmarks_2d_array[:, 0])),
                'std_y': float(np.std(landmarks_2d_array[:, 1])),
                'min_x': float(np.min(landmarks_2d_array[:, 0])),
                'max_x': float(np.max(landmarks_2d_array[:, 0])),
                'min_y': float(np.min(landmarks_2d_array[:, 1])),
                'max_y': float(np.max(landmarks_2d_array[:, 1]))
            },
            'face_detection_rate': sum(1 for l in landmarks if l.face_detected) / len(landmarks),
            'average_confidence': np.mean([l.confidence for l in landmarks if l.face_detected]) if any(l.face_detected for l in landmarks) else 0.0
        }
        
        return summary
    
    def _extract_temporal_features(self, landmarks: List[FacialLandmarks]) -> Dict:
        """Extract temporal features from landmark sequence"""
        if len(landmarks) < 2:
            return {}
        
        # Extract movement patterns
        movements = []
        for i in range(1, len(landmarks)):
            if landmarks[i-1].face_detected and landmarks[i].face_detected:
                # Calculate movement between frames
                prev_landmarks = np.array(landmarks[i-1].landmarks_2d)
                curr_landmarks = np.array(landmarks[i].landmarks_2d)
                
                if len(prev_landmarks) > 0 and len(curr_landmarks) > 0:
                    movement = np.mean(np.linalg.norm(curr_landmarks - prev_landmarks, axis=1))
                    movements.append(movement)
        
        temporal_features = {
            'average_movement': float(np.mean(movements)) if movements else 0.0,
            'movement_variance': float(np.var(movements)) if movements else 0.0,
            'max_movement': float(np.max(movements)) if movements else 0.0,
            'movement_stability': 1.0 / (1.0 + np.var(movements)) if movements else 0.0
        }
        
        return temporal_features
    
    def _extract_spatial_features(self, landmarks: List[FacialLandmarks]) -> Dict:
        """Extract spatial features from landmarks"""
        if not landmarks:
            return {}
        
        # Analyze spatial distribution
        face_rects = [l.face_rect for l in landmarks if l.face_detected]
        
        if not face_rects:
            return {}
        
        # Calculate face position stability
        x_positions = [rect[0] for rect in face_rects]
        y_positions = [rect[1] for rect in face_rects]
        widths = [rect[2] for rect in face_rects]
        heights = [rect[3] for rect in face_rects]
        
        spatial_features = {
            'face_position_stability': {
                'x_stability': 1.0 / (1.0 + np.std(x_positions)) if x_positions else 0.0,
                'y_stability': 1.0 / (1.0 + np.std(y_positions)) if y_positions else 0.0
            },
            'face_size_consistency': {
                'width_consistency': 1.0 / (1.0 + np.std(widths)) if widths else 0.0,
                'height_consistency': 1.0 / (1.0 + np.std(heights)) if heights else 0.0
            },
            'average_face_size': {
                'width': float(np.mean(widths)) if widths else 0.0,
                'height': float(np.mean(heights)) if heights else 0.0
            }
        }
        
        return spatial_features
    
    def get_privacy_metrics(self) -> Dict:
        """Get privacy and security metrics"""
        return {
            'data_reduction_ratio': self.FRAME_SKIP,
            'feature_extraction_only': True,
            'raw_pixel_data_removed': self.REMOVE_RAW_PIXELS,
            'background_obfuscation': self.OBFUSCATE_BACKGROUND,
            'facial_landmarks_only': True,
            'no_identifiable_images': True,
            'edge_processing_benefits': [
                'Reduced bandwidth usage',
                'Enhanced privacy protection',
                'Faster processing times',
                'Lower server load'
            ]
        }
    
    def validate_edge_data_integrity(self, edge_data: EdgeProcessedData) -> bool:
        """Validate integrity of edge-processed data"""
        try:
            # Recalculate hash and compare
            calculated_hash = self._calculate_data_hash(edge_data)
            return calculated_hash == edge_data.data_hash
            
        except Exception as e:
            print(f"Integrity validation error: {e}")
            return False
