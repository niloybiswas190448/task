# AI Implementation Guide for Construction Risk Management

## Technical Implementation Examples and Code Snippets

This guide provides practical implementation examples for AI applications in construction risk management, building upon the research report with detailed code snippets and technical specifications.

## 1. Computer Vision for Safety Monitoring

### Safety Violation Detection System

```python
import cv2
import numpy as np
from ultralytics import YOLO
import torch

class ConstructionSafetyMonitor:
    def __init__(self):
        # Load pre-trained models
        self.person_detector = YOLO('yolov8n.pt')
        self.ppe_detector = YOLO('ppe_detection_model.pt')
        self.hardhat_detector = YOLO('hardhat_detection.pt')
        
        # Safety violation thresholds
        self.safety_zones = []
        self.ppe_required = True
        self.hardhat_required = True
        
    def detect_safety_violations(self, frame):
        """Detect safety violations in a construction site frame"""
        violations = []
        
        # Detect people
        person_results = self.person_detector(frame)
        
        for person in person_results[0].boxes.data:
            x1, y1, x2, y2, conf, cls = person
            
            if cls == 0:  # Person class
                person_roi = frame[int(y1):int(y2), int(x1):int(x2)]
                
                # Check PPE compliance
                if self.ppe_required:
                    ppe_violation = self.check_ppe_compliance(person_roi)
                    if ppe_violation:
                        violations.append({
                            'type': 'PPE_VIOLATION',
                            'location': (int(x1), int(y1), int(x2), int(y2)),
                            'severity': 'HIGH'
                        })
                
                # Check hardhat compliance
                if self.hardhat_required:
                    hardhat_violation = self.check_hardhat_compliance(person_roi)
                    if hardhat_violation:
                        violations.append({
                            'type': 'HARDHAT_VIOLATION',
                            'location': (int(x1), int(y1), int(x2), int(y2)),
                            'severity': 'CRITICAL'
                        })
                
                # Check safety zone violations
                zone_violation = self.check_safety_zones((x1, y1, x2, y2))
                if zone_violation:
                    violations.append({
                        'type': 'SAFETY_ZONE_VIOLATION',
                        'location': (int(x1), int(y1), int(x2), int(y2)),
                        'severity': 'HIGH'
                    })
        
        return violations
    
    def check_ppe_compliance(self, person_roi):
        """Check if person is wearing required PPE"""
        ppe_results = self.ppe_detector(person_roi)
        required_items = ['vest', 'gloves', 'safety_glasses']
        detected_items = []
        
        for detection in ppe_results[0].boxes.data:
            cls = int(detection[5])
            conf = detection[4]
            if conf > 0.7:  # High confidence threshold
                detected_items.append(self.ppe_classes[cls])
        
        missing_items = set(required_items) - set(detected_items)
        return len(missing_items) > 0
    
    def check_hardhat_compliance(self, person_roi):
        """Check if person is wearing hardhat"""
        hardhat_results = self.hardhat_detector(person_roi)
        
        for detection in hardhat_results[0].boxes.data:
            conf = detection[4]
            if conf > 0.8:  # High confidence for hardhat detection
                return False  # Hardhat detected, no violation
        
        return True  # No hardhat detected, violation
    
    def check_safety_zones(self, person_bbox):
        """Check if person is in restricted safety zones"""
        person_center = ((person_bbox[0] + person_bbox[2]) / 2, 
                        (person_bbox[1] + person_bbox[3]) / 2)
        
        for zone in self.safety_zones:
            if self.point_in_polygon(person_center, zone):
                return True
        
        return False
    
    def point_in_polygon(self, point, polygon):
        """Check if point is inside polygon"""
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside

# Usage example
def main():
    monitor = ConstructionSafetyMonitor()
    cap = cv2.VideoCapture(0)  # Use camera or video file
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        violations = monitor.detect_safety_violations(frame)
        
        # Draw violations on frame
        for violation in violations:
            x1, y1, x2, y2 = violation['location']
            color = (0, 0, 255) if violation['severity'] == 'CRITICAL' else (0, 165, 255)
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, violation['type'], (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        cv2.imshow('Safety Monitoring', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
```

## 2. Predictive Analytics for Risk Assessment

