from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import numpy as np
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TimeSeriesData:
    """Time-series data structure for cognitive health metrics"""
    patient_id: str
    timestamp: datetime
    cognitive_score: float
    digital_biomarkers: Dict[str, Any]
    anomaly_detection: Dict[str, Any]
    multilingual_analysis: Optional[Dict[str, Any]] = None
    session_id: str = ""
    assessment_type: str = "daily_checkin"

class MongoDBManager:
    """
    MongoDB manager for time-series cognitive health data
    Optimized for rapid scaling and efficient querying
    """
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017", 
                 database_name: str = "cogniscan"):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        
        # Collections
        self.assessments_collection = None
        self.patients_collection = None
        self.baselines_collection = None
        self.time_series_collection = None
        
        # Connect to MongoDB
        self.connect()
        
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.database_name]
            
            # Initialize collections
            self.assessments_collection = self.db.assessments
            self.patients_collection = self.db.patients
            self.baselines_collection = self.db.baselines
            self.time_series_collection = self.db.time_series
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Create indexes for performance
            self._create_indexes()
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error setting up MongoDB: {e}")
            raise e
    
    def _create_indexes(self):
        """Create indexes for optimal query performance"""
        try:
            # Assessments collection indexes
            self.assessments_collection.create_index([("patient_id", 1), ("timestamp", -1)])
            self.assessments_collection.create_index([("timestamp", -1)])
            self.assessments_collection.create_index([("patient_id", 1), ("cognitive_score", -1)])
            
            # Time-series collection indexes
            self.time_series_collection.create_index([("patient_id", 1), ("timestamp", -1)])
            self.time_series_collection.create_index([("timestamp", -1)])
            self.time_series_collection.create_index([("patient_id", 1), ("session_id", 1)])
            
            # Patients collection indexes
            self.patients_collection.create_index([("patient_id", 1)], unique=True)
            self.patients_collection.create_index([("risk_level", 1)])
            self.patients_collection.create_index([("last_assessment", -1)])
            
            # Baselines collection indexes
            self.baselines_collection.create_index([("patient_id", 1)], unique=True)
            self.baselines_collection.create_index([("established_date", -1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            raise e
    
    def store_assessment(self, assessment_data: TimeSeriesData) -> str:
        """
        Store assessment data in time-series format
        """
        try:
            # Convert to dictionary
            data_dict = asdict(assessment_data)
            
            # Ensure timestamp is datetime object
            if isinstance(data_dict['timestamp'], str):
                data_dict['timestamp'] = datetime.fromisoformat(data_dict['timestamp'])
            
            # Store in assessments collection
            result = self.assessments_collection.insert_one(data_dict)
            
            # Store in time-series collection for specialized queries
            time_series_entry = {
                "patient_id": assessment_data.patient_id,
                "timestamp": assessment_data.timestamp,
                "value": assessment_data.cognitive_score,
                "metadata": {
                    "session_id": assessment_data.session_id,
                    "assessment_type": assessment_data.assessment_type,
                    "digital_biomarkers": assessment_data.digital_biomarkers,
                    "anomaly_detection": assessment_data.anomaly_detection,
                    "multilingual_analysis": assessment_data.multilingual_analysis
                }
            }
            
            self.time_series_collection.insert_one(time_series_entry)
            
            logger.info(f"Assessment stored for patient {assessment_data.patient_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing assessment: {e}")
            raise e
    
    def get_patient_history(self, patient_id: str, days: int = 30) -> List[Dict]:
        """
        Get patient assessment history for specified number of days
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            cursor = self.assessments_collection.find({
                "patient_id": patient_id,
                "timestamp": {"$gte": start_date}
            }).sort("timestamp", -1)
            
            history = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for doc in history:
                doc["_id"] = str(doc["_id"])
                if "timestamp" in doc and isinstance(doc["timestamp"], datetime):
                    doc["timestamp"] = doc["timestamp"].isoformat()
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting patient history: {e}")
            return []
    
    def get_time_series_data(self, patient_id: str, start_date: datetime, 
                           end_date: datetime) -> List[Dict]:
        """
        Get time-series data for a specific date range
        """
        try:
            cursor = self.time_series_collection.find({
                "patient_id": patient_id,
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }).sort("timestamp", 1)
            
            data = list(cursor)
            
            # Convert ObjectId to string
            for doc in data:
                doc["_id"] = str(doc["_id"])
                if "timestamp" in doc and isinstance(doc["timestamp"], datetime):
                    doc["timestamp"] = doc["timestamp"].isoformat()
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting time-series data: {e}")
            return []
    
    def get_aggregated_metrics(self, patient_id: str, days: int = 30) -> Dict:
        """
        Get aggregated metrics for a patient over specified period
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Aggregation pipeline
            pipeline = [
                {
                    "$match": {
                        "patient_id": patient_id,
                        "timestamp": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$patient_id",
                        "avg_score": {"$avg": "$cognitive_score"},
                        "min_score": {"$min": "$cognitive_score"},
                        "max_score": {"$max": "$cognitive_score"},
                        "std_score": {"$stdDevPop": "$cognitive_score"},
                        "assessment_count": {"$sum": 1},
                        "latest_assessment": {"$max": "$timestamp"},
                        "anomaly_count": {
                            "$sum": {
                                "$cond": [{"$eq": ["$anomaly_detection.isAnomaly", True]}, 1, 0]
                            }
                        }
                    }
                }
            ]
            
            result = list(self.assessments_collection.aggregate(pipeline))
            
            if result:
                metrics = result[0]
                metrics["_id"] = str(metrics["_id"])
                if "latest_assessment" in metrics and isinstance(metrics["latest_assessment"], datetime):
                    metrics["latest_assessment"] = metrics["latest_assessment"].isoformat()
                return metrics
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting aggregated metrics: {e}")
            return {}
    
    def get_trending_patients(self, risk_level: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Get patients with recent assessments, filtered by risk level
        """
        try:
            match_condition = {
                "last_assessment": {"$gte": datetime.now() - timedelta(days=7)}
            }
            
            if risk_level:
                match_condition["risk_level"] = risk_level
            
            cursor = self.patients_collection.find(match_condition).sort("last_assessment", -1).limit(limit)
            
            patients = list(cursor)
            
            # Convert ObjectId to string
            for patient in patients:
                patient["_id"] = str(patient["_id"])
                if "last_assessment" in patient and isinstance(patient["last_assessment"], datetime):
                    patient["last_assessment"] = patient["last_assessment"].isoformat()
            
            return patients
            
        except Exception as e:
            logger.error(f"Error getting trending patients: {e}")
            return []
    
    def store_patient_baseline(self, patient_id: str, baseline_data: Dict) -> bool:
        """
        Store patient baseline data
        """
        try:
            baseline_entry = {
                "patient_id": patient_id,
                "baseline_data": baseline_data,
                "established_date": datetime.now(),
                "last_updated": datetime.now()
            }
            
            result = self.baselines_collection.replace_one(
                {"patient_id": patient_id},
                baseline_entry,
                upsert=True
            )
            
            logger.info(f"Baseline stored for patient {patient_id}")
            return result.acknowledged
            
        except Exception as e:
            logger.error(f"Error storing baseline: {e}")
            return False
    
    def get_patient_baseline(self, patient_id: str) -> Optional[Dict]:
        """
        Get patient baseline data
        """
        try:
            baseline = self.baselines_collection.find_one({"patient_id": patient_id})
            
            if baseline:
                baseline["_id"] = str(baseline["_id"])
                if "established_date" in baseline and isinstance(baseline["established_date"], datetime):
                    baseline["established_date"] = baseline["established_date"].isoformat()
                if "last_updated" in baseline and isinstance(baseline["last_updated"], datetime):
                    baseline["last_updated"] = baseline["last_updated"].isoformat()
                return baseline
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting patient baseline: {e}")
            return None
    
    def update_patient_info(self, patient_id: str, patient_data: Dict) -> bool:
        """
        Update patient information
        """
        try:
            patient_data["last_updated"] = datetime.now()
            
            result = self.patients_collection.replace_one(
                {"patient_id": patient_id},
                patient_data,
                upsert=True
            )
            
            logger.info(f"Patient info updated for {patient_id}")
            return result.acknowledged
            
        except Exception as e:
            logger.error(f"Error updating patient info: {e}")
            return False
    
    def get_anomaly_summary(self, days: int = 30) -> Dict:
        """
        Get summary of anomalies detected in specified period
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            pipeline = [
                {
                    "$match": {
                        "timestamp": {"$gte": start_date},
                        "anomaly_detection.isAnomaly": True
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_anomalies": {"$sum": 1},
                        "unique_patients": {"$addToSet": "$patient_id"},
                        "avg_anomaly_score": {"$avg": "$anomaly_detection.anomalyScore"},
                        "daily_anomalies": {
                            "$push": {
                                "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                                "patient_id": "$patient_id",
                                "score": "$cognitive_score"
                            }
                        }
                    }
                }
            ]
            
            result = list(self.assessments_collection.aggregate(pipeline))
            
            if result:
                summary = result[0]
                summary["unique_patient_count"] = len(summary["unique_patients"])
                del summary["unique_patients"]  # Remove array, keep count
                return summary
            else:
                return {
                    "total_anomalies": 0,
                    "unique_patient_count": 0,
                    "avg_anomaly_score": 0,
                    "daily_anomalies": []
                }
                
        except Exception as e:
            logger.error(f"Error getting anomaly summary: {e}")
            return {}
    
    def get_multilingual_stats(self, days: int = 30) -> Dict:
        """
        Get statistics on multilingual assessments
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            pipeline = [
                {
                    "$match": {
                        "timestamp": {"$gte": start_date},
                        "multilingual_analysis": {"$exists": True}
                    }
                },
                {
                    "$group": {
                        "_id": "$multilingual_analysis.language",
                        "count": {"$sum": 1},
                        "avg_coherence": {"$avg": "$multilingual_analysis.coherence"},
                        "sentiment_distribution": {
                            "$push": "$multilingual_analysis.sentiment"
                        }
                    }
                }
            ]
            
            result = list(self.assessments_collection.aggregate(pipeline))
            
            stats = {}
            for lang_stat in result:
                language = lang_stat["_id"]
                stats[language] = {
                    "assessment_count": lang_stat["count"],
                    "avg_coherence": lang_stat["avg_coherence"],
                    "sentiment_distribution": {
                        "positive": lang_stat["sentiment_distribution"].count("positive"),
                        "negative": lang_stat["sentiment_distribution"].count("negative"),
                        "neutral": lang_stat["sentiment_distribution"].count("neutral")
                    }
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting multilingual stats: {e}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 365) -> int:
        """
        Clean up data older than specified number of days
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Delete old assessments
            result = self.assessments_collection.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            # Delete old time-series data
            ts_result = self.time_series_collection.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            deleted_count = result.deleted_count + ts_result.deleted_count
            logger.info(f"Cleaned up {deleted_count} old records")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0
    
    def get_database_stats(self) -> Dict:
        """
        Get database statistics
        """
        try:
            stats = {
                "assessments_count": self.assessments_collection.count_documents({}),
                "patients_count": self.patients_collection.count_documents({}),
                "baselines_count": self.baselines_collection.count_documents({}),
                "time_series_count": self.time_series_collection.count_documents({}),
                "database_size": self.db.command("collstats", "assessments").get("size", 0),
                "indexes": []
            }
            
            # Get index information
            for collection_name in ["assessments", "patients", "baselines", "time_series"]:
                collection = self.db[collection_name]
                index_info = collection.index_information()
                stats["indexes"].append({
                    "collection": collection_name,
                    "index_count": len(index_info)
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Singleton instance for application
db_manager = None

def get_database_manager(connection_string: str = "mongodb://localhost:27017") -> MongoDBManager:
    """
    Get or create database manager instance
    """
    global db_manager
    
    if db_manager is None:
        db_manager = MongoDBManager(connection_string)
    
    return db_manager

# Utility functions for data migration and setup
def setup_sample_data():
    """
    Setup sample data for testing and demonstration
    """
    try:
        db = get_database_manager()
        
        # Sample patients
        patients = [
            {
                "patient_id": "PAT001",
                "name": "Rajesh Kumar",
                "age": 68,
                "gender": "Male",
                "risk_level": "high",
                "baseline_established": True,
                "last_assessment": datetime.now(),
                "created_at": datetime.now()
            },
            {
                "patient_id": "PAT002",
                "name": "Meena Patel",
                "age": 72,
                "gender": "Female",
                "risk_level": "medium",
                "baseline_established": True,
                "last_assessment": datetime.now() - timedelta(days=1),
                "created_at": datetime.now()
            }
        ]
        
        # Insert patients
        for patient in patients:
            db.patients_collection.replace_one(
                {"patient_id": patient["patient_id"]},
                patient,
                upsert=True
            )
        
        # Sample assessments
        for patient in patients:
            for i in range(30):
                assessment_date = datetime.now() - timedelta(days=i)
                base_score = 75 if patient["risk_level"] == "medium" else 65
                score = base_score + np.random.normal(0, 5)
                
                assessment = TimeSeriesData(
                    patient_id=patient["patient_id"],
                    timestamp=assessment_date,
                    cognitive_score=max(50, min(95, score)),
                    digital_biomarkers={
                        "vocal_tremor": 2.5 + np.random.normal(0, 0.5),
                        "emotional_blunting": 0.4 + np.random.normal(0, 0.2),
                        "speech_pause": 1.5 + np.random.normal(0, 0.3)
                    },
                    anomaly_detection={
                        "isAnomaly": score < 70 and np.random.random() > 0.7,
                        "anomalyScore": np.random.uniform(1.5, 3.0) if score < 70 else 0.5,
                        "affectedMetrics": ["cognitive_score"] if score < 70 else []
                    },
                    multilingual_analysis={
                        "language": "Hindi" if np.random.random() > 0.5 else "English",
                        "coherence": 0.6 + np.random.normal(0, 0.2),
                        "sentiment": np.random.choice(["positive", "negative", "neutral"])
                    } if np.random.random() > 0.3 else None,
                    session_id=f"SESSION_{patient['patient_id']}_{i}",
                    assessment_type="daily_checkin"
                )
                
                db.store_assessment(assessment)
        
        logger.info("Sample data setup completed")
        
    except Exception as e:
        logger.error(f"Error setting up sample data: {e}")
        raise e

if __name__ == "__main__":
    # Test database setup
    try:
        db = get_database_manager()
        stats = db.get_database_stats()
        print("Database Statistics:")
        print(json.dumps(stats, indent=2, default=str))
        
        # Setup sample data if needed
        if stats["patients_count"] == 0:
            setup_sample_data()
            print("Sample data created")
        
    except Exception as e:
        print(f"Database setup error: {e}")
    finally:
        if db_manager:
            db_manager.close()
