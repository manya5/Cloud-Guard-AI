from sklearn.ensemble import IsolationForest
import numpy as np
from datetime import datetime
import joblib

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        # Define thresholds for different features
        self.thresholds = {
            'file_size': 50,  # MB
            'unusual_hour_start': 23,  # 11 PM
            'unusual_hour_end': 5,     # 5 AM
        }
    
    def prepare_data(self, activities):
        features = []
        for activity in activities:
            try:
                # Extract timestamp features
                upload_time = None
                if activity.get('fileUploadedAt'):
                    upload_time = datetime.fromisoformat(str(activity['fileUploadedAt']).replace('Z', '+00:00'))
                
                hour = upload_time.hour if upload_time else 0
                day_of_week = upload_time.weekday() if upload_time else 0
                
                # Convert file size from KB to MB
                filesize_str = activity.get('filesize', '0 KB')
                file_size = float(filesize_str.replace(" KB", "")) / 1024
                
                # Convert activity type to numeric
                activity_type_map = {
                    "upload": 1,
                    "download": 2,
                    "delete": 3
                }
                activity_type = activity_type_map.get(activity.get('activityType', '').lower(), 0)
                
                # Check file extension
                file_extension = activity.get('fileExtension', '').lower()
                is_pdf = 1 if '.pdf' in file_extension else 0
                
                # Create feature vector
                feature_vector = [
                    hour,
                    day_of_week,
                    file_size,
                    activity_type,
                    is_pdf
                ]
                features.append(feature_vector)
            except Exception as e:
                print(f"Error processing activity: {e}")
                continue
            
        if not features:
            raise ValueError("No valid activity data found")
            
        return np.array(features)
    
    def get_anomaly_reason(self, activity, score):
        reasons = []
        
        # Check file size
        filesize_str = activity.get('filesize', '0 KB')
        file_size = float(filesize_str.replace(" KB", "")) / 1024  # Convert to MB
        if file_size > self.thresholds['file_size']:
            reasons.append(f"Unusual file size: {file_size:.2f} MB")

        # Check time of activity
        if activity.get('fileUploadedAt'):
            upload_time = datetime.fromisoformat(str(activity['fileUploadedAt']).replace('Z', '+00:00'))
            hour = upload_time.hour
            if hour >= self.thresholds['unusual_hour_start'] or hour <= self.thresholds['unusual_hour_end']:
                reasons.append(f"Unusual activity time: {hour:02d}:00")

        # Check activity type
        activity_type = activity.get('activityType', '').lower()
        if activity_type == 'delete':
            reasons.append("Delete operation detected")

        # Check file extension
        file_extension = activity.get('fileExtension', '').lower()
        suspicious_extensions = ['.exe', '.bat', '.sh', '.php']
        if any(ext in file_extension for ext in suspicious_extensions):
            reasons.append(f"Suspicious file extension: {file_extension}")

        # If no specific reasons found but still anomalous
        if not reasons and score < -0.5:  # You can adjust this threshold
            reasons.append("Unusual pattern detected based on historical activity")

        return " | ".join(reasons) if reasons else "Unknown anomaly pattern"

    def train(self, activities):
        try:
            X = self.prepare_data(activities)
            if len(X) > 0:
                self.model.fit(X)
                joblib.dump(self.model, 'anomaly_model.pkl')
                return True
            return False
        except Exception as e:
            print(f"Training error: {e}")
            return False
    
    def predict_with_score(self, activity):
        try:
            X = self.prepare_data([activity])
            prediction = self.model.predict(X)
            score = self.model.score_samples(X)
            
            is_anomaly = bool(prediction[0] == -1)
            anomaly_score = float(score[0])
            
            result = {
                'is_anomaly': is_anomaly,
                'anomaly_score': anomaly_score,
            }

            # If it's an anomaly, add the reason
            if is_anomaly:
                result['reason'] = self.get_anomaly_reason(activity, anomaly_score)
                
                # Add severity level based on anomaly score
                if anomaly_score < -0.8:
                    result['severity'] = 'high'
                elif anomaly_score < -0.6:
                    result['severity'] = 'medium'
                else:
                    result['severity'] = 'low'

            return result

        except Exception as e:
            print(f"Prediction error: {e}")
            return {
                'is_anomaly': False,
                'anomaly_score': 0.0,
                'error': str(e)
            }