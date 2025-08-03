import cv2
import numpy as np
from ultralytics import YOLO
import time
from typing import List, Tuple, Dict, Optional
import os

class VehicleDetector:
    """
    A comprehensive vehicle detection system using YOLO model.
    Supports real-time detection from video streams, images, and webcam.
    """
    
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        """
        Initialize the vehicle detector.
        
        Args:
            model_path: Path to YOLO model file or model name
            confidence_threshold: Minimum confidence score for detections
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.vehicle_classes = [2, 3, 5, 7]  # COCO dataset vehicle classes: car, motorcycle, bus, truck
        
        # Initialize YOLO model
        try:
            self.model = YOLO(model_path)
            print(f"Model loaded successfully: {model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Downloading YOLOv8n model...")
            self.model = YOLO("yolov8n.pt")
    
    def detect_vehicles(self, image: np.ndarray) -> List[Dict]:
        """
        Detect vehicles in an image.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of detection dictionaries with bounding boxes and confidence scores
        """
        if self.model is None:
            return []
        
        # Run YOLO detection
        results = self.model(image, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Get confidence and class
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    # Filter for vehicle classes and confidence threshold
                    if class_id in self.vehicle_classes and confidence >= self.confidence_threshold:
                        detection = {
                            'bbox': (int(x1), int(y1), int(x2), int(y2)),
                            'confidence': float(confidence),
                            'class_id': class_id,
                            'class_name': self._get_class_name(class_id)
                        }
                        detections.append(detection)
        
        return detections
    
    def _get_class_name(self, class_id: int) -> str:
        """Get class name from class ID."""
        class_names = {
            2: 'car',
            3: 'motorcycle',
            5: 'bus',
            7: 'truck'
        }
        return class_names.get(class_id, 'unknown')
    
    def draw_detections(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw bounding boxes and labels on the image.
        
        Args:
            image: Input image
            detections: List of detection dictionaries
            
        Returns:
            Image with drawn detections
        """
        result_image = image.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            confidence = detection['confidence']
            class_name = detection['class_name']
            
            # Draw bounding box
            cv2.rectangle(result_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # Draw label background
            cv2.rectangle(result_image, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), (0, 255, 0), -1)
            
            # Draw label text
            cv2.putText(result_image, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return result_image
    
    def detect_from_image(self, image_path: str, output_path: Optional[str] = None) -> np.ndarray:
        """
        Detect vehicles in an image file.
        
        Args:
            image_path: Path to input image
            output_path: Path to save output image (optional)
            
        Returns:
            Processed image with detections
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Detect vehicles
        detections = self.detect_vehicles(image)
        
        # Draw detections
        result_image = self.draw_detections(image, detections)
        
        # Add detection count
        cv2.putText(result_image, f"Vehicles detected: {len(detections)}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Save result if output path provided
        if output_path:
            cv2.imwrite(output_path, result_image)
            print(f"Result saved to: {output_path}")
        
        return result_image
    
    def detect_from_video(self, video_path: str, output_path: Optional[str] = None, 
                         show_video: bool = True) -> None:
        """
        Detect vehicles in a video file.
        
        Args:
            video_path: Path to input video
            output_path: Path to save output video (optional)
            show_video: Whether to display video during processing
        """
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Initialize video writer if output path provided
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect vehicles
            detections = self.detect_vehicles(frame)
            
            # Draw detections
            result_frame = self.draw_detections(frame, detections)
            
            # Add detection count and FPS
            cv2.putText(result_frame, f"Vehicles: {len(detections)}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Calculate and display FPS
            frame_count += 1
            elapsed_time = time.time() - start_time
            current_fps = frame_count / elapsed_time
            cv2.putText(result_frame, f"FPS: {current_fps:.1f}", 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Write frame if output path provided
            if writer:
                writer.write(result_frame)
            
            # Show frame if requested
            if show_video:
                cv2.imshow('Vehicle Detection', result_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        # Cleanup
        cap.release()
        if writer:
            writer.release()
        if show_video:
            cv2.destroyAllWindows()
        
        print(f"Processed {frame_count} frames in {elapsed_time:.2f} seconds")
    
    def detect_from_webcam(self, camera_id: int = 0, output_path: Optional[str] = None) -> None:
        """
        Detect vehicles from webcam feed.
        
        Args:
            camera_id: Camera device ID
            output_path: Path to save output video (optional)
        """
        # Open webcam
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            raise ValueError(f"Could not open camera: {camera_id}")
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Initialize video writer if output path provided
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, 20, (640, 480))
        
        frame_count = 0
        start_time = time.time()
        
        print("Press 'q' to quit, 's' to save current frame")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect vehicles
            detections = self.detect_vehicles(frame)
            
            # Draw detections
            result_frame = self.draw_detections(frame, detections)
            
            # Add detection count and FPS
            cv2.putText(result_frame, f"Vehicles: {len(detections)}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Calculate and display FPS
            frame_count += 1
            elapsed_time = time.time() - start_time
            current_fps = frame_count / elapsed_time
            cv2.putText(result_frame, f"FPS: {current_fps:.1f}", 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Write frame if output path provided
            if writer:
                writer.write(result_frame)
            
            # Show frame
            cv2.imshow('Vehicle Detection - Webcam', result_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save current frame
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"webcam_frame_{timestamp}.jpg"
                cv2.imwrite(filename, result_frame)
                print(f"Frame saved as: {filename}")
        
        # Cleanup
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        
        print(f"Processed {frame_count} frames in {elapsed_time:.2f} seconds")
    
    def get_detection_stats(self, detections: List[Dict]) -> Dict:
        """
        Get statistics about detections.
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            Dictionary with detection statistics
        """
        if not detections:
            return {
                'total_vehicles': 0,
                'vehicle_types': {},
                'average_confidence': 0.0,
                'confidence_range': (0.0, 0.0)
            }
        
        # Count vehicle types
        vehicle_types = {}
        confidences = []
        
        for detection in detections:
            class_name = detection['class_name']
            confidence = detection['confidence']
            
            vehicle_types[class_name] = vehicle_types.get(class_name, 0) + 1
            confidences.append(confidence)
        
        return {
            'total_vehicles': len(detections),
            'vehicle_types': vehicle_types,
            'average_confidence': np.mean(confidences),
            'confidence_range': (min(confidences), max(confidences))
        }