### Project Risk Prediction Model

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

class ConstructionRiskPredictor:
    def __init__(self):
        self.schedule_model = None
        self.cost_model = None
        self.safety_model = None
        self.scaler = StandardScaler()
        
    def prepare_features(self, project_data):
        """Prepare features for risk prediction"""
        features = []
        
        # Project characteristics
        features.extend([
            project_data['project_size'],  # Square footage
            project_data['complexity_score'],  # 1-10 scale
            project_data['duration_months'],
            project_data['budget_millions'],
            project_data['team_size']
        ])
        
        # Environmental factors
        features.extend([
            project_data['weather_risk_score'],
            project_data['site_conditions_score'],
            project_data['regulatory_complexity']
        ])
        
        # Resource availability
        features.extend([
            project_data['material_availability'],
            project_data['labor_availability'],
            project_data['equipment_availability']
        ])
        
        # Historical performance
        features.extend([
            project_data['company_safety_record'],
            project_data['company_schedule_performance'],
            project_data['company_cost_performance']
        ])
        
        return np.array(features).reshape(1, -1)
    
    def train_schedule_risk_model(self, training_data):
        """Train model to predict schedule risk"""
        X = training_data[['project_size', 'complexity_score', 'duration_months', 
                          'weather_risk_score', 'team_size', 'material_availability']]
        y = training_data['schedule_delay_percentage']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        self.schedule_model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        self.schedule_model.fit(X_train, y_train)
        
        # Evaluate model
        train_score = self.schedule_model.score(X_train, y_train)
        test_score = self.schedule_model.score(X_test, y_test)
        
        print(f"Schedule Risk Model - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
        
        return self.schedule_model
    
    def train_cost_risk_model(self, training_data):
        """Train model to predict cost overrun risk"""
        X = training_data[['project_size', 'complexity_score', 'budget_millions',
                          'duration_months', 'material_availability', 'regulatory_complexity']]
        y = training_data['cost_overrun_percentage']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        self.cost_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.cost_model.fit(X_train, y_train)
        
        # Evaluate model
        train_score = self.cost_model.score(X_train, y_train)
        test_score = self.cost_model.score(X_test, y_test)
        
        print(f"Cost Risk Model - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
        
        return self.cost_model
    
    def predict_project_risks(self, project_data):
        """Predict comprehensive project risks"""
        features = self.prepare_features(project_data)
        features_scaled = self.scaler.fit_transform(features)
        
        predictions = {}
        
        if self.schedule_model:
            schedule_risk = self.schedule_model.predict(features_scaled)[0]
            predictions['schedule_risk'] = {
                'delay_percentage': schedule_risk,
                'risk_level': self.categorize_risk(schedule_risk, 'schedule'),
                'confidence': self.calculate_confidence(schedule_risk)
            }
        
        if self.cost_model:
            cost_risk = self.cost_model.predict(features_scaled)[0]
            predictions['cost_risk'] = {
                'overrun_percentage': cost_risk,
                'risk_level': self.categorize_risk(cost_risk, 'cost'),
                'confidence': self.calculate_confidence(cost_risk)
            }
        
        # Calculate overall risk score
        overall_risk = self.calculate_overall_risk(predictions)
        predictions['overall_risk'] = overall_risk
        
        return predictions
    
    def categorize_risk(self, risk_value, risk_type):
        """Categorize risk level based on value"""
        if risk_type == 'schedule':
            if risk_value < 5:
                return 'LOW'
            elif risk_value < 15:
                return 'MEDIUM'
            else:
                return 'HIGH'
        elif risk_type == 'cost':
            if risk_value < 3:
                return 'LOW'
            elif risk_value < 10:
                return 'MEDIUM'
            else:
                return 'HIGH'
    
    def calculate_confidence(self, prediction):
        """Calculate confidence level for prediction"""
        # Simplified confidence calculation
        # In practice, this would use model uncertainty estimates
        return 0.85  # Placeholder
    
    def calculate_overall_risk(self, predictions):
        """Calculate overall project risk score"""
        risk_scores = []
        
        if 'schedule_risk' in predictions:
            schedule_score = self.risk_level_to_score(predictions['schedule_risk']['risk_level'])
            risk_scores.append(schedule_score * 0.4)  # 40% weight
        
        if 'cost_risk' in predictions:
            cost_score = self.risk_level_to_score(predictions['cost_risk']['risk_level'])
            risk_scores.append(cost_score * 0.4)  # 40% weight
        
        # Add safety risk (placeholder)
        safety_score = 0.2  # Placeholder
        risk_scores.append(safety_score * 0.2)  # 20% weight
        
        overall_score = sum(risk_scores)
        
        return {
            'score': overall_score,
            'level': self.score_to_risk_level(overall_score),
            'recommendations': self.generate_recommendations(predictions)
        }
    
    def risk_level_to_score(self, risk_level):
        """Convert risk level to numerical score"""
        mapping = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}
        return mapping.get(risk_level, 2)
    
    def score_to_risk_level(self, score):
        """Convert numerical score to risk level"""
        if score < 1.5:
            return 'LOW'
        elif score < 2.5:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def generate_recommendations(self, predictions):
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        if 'schedule_risk' in predictions:
            if predictions['schedule_risk']['risk_level'] == 'HIGH':
                recommendations.append("Implement accelerated construction methods")
                recommendations.append("Increase resource allocation")
                recommendations.append("Develop contingency schedules")
        
        if 'cost_risk' in predictions:
            if predictions['cost_risk']['risk_level'] == 'HIGH':
                recommendations.append("Implement cost control measures")
                recommendations.append("Negotiate fixed-price contracts")
                recommendations.append("Establish cost monitoring systems")
        
        return recommendations

# Usage example
def example_risk_prediction():
    predictor = ConstructionRiskPredictor()
    
    # Sample project data
    project_data = {
        'project_size': 50000,  # sq ft
        'complexity_score': 7,  # 1-10
        'duration_months': 18,
        'budget_millions': 25,
        'team_size': 45,
        'weather_risk_score': 6,
        'site_conditions_score': 4,
        'regulatory_complexity': 5,
        'material_availability': 0.8,
        'labor_availability': 0.7,
        'equipment_availability': 0.9,
        'company_safety_record': 0.95,
        'company_schedule_performance': 0.88,
        'company_cost_performance': 0.92
    }
    
    # Predict risks
    risks = predictor.predict_project_risks(project_data)
    
    print("Project Risk Assessment:")
    print(f"Overall Risk Level: {risks['overall_risk']['level']}")
    print(f"Overall Risk Score: {risks['overall_risk']['score']:.2f}")
    
    if 'schedule_risk' in risks:
        print(f"Schedule Risk: {risks['schedule_risk']['risk_level']} "
              f"({risks['schedule_risk']['delay_percentage']:.1f}% delay)")
    
    if 'cost_risk' in risks:
        print(f"Cost Risk: {risks['cost_risk']['risk_level']} "
              f"({risks['cost_risk']['overrun_percentage']:.1f}% overrun)")
    
    print("\nRecommendations:")
    for rec in risks['overall_risk']['recommendations']:
        print(f"- {rec}")
```

## 3. IoT and Sensor Integration

### Environmental Monitoring System

```python
import time
import json
import requests
from datetime import datetime
import threading

class EnvironmentalMonitor:
    def __init__(self):
        self.sensors = {
            'air_quality': None,
            'noise_level': None,
            'vibration': None,
            'temperature': None,
            'humidity': None
        }
        self.thresholds = {
            'air_quality': {'min': 0, 'max': 100, 'critical': 150},
            'noise_level': {'min': 0, 'max': 85, 'critical': 100},
            'vibration': {'min': 0, 'max': 2.0, 'critical': 5.0},
            'temperature': {'min': -10, 'max': 40, 'critical': 50},
            'humidity': {'min': 20, 'max': 80, 'critical': 95}
        }
        self.alerts = []
        self.monitoring_active = False
    
    def initialize_sensors(self):
        """Initialize IoT sensors"""
        # In practice, this would connect to actual sensors
        # For demonstration, we'll simulate sensor data
        print("Initializing environmental sensors...")
        
        # Simulate sensor initialization
        for sensor_type in self.sensors:
            self.sensors[sensor_type] = {
                'connected': True,
                'last_reading': None,
                'last_update': None
            }
        
        print("All sensors initialized successfully")
    
    def read_sensor_data(self, sensor_type):
        """Read data from specific sensor"""
        # Simulate sensor reading
        if sensor_type == 'air_quality':
            return np.random.normal(50, 15)  # PM2.5 levels
        elif sensor_type == 'noise_level':
            return np.random.normal(70, 10)  # dB levels
        elif sensor_type == 'vibration':
            return np.random.normal(1.0, 0.5)  # mm/s
        elif sensor_type == 'temperature':
            return np.random.normal(25, 8)  # Celsius
        elif sensor_type == 'humidity':
            return np.random.normal(60, 15)  # Percentage
        
        return None
    
    def check_thresholds(self, sensor_type, value):
        """Check if sensor reading exceeds thresholds"""
        threshold = self.thresholds[sensor_type]
        
        if value > threshold['critical']:
            return 'CRITICAL'
        elif value > threshold['max'] or value < threshold['min']:
            return 'WARNING'
        else:
            return 'NORMAL'
    
    def generate_alert(self, sensor_type, value, status):
        """Generate environmental alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'sensor_type': sensor_type,
            'value': value,
            'status': status,
            'threshold': self.thresholds[sensor_type],
            'message': self.get_alert_message(sensor_type, value, status)
        }
        
        self.alerts.append(alert)
        return alert
    
    def get_alert_message(self, sensor_type, value, status):
        """Generate alert message"""
        messages = {
            'air_quality': {
                'WARNING': f"Air quality is elevated: {value:.1f} PM2.5",
                'CRITICAL': f"Air quality is critical: {value:.1f} PM2.5 - Consider work stoppage"
            },
            'noise_level': {
                'WARNING': f"Noise level is high: {value:.1f} dB",
                'CRITICAL': f"Noise level is critical: {value:.1f} dB - Provide hearing protection"
            },
            'vibration': {
                'WARNING': f"Vibration levels elevated: {value:.2f} mm/s",
                'CRITICAL': f"Vibration levels critical: {value:.2f} mm/s - Check equipment"
            },
            'temperature': {
                'WARNING': f"Temperature is {value:.1f}°C - Monitor worker comfort",
                'CRITICAL': f"Temperature is critical: {value:.1f}°C - Implement heat stress measures"
            },
            'humidity': {
                'WARNING': f"Humidity is {value:.1f}% - Monitor condensation",
                'CRITICAL': f"Humidity is critical: {value:.1f}% - Check for moisture damage"
            }
        }
        
        return messages[sensor_type].get(status, f"{sensor_type} reading: {value}")
    
    def monitor_environment(self):
        """Continuous environmental monitoring"""
        self.monitoring_active = True
        
        while self.monitoring_active:
            for sensor_type in self.sensors:
                if self.sensors[sensor_type]['connected']:
                    # Read sensor data
                    value = self.read_sensor_data(sensor_type)
                    
                    # Update sensor status
                    self.sensors[sensor_type]['last_reading'] = value
                    self.sensors[sensor_type]['last_update'] = datetime.now()
                    
                    # Check thresholds
                    status = self.check_thresholds(sensor_type, value)
                    
                    # Generate alert if needed
                    if status in ['WARNING', 'CRITICAL']:
                        alert = self.generate_alert(sensor_type, value, status)
                        self.send_alert(alert)
            
            # Wait before next reading
            time.sleep(30)  # 30-second intervals
    
    def send_alert(self, alert):
        """Send alert to relevant parties"""
        print(f"ALERT: {alert['message']}")
        
        # In practice, this would send alerts via:
        # - Email notifications
        # - SMS messages
        # - Dashboard updates
        # - Mobile app notifications
        
        # Example: Send to webhook
        try:
            response = requests.post(
                'https://api.example.com/alerts',
                json=alert,
                timeout=5
            )
            if response.status_code == 200:
                print(f"Alert sent successfully: {alert['sensor_type']}")
        except Exception as e:
            print(f"Failed to send alert: {e}")
    
    def get_current_readings(self):
        """Get current sensor readings"""
        readings = {}
        for sensor_type, sensor_data in self.sensors.items():
            if sensor_data['connected']:
                readings[sensor_type] = {
                    'value': sensor_data['last_reading'],
                    'timestamp': sensor_data['last_update'],
                    'status': self.check_thresholds(sensor_type, sensor_data['last_reading'])
                }
        return readings
    
    def get_alert_history(self, hours=24):
        """Get alert history for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > cutoff_time
        ]
        return recent_alerts
    
    def stop_monitoring(self):
        """Stop environmental monitoring"""
        self.monitoring_active = False
        print("Environmental monitoring stopped")

