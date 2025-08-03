import cv2
import numpy as np
from ultralytics import YOLO
import time
from typing import List, Dict, Tuple, Optional
from collections import defaultdict, deque
import math

class AdvancedVehicleDetector:
    """
    Advanced vehicle detection system with tracking, counting, and lane analysis.
    """
    
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        """
        Initialize the advanced vehicle detector.
        
        Args:
            model_path: Path to YOLO model file
            confidence_threshold: Minimum confidence score for detections
        """
        self.confidence_threshold = confidence_threshold
        self.model = YOLO(model_path)
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        
        # Tracking variables
        self.trackers = {}
        self.next_tracker_id = 1
        self.tracker_history = defaultdict(lambda: deque(maxlen=30))
        self.vehicle_count = defaultdict(int)
        self.lane_lines = []
        
        # Detection zones
        self.counting_line_y = None
        self.counting_zone = None
        
    def detect_vehicles(self, image: np.ndarray) -> List[Dict]:
        """Detect vehicles in an image."""
        results = self.model(image, verbose=False)
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    if class_id in self.vehicle_classes and confidence >= self.confidence_threshold:
                        detection = {
                            'bbox': (int(x1), int(y1), int(x2), int(y2)),
                            'confidence': float(confidence),
                            'class_id': class_id,
                            'class_name': self._get_class_name(class_id),
                            'center': (int((x1 + x2) / 2), int((y1 + y2) / 2))
                        }
                        detections.append(detection)
        
        return detections
    
    def _get_class_name(self, class_id: int) -> str:
        """Get class name from class ID."""
        class_names = {2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}
        return class_names.get(class_id, 'unknown')
    
    def update_tracking(self, detections: List[Dict]) -> List[Dict]:
        """
        Update vehicle tracking using simple centroid tracking.
        
        Args:
            detections: List of current detections
            
        Returns:
            List of detections with tracking IDs
        """
        current_trackers = {}
        
        for detection in detections:
            center = detection['center']
            min_distance = float('inf')
            matched_id = None
            
            # Find closest existing tracker
            for tracker_id, tracker_center in self.trackers.items():
                distance = math.sqrt((center[0] - tracker_center[0])**2 + 
                                   (center[1] - tracker_center[1])**2)
                if distance < min_distance and distance < 100:  # Max distance threshold
                    min_distance = distance
                    matched_id = tracker_id
            
            if matched_id is not None:
                # Update existing tracker
                current_trackers[matched_id] = center
                detection['tracker_id'] = matched_id
                self.tracker_history[matched_id].append(center)
            else:
                # Create new tracker
                current_trackers[self.next_tracker_id] = center
                detection['tracker_id'] = self.next_tracker_id
                self.tracker_history[self.next_tracker_id].append(center)
                self.next_tracker_id += 1
        
        # Update trackers
        self.trackers = current_trackers
        
        return detections
    
    def detect_lanes(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Detect lane lines in the image.
        
        Args:
            image: Input image
            
        Returns:
            List of detected lane lines
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Define region of interest (ROI)
        height, width = edges.shape
        roi_vertices = np.array([
            [(0, height), (width/2, height/2), (width, height)]
        ], dtype=np.int32)
        
        mask = np.zeros_like(edges)
        cv2.fillPoly(mask, roi_vertices, 255)
        masked_edges = cv2.bitwise_and(edges, mask)
        
        # Hough line detection
        lines = cv2.HoughLinesP(masked_edges, 1, np.pi/180, 
                               threshold=50, minLineLength=100, maxLineGap=50)
        
        lane_lines = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # Filter for horizontal lines (potential lane markers)
                if abs(y2 - y1) < 50:  # Nearly horizontal
                    lane_lines.append(line[0])
        
        return lane_lines
    
    def set_counting_zone(self, y_position: int):
        """Set the counting line at a specific y-position."""
        self.counting_line_y = y_position
    
    def count_vehicles(self, detections: List[Dict]) -> Dict:
        """
        Count vehicles crossing the counting line.
        
        Args:
            detections: List of tracked detections
            
        Returns:
            Dictionary with counting statistics
        """
        if self.counting_line_y is None:
            return {}
        
        for detection in detections:
            tracker_id = detection.get('tracker_id')
            if tracker_id and tracker_id in self.tracker_history:
                history = self.tracker_history[tracker_id]
                if len(history) >= 2:
                    # Check if vehicle crossed the counting line
                    prev_y = history[-2][1]
                    curr_y = history[-1][1]
                    
                    if prev_y < self.counting_line_y and curr_y >= self.counting_line_y:
                        # Vehicle crossed the line downward
                        vehicle_type = detection['class_name']
                        self.vehicle_count[vehicle_type] += 1
                        print(f"Vehicle counted: {vehicle_type} (ID: {tracker_id})")
        
        return dict(self.vehicle_count)
    
    def estimate_speed(self, tracker_id: int, fps: float = 30.0) -> Optional[float]:
        """
        Estimate vehicle speed based on tracking history.
        
        Args:
            tracker_id: Tracking ID of the vehicle
            fps: Frames per second of the video
            
        Returns:
            Estimated speed in pixels per second
        """
        if tracker_id not in self.tracker_history:
            return None
        
        history = self.tracker_history[tracker_id]
        if len(history) < 2:
            return None
        
        # Calculate displacement over time
        start_pos = history[0]
        end_pos = history[-1]
        
        distance = math.sqrt((end_pos[0] - start_pos[0])**2 + 
                           (end_pos[1] - start_pos[1])**2)
        
        time_elapsed = len(history) / fps
        
        if time_elapsed > 0:
            speed = distance / time_elapsed
            return speed
        
        return None
    
    def draw_advanced_detections(self, image: np.ndarray, detections: List[Dict], 
                                show_tracking: bool = True, show_lanes: bool = True) -> np.ndarray:
        """
        Draw advanced visualizations including tracking, counting, and lanes.
        
        Args:
            image: Input image
            detections: List of detections with tracking info
            show_tracking: Whether to show tracking paths
            show_lanes: Whether to show detected lanes
            
        Returns:
            Image with advanced visualizations
        """
        result_image = image.copy()
        
        # Draw lane lines
        if show_lanes:
            lane_lines = self.detect_lanes(image)
            for line in lane_lines:
                x1, y1, x2, y2 = line
                cv2.line(result_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
        # Draw counting line
        if self.counting_line_y is not None:
            cv2.line(result_image, (0, self.counting_line_y), 
                    (image.shape[1], self.counting_line_y), (0, 255, 255), 2)
            cv2.putText(result_image, "Counting Line", (10, self.counting_line_y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Draw detections and tracking
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            confidence = detection['confidence']
            class_name = detection['class_name']
            tracker_id = detection.get('tracker_id')
            
            # Choose color based on vehicle type
            color_map = {
                'car': (0, 255, 0),
                'motorcycle': (255, 0, 0),
                'bus': (0, 0, 255),
                'truck': (255, 255, 0)
            }
            color = color_map.get(class_name, (0, 255, 0))
            
            # Draw bounding box
            cv2.rectangle(result_image, (x1, y1), (x2, y2), color, 2)
            
            # Draw label with tracker ID
            label = f"{class_name} #{tracker_id}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # Draw label background
            cv2.rectangle(result_image, (x1, y1 - label_size[1] - 10),
                         (x1 + label_size[0], y1), color, -1)
            
            # Draw label text
            cv2.putText(result_image, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            
            # Draw tracking path
            if show_tracking and tracker_id and tracker_id in self.tracker_history:
                history = list(self.tracker_history[tracker_id])
                if len(history) > 1:
                    for i in range(1, len(history)):
                        cv2.line(result_image, history[i-1], history[i], color, 2)
        
        # Draw counting statistics
        y_offset = 30
        for vehicle_type, count in self.vehicle_count.items():
            text = f"{vehicle_type}: {count}"
            cv2.putText(result_image, text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            y_offset += 25
        
        # Draw total count
        total_count = sum(self.vehicle_count.values())
        cv2.putText(result_image, f"Total: {total_count}", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        return result_image
    
    def process_video_advanced(self, video_path: str, output_path: Optional[str] = None,
                              show_video: bool = True, counting_line_y: Optional[int] = None) -> None:
        """
        Process video with advanced features.
        
        Args:
            video_path: Path to input video
            output_path: Path to save output video
            show_video: Whether to display video
            counting_line_y: Y-position for counting line
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Set counting line if provided
        if counting_line_y is None:
            counting_line_y = height // 2
        self.set_counting_zone(counting_line_y)
        
        # Initialize video writer
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        start_time = time.time()
        
        print(f"Processing video with advanced features...")
        print(f"Counting line set at y={counting_line_y}")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect vehicles
            detections = self.detect_vehicles(frame)
            
            # Update tracking
            tracked_detections = self.update_tracking(detections)
            
            # Count vehicles
            self.count_vehicles(tracked_detections)
            
            # Draw advanced visualizations
            result_frame = self.draw_advanced_detections(frame, tracked_detections)
            
            # Add FPS counter
            frame_count += 1
            elapsed_time = time.time() - start_time
            current_fps = frame_count / elapsed_time
            cv2.putText(result_frame, f"FPS: {current_fps:.1f}", 
                       (width - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Write frame
            if writer:
                writer.write(result_frame)
            
            # Show frame
            if show_video:
                cv2.imshow('Advanced Vehicle Detection', result_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        # Cleanup
        cap.release()
        if writer:
            writer.release()
        if show_video:
            cv2.destroyAllWindows()
        
        # Print final statistics
        print(f"\nProcessing completed!")
        print(f"Frames processed: {frame_count}")
        print(f"Total time: {elapsed_time:.2f} seconds")
        print(f"Average FPS: {frame_count/elapsed_time:.1f}")
        print(f"Vehicle counts: {dict(self.vehicle_count)}")