#!/usr/bin/env python3
"""
Main script for vehicle detection system.
Provides command-line interface and examples for using the VehicleDetector class.
"""

import argparse
import os
import sys
from vehicle_detector import VehicleDetector
import cv2
import numpy as np

def main():
    parser = argparse.ArgumentParser(description='Vehicle Detection System')
    parser.add_argument('--mode', choices=['image', 'video', 'webcam'], 
                       required=True, help='Detection mode')
    parser.add_argument('--input', type=str, help='Input file path (for image/video mode)')
    parser.add_argument('--output', type=str, help='Output file path (optional)')
    parser.add_argument('--confidence', type=float, default=0.5, 
                       help='Confidence threshold (default: 0.5)')
    parser.add_argument('--model', type=str, default='yolov8n.pt', 
                       help='YOLO model path (default: yolov8n.pt)')
    parser.add_argument('--camera', type=int, default=0, 
                       help='Camera ID for webcam mode (default: 0)')
    parser.add_argument('--no-display', action='store_true', 
                       help='Disable video display (for video mode)')
    
    args = parser.parse_args()
    
    # Initialize vehicle detector
    print("Initializing vehicle detector...")
    detector = VehicleDetector(model_path=args.model, confidence_threshold=args.confidence)
    
    try:
        if args.mode == 'image':
            if not args.input:
                print("Error: Input image path required for image mode")
                sys.exit(1)
            
            if not os.path.exists(args.input):
                print(f"Error: Input file not found: {args.input}")
                sys.exit(1)
            
            print(f"Processing image: {args.input}")
            result_image = detector.detect_from_image(args.input, args.output)
            
            # Display result
            cv2.imshow('Vehicle Detection Result', result_image)
            print("Press any key to close...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        elif args.mode == 'video':
            if not args.input:
                print("Error: Input video path required for video mode")
                sys.exit(1)
            
            if not os.path.exists(args.input):
                print(f"Error: Input file not found: {args.input}")
                sys.exit(1)
            
            print(f"Processing video: {args.input}")
            detector.detect_from_video(args.input, args.output, not args.no_display)
            
        elif args.mode == 'webcam':
            print(f"Starting webcam detection (camera ID: {args.camera})")
            detector.detect_from_webcam(args.camera, args.output)
            
    except KeyboardInterrupt:
        print("\nDetection stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def run_examples():
    """Run example demonstrations of the vehicle detection system."""
    print("=== Vehicle Detection Examples ===\n")
    
    # Initialize detector
    detector = VehicleDetector(confidence_threshold=0.5)
    
    # Example 1: Create a sample image with vehicles (if no input provided)
    print("Example 1: Creating a sample image for demonstration...")
    
    # Create a simple test image with colored rectangles representing vehicles
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Add some "vehicles" (colored rectangles)
    cv2.rectangle(test_image, (100, 200), (200, 300), (255, 0, 0), -1)  # Blue car
    cv2.rectangle(test_image, (300, 150), (400, 250), (0, 255, 0), -1)  # Green car
    cv2.rectangle(test_image, (500, 250), (600, 350), (0, 0, 255), -1)  # Red car
    
    # Add some text to make it look more realistic
    cv2.putText(test_image, "Sample Traffic Scene", (50, 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Save test image
    cv2.imwrite("sample_traffic.jpg", test_image)
    print("Sample image created: sample_traffic.jpg")
    
    # Example 2: Process the sample image
    print("\nExample 2: Processing sample image...")
    try:
        result = detector.detect_from_image("sample_traffic.jpg", "result_sample.jpg")
        print("Sample image processed successfully!")
        
        # Show statistics
        detections = detector.detect_vehicles(cv2.imread("sample_traffic.jpg"))
        stats = detector.get_detection_stats(detections)
        print(f"Detection statistics: {stats}")
        
    except Exception as e:
        print(f"Note: YOLO model may not detect simple rectangles as vehicles: {e}")
    
    # Example 3: Webcam demonstration
    print("\nExample 3: Webcam demonstration")
    print("This will open your webcam for real-time vehicle detection.")
    print("Press 'q' to quit, 's' to save a frame")
    
    try:
        detector.detect_from_webcam()
    except Exception as e:
        print(f"Webcam not available or error occurred: {e}")
        print("You can still use the system with image or video files.")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, run examples
        run_examples()
    else:
        # Run with command line arguments
        main()