# Usage example
def example_environmental_monitoring():
    monitor = EnvironmentalMonitor()
    monitor.initialize_sensors()
    
    # Start monitoring in background thread
    monitor_thread = threading.Thread(target=monitor.monitor_environment)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Monitor for 5 minutes
    time.sleep(300)
    
    # Get current readings
    readings = monitor.get_current_readings()
    print("\nCurrent Environmental Readings:")
    for sensor_type, data in readings.items():
        print(f"{sensor_type}: {data['value']:.2f} ({data['status']})")
    
    # Get alert history
    alerts = monitor.get_alert_history(hours=1)
    print(f"\nAlerts in last hour: {len(alerts)}")
    for alert in alerts[-3:]:  # Last 3 alerts
        print(f"- {alert['message']}")
    
    # Stop monitoring
    monitor.stop_monitoring()
```

## 4. Automated Quality Control

### Computer Vision Quality Inspection

```python
import cv2
import numpy as np
from ultralytics import YOLO
import json

class QualityInspector:
    def __init__(self):
        self.defect_detector = YOLO('defect_detection_model.pt')
        self.material_classifier = YOLO('material_classification.pt')
        self.measurement_model = None  # Custom measurement model
        
        self.quality_standards = {
            'concrete': {
                'cracking_threshold': 0.5,  # mm
                'surface_roughness_max': 3.0,  # mm
                'color_variation_max': 0.1
            },
            'steel': {
                'rust_threshold': 0.1,  # percentage
                'deformation_max': 2.0,  # mm
                'weld_quality_min': 0.8
            },
            'wood': {
                'moisture_max': 12.0,  # percentage
                'crack_width_max': 1.0,  # mm
                'knot_size_max': 0.3  # percentage
            }
        }
    
    def inspect_structural_element(self, image_path, element_type):
        """Comprehensive quality inspection of structural element"""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        inspection_results = {
            'element_type': element_type,
            'timestamp': datetime.now().isoformat(),
            'overall_quality': 'PASS',
            'defects': [],
            'measurements': {},
            'recommendations': []
        }
        
        # Detect defects
        defects = self.detect_defects(image, element_type)
        inspection_results['defects'] = defects
        
        # Perform measurements
        measurements = self.perform_measurements(image, element_type)
        inspection_results['measurements'] = measurements
        
        # Assess quality
        quality_assessment = self.assess_quality(defects, measurements, element_type)
        inspection_results['overall_quality'] = quality_assessment['status']
        inspection_results['recommendations'] = quality_assessment['recommendations']
        
        return inspection_results
    
    def detect_defects(self, image, element_type):
        """Detect defects in structural element"""
        defects = []
        
        # Run defect detection model
        results = self.defect_detector(image)
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    if confidence > 0.7:  # High confidence threshold
                        defect_type = self.get_defect_type(class_id, element_type)
                        defect = {
                            'type': defect_type,
                            'location': (int(x1), int(y1), int(x2), int(y2)),
                            'confidence': float(confidence),
                            'severity': self.assess_defect_severity(defect_type, confidence)
                        }
                        defects.append(defect)
        
        return defects
    
    def get_defect_type(self, class_id, element_type):
        """Map class ID to defect type based on element type"""
        defect_mapping = {
            'concrete': {
                0: 'cracking',
                1: 'spalling',
                2: 'honeycombing',
                3: 'surface_roughness',
                4: 'color_variation'
            },
            'steel': {
                0: 'rust',
                1: 'deformation',
                2: 'weld_defect',
                3: 'corrosion',
                4: 'surface_damage'
            },
            'wood': {
                0: 'cracking',
                1: 'knots',
                2: 'moisture_damage',
                3: 'insect_damage',
                4: 'decay'
            }
        }
        
        return defect_mapping.get(element_type, {}).get(class_id, 'unknown')
    
    def assess_defect_severity(self, defect_type, confidence):
        """Assess severity of detected defect"""
        if confidence > 0.9:
            return 'CRITICAL'
        elif confidence > 0.8:
            return 'HIGH'
        elif confidence > 0.7:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def perform_measurements(self, image, element_type):
        """Perform measurements on structural element"""
        measurements = {}
        
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get largest contour (assumed to be the main element)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Calculate measurements
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            
            # Bounding rectangle
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            measurements = {
                'area_pixels': area,
                'perimeter_pixels': perimeter,
                'width_pixels': w,
                'height_pixels': h,
                'aspect_ratio': w / h if h > 0 else 0
            }
            
            # Convert to real-world measurements (if calibration data available)
            # measurements = self.convert_to_real_units(measurements)
        
        return measurements
    
    def assess_quality(self, defects, measurements, element_type):
        """Assess overall quality based on defects and measurements"""
        standards = self.quality_standards.get(element_type, {})
        
        quality_status = 'PASS'
        recommendations = []
        
        # Check defect severity
        critical_defects = [d for d in defects if d['severity'] == 'CRITICAL']
        high_defects = [d for d in defects if d['severity'] == 'HIGH']
        
        if critical_defects:
            quality_status = 'FAIL'
            recommendations.append("Critical defects detected - immediate remediation required")
        
        if high_defects:
            if quality_status == 'PASS':
                quality_status = 'CONDITIONAL'
            recommendations.append("High severity defects detected - schedule remediation")
        
        # Check measurements against standards
        if element_type == 'concrete':
            if measurements.get('aspect_ratio', 0) > 3.0:
                recommendations.append("High aspect ratio detected - check for structural issues")
        
        # Add general recommendations
        if len(defects) > 5:
            recommendations.append("Multiple defects detected - consider comprehensive inspection")
        
        return {
            'status': quality_status,
            'recommendations': recommendations
        }
    
    def generate_inspection_report(self, inspection_results):
        """Generate detailed inspection report"""
        report = {
            'inspection_summary': {
                'element_type': inspection_results['element_type'],
                'timestamp': inspection_results['timestamp'],
                'overall_quality': inspection_results['overall_quality'],
                'total_defects': len(inspection_results['defects']),
                'critical_defects': len([d for d in inspection_results['defects'] 
                                       if d['severity'] == 'CRITICAL'])
            },
            'defect_details': inspection_results['defects'],
            'measurements': inspection_results['measurements'],
            'recommendations': inspection_results['recommendations'],
            'compliance_status': self.check_compliance(inspection_results)
        }
        
        return report
    
    def check_compliance(self, inspection_results):
        """Check compliance with building codes and standards"""
        compliance = {
            'building_code': 'COMPLIANT',
            'safety_standards': 'COMPLIANT',
            'quality_standards': 'COMPLIANT'
        }
        
        # Check for critical defects
        critical_defects = [d for d in inspection_results['defects'] 
                          if d['severity'] == 'CRITICAL']
        
        if critical_defects:
            compliance['safety_standards'] = 'NON_COMPLIANT'
            compliance['quality_standards'] = 'NON_COMPLIANT'
        
        return compliance

