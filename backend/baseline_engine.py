from typing import Dict, List, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from pymongo import MongoClient
import json

@dataclass
class BaselineData:
    """Stores patient baseline cognitive metrics"""
    patient_id: str
    baseline_scores: List[float]
    baseline_features: Dict[str, float]
    established_date: datetime
    is_stable: bool = False
    
@dataclass
class AnomalyResult:
    """Anomaly detection result"""
    is_anomaly: bool
    anomaly_score: float
    deviation_percentage: float
    affected_metrics: List[str]
    confidence: float

class SmartBaselineEngine:
    """
    Smart Baseline Engine that establishes personalized cognitive baselines
    and detects anomalies based on individual patterns rather than universal averages
    """
    
    def __init__(self, mongodb_uri: str = "mongodb://localhost:27017"):
        self.client = MongoClient(mongodb_uri)
        self.db = self.client.cogniscan
        self.baselines_collection = self.db.patient_baselines
        self.assessments_collection = self.db.assessments
        
        # Anomaly detection thresholds
        self.ANOMALY_THRESHOLD = 2.0  # Standard deviations
        self.MIN_BASELINE_SAMPLES = 3
        self.BASELINE_STABILITY_THRESHOLD = 0.15  # 15% variance allowed
        
    def establish_baseline(self, patient_id: str) -> bool:
        """
        Establish baseline from first 3 assessments for a patient
        """
        try:
            # Get first 3 assessments for this patient
            assessments = list(
                self.assessments_collection.find(
                    {"patient_id": patient_id}
                ).sort("timestamp", 1).limit(3)
            )
            
            if len(assessments) < self.MIN_BASELINE_SAMPLES:
                return False
            
            # Extract cognitive scores and features
            scores = []
            features = {
                "facial_symmetry": [],
                "pitch_variance": [],
                "speech_rate": [],
                "coherence": [],
                "vocabulary_richness": []
            }
            
            for assessment in assessments:
                scores.append(assessment["cognitive_score"])
                
                # Extract detailed features
                analysis = assessment.get("analysis", {})
                
                # Facial features
                facial = analysis.get("facial_analysis", {})
                if "facial_symmetry" in facial:
                    features["facial_symmetry"].append(self._normalize_feature(facial["facial_symmetry"]))
                
                # Speech features
                speech = analysis.get("speech_analysis", {})
                if "pitch_variance" in speech:
                    features["pitch_variance"].append(self._normalize_feature(speech["pitch_variance"]))
                if "speech_rate" in speech:
                    features["speech_rate"].append(self._normalize_feature(speech["speech_rate"]))
                
                # Language features
                language = analysis.get("language_analysis", {})
                if "coherence" in language:
                    features["coherence"].append(self._normalize_feature(language["coherence"]))
                if "vocabulary_richness" in language:
                    features["vocabulary_richness"].append(self._normalize_feature(language["vocabulary_richness"]))
            
            # Calculate baseline statistics
            baseline_data = BaselineData(
                patient_id=patient_id,
                baseline_scores=scores,
                baseline_features={
                    key: {
                        "mean": np.mean(values),
                        "std": np.std(values),
                        "count": len(values)
                    } if values else {"mean": 0, "std": 0, "count": 0}
                    for key, values in features.items()
                },
                established_date=datetime.now(),
                is_stable=self._check_baseline_stability(scores)
            )
            
            # Store baseline
            self.baselines_collection.replace_one(
                {"patient_id": patient_id},
                baseline_data.__dict__,
                upsert=True
            )
            
            return True
            
        except Exception as e:
            print(f"Error establishing baseline: {e}")
            return False
    
    def detect_anomalies(self, patient_id: str, current_assessment: Dict) -> AnomalyResult:
        """
        Detect anomalies by comparing current assessment against patient's baseline
        """
        try:
            # Get patient baseline
            baseline_doc = self.baselines_collection.find_one({"patient_id": patient_id})
            
            if not baseline_doc:
                # No baseline established yet
                return AnomalyResult(
                    is_anomaly=False,
                    anomaly_score=0.0,
                    deviation_percentage=0.0,
                    affected_metrics=[],
                    confidence=0.0
                )
            
            current_score = current_assessment["cognitive_score"]
            baseline_scores = baseline_doc["baseline_scores"]
            baseline_features = baseline_doc["baseline_features"]
            
            # Calculate anomaly score based on multiple factors
            anomaly_factors = []
            affected_metrics = []
            
            # 1. Cognitive score deviation
            baseline_mean = np.mean(baseline_scores)
            baseline_std = np.std(baseline_scores)
            
            if baseline_std > 0:
                score_z_score = abs(current_score - baseline_mean) / baseline_std
                anomaly_factors.append(score_z_score)
                
                if score_z_score > self.ANOMALY_THRESHOLD:
                    affected_metrics.append("cognitive_score")
            
            # 2. Feature-based anomalies
            current_analysis = current_assessment.get("analysis", {})
            
            # Facial analysis
            facial = current_analysis.get("facial_analysis", {})
            if "facial_symmetry" in facial:
                current_symmetry = self._normalize_feature(facial["facial_symmetry"])
                symmetry_stats = baseline_features.get("facial_symmetry", {})
                
                if symmetry_stats.get("std", 0) > 0:
                    symmetry_z = abs(current_symmetry - symmetry_stats["mean"]) / symmetry_stats["std"]
                    anomaly_factors.append(symmetry_z)
                    
                    if symmetry_z > self.ANOMALY_THRESHOLD:
                        affected_metrics.append("facial_symmetry")
            
            # Speech analysis
            speech = current_analysis.get("speech_analysis", {})
            if "pitch_variance" in speech:
                current_pitch = self._normalize_feature(speech["pitch_variance"])
                pitch_stats = baseline_features.get("pitch_variance", {})
                
                if pitch_stats.get("std", 0) > 0:
                    pitch_z = abs(current_pitch - pitch_stats["mean"]) / pitch_stats["std"]
                    anomaly_factors.append(pitch_z)
                    
                    if pitch_z > self.ANOMALY_THRESHOLD:
                        affected_metrics.append("pitch_variance")
            
            # Language analysis
            language = current_analysis.get("language_analysis", {})
            if "coherence" in language:
                current_coherence = self._normalize_feature(language["coherence"])
                coherence_stats = baseline_features.get("coherence", {})
                
                if coherence_stats.get("std", 0) > 0:
                    coherence_z = abs(current_coherence - coherence_stats["mean"]) / coherence_stats["std"]
                    anomaly_factors.append(coherence_z)
                    
                    if coherence_z > self.ANOMALY_THRESHOLD:
                        affected_metrics.append("coherence")
            
            # Calculate overall anomaly score
            if anomaly_factors:
                anomaly_score = np.mean(anomaly_factors)
                confidence = min(len(anomaly_factors) / 3.0, 1.0)  # More factors = higher confidence
            else:
                anomaly_score = 0.0
                confidence = 0.0
            
            # Calculate deviation percentage
            if baseline_mean > 0:
                deviation_percentage = abs(current_score - baseline_mean) / baseline_mean * 100
            else:
                deviation_percentage = 0.0
            
            is_anomaly = anomaly_score > self.ANOMALY_THRESHOLD and confidence > 0.5
            
            return AnomalyResult(
                is_anomaly=is_anomaly,
                anomaly_score=anomaly_score,
                deviation_percentage=deviation_percentage,
                affected_metrics=affected_metrics,
                confidence=confidence
            )
            
        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            return AnomalyResult(
                is_anomaly=False,
                anomaly_score=0.0,
                deviation_percentage=0.0,
                affected_metrics=[],
                confidence=0.0
            )
    
    def get_baseline_status(self, patient_id: str) -> Dict:
        """
        Get baseline establishment status for a patient
        """
        try:
            # Count assessments
            assessment_count = self.assessments_collection.count_documents({"patient_id": patient_id})
            
            # Check if baseline exists
            baseline = self.baselines_collection.find_one({"patient_id": patient_id})
            
            status = {
                "patient_id": patient_id,
                "assessments_completed": assessment_count,
                "baseline_established": baseline is not None,
                "baseline_stable": baseline.get("is_stable", False) if baseline else False,
                "needed_for_baseline": max(0, self.MIN_BASELINE_SAMPLES - assessment_count)
            }
            
            if baseline:
                status.update({
                    "baseline_date": baseline["established_date"],
                    "baseline_mean_score": np.mean(baseline["baseline_scores"]),
                    "baseline_score_range": {
                        "min": min(baseline["baseline_scores"]),
                        "max": max(baseline["baseline_scores"])
                    }
                })
            
            return status
            
        except Exception as e:
            print(f"Error getting baseline status: {e}")
            return {"error": str(e)}
    
    def _normalize_feature(self, feature_value: str) -> float:
        """
        Normalize categorical feature values to numerical scores
        """
        normalization_map = {
            # Facial features
            "normal": 0.8,
            "stable": 0.8,
            "balanced": 0.8,
            "abnormal": 0.3,
            "unstable": 0.3,
            "imbalanced": 0.3,
            
            # Speech features
            "moderate": 0.7,
            "acceptable": 0.7,
            "fast": 0.5,
            "slow": 0.5,
            "irregular": 0.3,
            
            # Language features
            "good": 0.8,
            "adequate": 0.6,
            "poor": 0.3,
            "normal": 0.7
        }
        
        return normalization_map.get(feature_value.lower(), 0.5)
    
    def _check_baseline_stability(self, scores: List[float]) -> bool:
        """
        Check if baseline scores are stable enough to be used
        """
        if len(scores) < 3:
            return False
        
        mean_score = np.mean(scores)
        coefficient_of_variation = np.std(scores) / mean_score
        
        return coefficient_of_variation <= self.BASELINE_STABILITY_THRESHOLD
    
    def update_baseline(self, patient_id: str, include_new_assessment: bool = True) -> bool:
        """
        Update baseline with new data (optional rolling baseline)
        """
        try:
            if include_new_assessment:
                # Re-establish baseline with all available data
                return self.establish_baseline(patient_id)
            else:
                # Keep existing baseline
                return True
                
        except Exception as e:
            print(f"Error updating baseline: {e}")
            return False