# Usage example
def example_quality_inspection():
    inspector = QualityInspector()
    
    # Inspect concrete element
    try:
        results = inspector.inspect_structural_element(
            'concrete_slab.jpg', 
            'concrete'
        )
        
        # Generate report
        report = inspector.generate_inspection_report(results)
        
        print("Quality Inspection Report:")
        print(f"Element Type: {report['inspection_summary']['element_type']}")
        print(f"Overall Quality: {report['inspection_summary']['overall_quality']}")
        print(f"Total Defects: {report['inspection_summary']['total_defects']}")
        print(f"Critical Defects: {report['inspection_summary']['critical_defects']}")
        
        print("\nDefects Found:")
        for defect in report['defect_details']:
            print(f"- {defect['type']}: {defect['severity']} (confidence: {defect['confidence']:.2f})")
        
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"- {rec}")
        
        print(f"\nCompliance Status: {report['compliance_status']}")
        
    except Exception as e:
        print(f"Inspection failed: {e}")
```

## 5. Integration and Dashboard

### Construction Risk Management Dashboard

```python
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

class ConstructionRiskDashboard:
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.safety_monitor = ConstructionSafetyMonitor()
        self.risk_predictor = ConstructionRiskPredictor()
        self.environmental_monitor = EnvironmentalMonitor()
        self.quality_inspector = QualityInspector()
        
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Setup dashboard layout"""
        self.app.layout = html.Div([
            html.H1("Construction Risk Management Dashboard", 
                   style={'textAlign': 'center', 'color': '#2c3e50'}),
            
            # Risk Overview Section
            html.Div([
                html.H2("Project Risk Overview"),
                dcc.Graph(id='risk-overview-chart'),
                dcc.Interval(id='risk-update-interval', interval=300000)  # 5 minutes
            ], style={'margin': '20px'}),
            
            # Safety Monitoring Section
            html.Div([
                html.H2("Safety Monitoring"),
                html.Div([
                    html.Div([
                        dcc.Graph(id='safety-violations-chart'),
                        dcc.Graph(id='ppe-compliance-chart')
                    ], style={'display': 'flex', 'justifyContent': 'space-between'})
                ]),
                dcc.Interval(id='safety-update-interval', interval=60000)  # 1 minute
            ], style={'margin': '20px'}),
            
            # Environmental Monitoring Section
            html.Div([
                html.H2("Environmental Conditions"),
                dcc.Graph(id='environmental-chart'),
                dcc.Interval(id='environmental-update-interval', interval=30000)  # 30 seconds
            ], style={'margin': '20px'}),
            
            # Quality Control Section
            html.Div([
                html.H2("Quality Control"),
                dcc.Graph(id='quality-chart'),
                html.Div(id='quality-alerts')
            ], style={'margin': '20px'}),
            
            # Alerts and Notifications
            html.Div([
                html.H2("Active Alerts"),
                html.Div(id='alerts-container'),
                dcc.Interval(id='alerts-update-interval', interval=10000)  # 10 seconds
            ], style={'margin': '20px'})
        ])
    
    def setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        @self.app.callback(
            Output('risk-overview-chart', 'figure'),
            Input('risk-update-interval', 'n_intervals')
        )
        def update_risk_overview(n):
            # Simulate risk data
            risk_data = {
                'Safety': 15,
                'Schedule': 25,
                'Cost': 20,
                'Quality': 10,
                'Environmental': 5
            }
            
            fig = go.Figure(data=[
                go.Bar(
                    x=list(risk_data.keys()),
                    y=list(risk_data.values()),
                    marker_color=['#e74c3c', '#f39c12', '#f1c40f', '#27ae60', '#3498db']
                )
            ])
            
            fig.update_layout(
                title="Current Risk Levels by Category",
                xaxis_title="Risk Categories",
                yaxis_title="Risk Score (%)",
                height=400
            )
            
            return fig
        
        @self.app.callback(
            Output('safety-violations-chart', 'figure'),
            Input('safety-update-interval', 'n_intervals')
        )
        def update_safety_violations(n):
            # Simulate safety violation data
            violations_data = {
                'PPE Violations': 3,
                'Safety Zone Violations': 1,
                'Equipment Misuse': 2,
                'Fall Hazards': 0
            }
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=list(violations_data.keys()),
                    values=list(violations_data.values()),
                    hole=0.4
                )
            ])
            
            fig.update_layout(
                title="Safety Violations by Type",
                height=300
            )
            
            return fig
        
        @self.app.callback(
            Output('environmental-chart', 'figure'),
            Input('environmental-update-interval', 'n_intervals')
        )
        def update_environmental_data(n):
            # Simulate environmental data
            time_points = pd.date_range(start=datetime.now() - timedelta(hours=6), 
                                      end=datetime.now(), freq='H')
            
            air_quality = np.random.normal(50, 10, len(time_points))
            noise_level = np.random.normal(70, 5, len(time_points))
            temperature = np.random.normal(25, 3, len(time_points))
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=time_points,
                y=air_quality,
                mode='lines+markers',
                name='Air Quality (PM2.5)',
                line=dict(color='#e74c3c')
            ))
            
            fig.add_trace(go.Scatter(
                x=time_points,
                y=noise_level,
                mode='lines+markers',
                name='Noise Level (dB)',
                line=dict(color='#f39c12'),
                yaxis='y2'
            ))
            
            fig.add_trace(go.Scatter(
                x=time_points,
                y=temperature,
                mode='lines+markers',
                name='Temperature (°C)',
                line=dict(color='#3498db'),
                yaxis='y3'
            ))
            
            fig.update_layout(
                title="Environmental Conditions Over Time",
                xaxis_title="Time",
                yaxis=dict(title="Air Quality (PM2.5)", side="left"),
                yaxis2=dict(title="Noise Level (dB)", side="right", overlaying="y"),
                yaxis3=dict(title="Temperature (°C)", side="right", overlaying="y", position=0.95),
                height=400
            )
            
            return fig
        
        @self.app.callback(
            Output('quality-chart', 'figure'),
            Input('environmental-update-interval', 'n_intervals')
        )
        def update_quality_data(n):
            # Simulate quality inspection data
            quality_data = {
                'Passed': 85,
                'Conditional': 10,
                'Failed': 5
            }
            
            fig = go.Figure(data=[
                go.Bar(
                    x=list(quality_data.keys()),
                    y=list(quality_data.values()),
                    marker_color=['#27ae60', '#f39c12', '#e74c3c']
                )
            ])
            
            fig.update_layout(
                title="Quality Inspection Results",
                xaxis_title="Inspection Status",
                yaxis_title="Number of Inspections",
                height=300
            )
            
            return fig
        
        @self.app.callback(
            Output('alerts-container', 'children'),
            Input('alerts-update-interval', 'n_intervals')
        )
        def update_alerts(n):
            # Simulate alerts
            alerts = [
                {'type': 'Safety', 'message': 'PPE violation detected in Zone A', 'severity': 'HIGH'},
                {'type': 'Environmental', 'message': 'Noise levels approaching limit', 'severity': 'MEDIUM'},
                {'type': 'Quality', 'message': 'Concrete curing temperature optimal', 'severity': 'LOW'}
            ]
            
            alert_cards = []
            for alert in alerts:
                color_map = {'HIGH': '#e74c3c', 'MEDIUM': '#f39c12', 'LOW': '#27ae60'}
                
                card = html.Div([
                    html.H4(alert['type'], style={'margin': '0'}),
                    html.P(alert['message']),
                    html.Span(alert['severity'], 
                             style={'backgroundColor': color_map[alert['severity']], 
                                   'color': 'white', 'padding': '2px 8px', 'borderRadius': '4px'})
                ], style={
                    'border': '1px solid #ddd',
                    'borderRadius': '8px',
                    'padding': '15px',
                    'margin': '10px 0',
                    'backgroundColor': '#f8f9fa'
                })
                
                alert_cards.append(card)
            
            return alert_cards
    
    def run_dashboard(self, debug=True, port=8050):
        """Run the dashboard"""
        print(f"Starting Construction Risk Management Dashboard on port {port}")
        self.app.run_server(debug=debug, port=port)

# Usage example
def example_dashboard():
    dashboard = ConstructionRiskDashboard()
    dashboard.run_dashboard(debug=True, port=8050)

if __name__ == "__main__":
    example_dashboard()
```

## Summary

This implementation guide provides practical examples of AI applications in construction risk management, including:

1. **Computer Vision for Safety Monitoring**: Real-time detection of safety violations, PPE compliance, and hazardous situations
2. **Predictive Analytics**: Machine learning models for predicting project risks and optimizing schedules
3. **IoT and Environmental Monitoring**: Sensor-based monitoring of environmental conditions
4. **Automated Quality Control**: Computer vision-based inspection systems
5. **Integrated Dashboard**: Comprehensive risk management dashboard

These implementations demonstrate how AI can be effectively integrated into construction projects to enhance safety, improve quality, and reduce risks. The code examples can be adapted and extended based on specific project requirements and available technologies.

For production deployment, additional considerations include:
- Data security and privacy
- System scalability and performance
- Integration with existing construction management systems
- Training and change management
- Regulatory compliance
- Continuous monitoring and improvement