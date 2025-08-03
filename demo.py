#!/usr/bin/env python3
"""
Demo script for vehicle detection system.
Provides interactive examples and showcases different features.
"""

import cv2
import numpy as np
import time
from vehicle_detector import VehicleDetector
from advanced_detector import AdvancedVehicleDetector

def create_demo_scene():
    """Create a realistic traffic scene for demonstration."""
    # Create a larger, more realistic scene
    scene = np.zeros((720, 1280, 3), dtype=np.uint8)
    
    # Sky gradient
    for y in range(300):
        intensity = int(200 - (y / 300) * 100)
        scene[y, :] = (intensity, intensity, intensity + 50)
    
    # Road
    scene[300:, :] = (40, 40, 40)
    
    # Lane markings
    for y in range(350, 720, 80):
        cv2.line(scene, (0, y), (1280, y), (255, 255, 255), 4)
    
    # Sidewalk
    cv2.rectangle(scene, (0, 280), (1280, 300), (100, 100, 100), -1)
    
    # Buildings in background
    buildings = [
        (50, 50, 200, 280, (80, 80, 80)),
        (250, 80, 350, 280, (70, 70, 70)),
        (400, 60, 500, 280, (90, 90, 90)),
        (550, 100, 650, 280, (75, 75, 75)),
        (700, 40, 800, 280, (85, 85, 85)),
        (850, 70, 950, 280, (65, 65, 65)),
        (1000, 90, 1100, 280, (95, 95, 95)),
        (1150, 30, 1250, 280, (60, 60, 60))
    ]
    
    for x1, y1, x2, y2, color in buildings:
        cv2.rectangle(scene, (x1, y1), (x2, y2), color, -1)
        # Add windows
        for wx in range(x1 + 20, x2 - 20, 40):
            for wy in range(y1 + 20, y2 - 20, 40):
                cv2.rectangle(scene, (wx, wy), (wx + 20, wy + 20), (255, 255, 200), -1)
    
    # Vehicles with more realistic shapes
    vehicles = [
        # Cars
        ((200, 400), (350, 500), (255, 0, 0)),      # Red car
        ((500, 380), (650, 480), (0, 255, 0)),      # Green car
        ((800, 420), (950, 520), (0, 0, 255)),      # Blue car
        ((1100, 400), (1250, 500), (255, 255, 0)),  # Yellow car
        
        # Trucks
        ((100, 520), (300, 620), (128, 0, 128)),    # Purple truck
        ((600, 540), (800, 640), (0, 255, 255)),    # Cyan truck
        
        # Motorcycles
        ((400, 480), (450, 520), (255, 165, 0)),    # Orange motorcycle
        ((900, 500), (950, 540), (255, 192, 203)),  # Pink motorcycle
    ]
    
    for (x1, y1), (x2, y2), color in vehicles:
        # Main body
        cv2.rectangle(scene, (x1, y1), (x2, y2), color, -1)
        
        # Windows (for cars and trucks)
        if y2 - y1 > 80:  # Larger vehicles
            window_y1 = y1 + 20
            window_y2 = y2 - 30
            window_x1 = x1 + 30
            window_x2 = x2 - 30
            cv2.rectangle(scene, (window_x1, window_y1), (window_x2, window_y2), (200, 200, 255), -1)
        
        # Wheels
        wheel_radius = 15
        cv2.circle(scene, (x1 + 30, y2), wheel_radius, (20, 20, 20), -1)
        cv2.circle(scene, (x2 - 30, y2), wheel_radius, (20, 20, 20), -1)
    
    # Add some pedestrians
    pedestrians = [
        (150, 250, (255, 200, 200)),
        (450, 260, (200, 255, 200)),
        (750, 245, (200, 200, 255)),
        (1050, 255, (255, 255, 200))
    ]
    
    for x, y, color in pedestrians:
        # Head
        cv2.circle(scene, (x, y), 8, color, -1)
        # Body
        cv2.rectangle(scene, (x-5, y+8), (x+5, y+25), color, -1)
        # Arms
        cv2.line(scene, (x-5, y+12), (x-15, y+20), color, 3)
        cv2.line(scene, (x+5, y+12), (x+15, y+20), color, 3)
        # Legs
        cv2.line(scene, (x-3, y+25), (x-8, y+35), color, 3)
        cv2.line(scene, (x+3, y+25), (x+8, y+35), color, 3)
    
    return scene

def demo_basic_detection():
    """Demonstrate basic vehicle detection."""
    print("\n🚗 Basic Vehicle Detection Demo")
    print("=" * 40)
    
    # Create detector
    detector = VehicleDetector(confidence_threshold=0.4)
    
    # Create demo scene
    scene = create_demo_scene()
    cv2.imwrite("demo_scene.jpg", scene)
    print("✓ Created demo traffic scene")
    
    # Detect vehicles
    print("Detecting vehicles...")
    start_time = time.time()
    detections = detector.detect_vehicles(scene)
    detection_time = time.time() - start_time
    
    print(f"✓ Detection completed in {detection_time:.3f} seconds")
    print(f"✓ Found {len(detections)} vehicles")
    
    # Show detections
    result = detector.draw_detections(scene, detections)
    cv2.imwrite("demo_basic_result.jpg", result)
    
    # Display statistics
    stats = detector.get_detection_stats(detections)
    print(f"✓ Detection statistics: {stats}")
    
    # Show result
    cv2.imshow('Basic Vehicle Detection Demo', result)
    print("Press any key to continue...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def demo_advanced_features():
    """Demonstrate advanced features."""
    print("\n🚀 Advanced Features Demo")
    print("=" * 40)
    
    # Create advanced detector
    detector = AdvancedVehicleDetector(confidence_threshold=0.4)
    
    # Create demo scene
    scene = create_demo_scene()
    
    # Set counting line
    detector.set_counting_zone(400)
    
    # Detect and track
    print("Detecting and tracking vehicles...")
    detections = detector.detect_vehicles(scene)
    tracked_detections = detector.update_tracking(detections)
    
    print(f"✓ Tracked {len(tracked_detections)} vehicles")
    
    # Detect lanes
    lane_lines = detector.detect_lanes(scene)
    print(f"✓ Detected {len(lane_lines)} lane lines")
    
    # Draw advanced visualizations
    result = detector.draw_advanced_detections(scene, tracked_detections)
    cv2.imwrite("demo_advanced_result.jpg", result)
    
    # Show result
    cv2.imshow('Advanced Vehicle Detection Demo', result)
    print("Press any key to continue...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def demo_webcam():
    """Demonstrate webcam detection."""
    print("\n📹 Webcam Demo")
    print("=" * 40)
    print("This will open your webcam for real-time vehicle detection.")
    print("Press 'q' to quit, 's' to save a frame")
    
    try:
        detector = VehicleDetector(confidence_threshold=0.5)
        detector.detect_from_webcam()
    except Exception as e:
        print(f"Webcam not available: {e}")
        print("You can still use the system with image or video files.")

def demo_performance_comparison():
    """Compare performance of different models."""
    print("\n⚡ Performance Comparison Demo")
    print("=" * 40)
    
    scene = create_demo_scene()
    models = ['yolov8n.pt', 'yolov8s.pt']
    
    for model in models:
        try:
            print(f"\nTesting {model}...")
            detector = VehicleDetector(model_path=model, confidence_threshold=0.5)
            
            # Warm up
            detector.detect_vehicles(scene)
            
            # Performance test
            times = []
            for _ in range(5):
                start_time = time.time()
                detections = detector.detect_vehicles(scene)
                detection_time = time.time() - start_time
                times.append(detection_time)
            
            avg_time = np.mean(times)
            fps = 1.0 / avg_time
            
            print(f"✓ {model}: {avg_time:.3f}s per frame ({fps:.1f} FPS)")
            print(f"  Detected {len(detections)} vehicles")
            
        except Exception as e:
            print(f"✗ {model}: Error - {e}")

def interactive_menu():
    """Show interactive menu."""
    while True:
        print("\n" + "=" * 50)
        print("🚗 Vehicle Detection System - Interactive Demo")
        print("=" * 50)
        print("1. Basic Vehicle Detection")
        print("2. Advanced Features (Tracking & Counting)")
        print("3. Webcam Detection")
        print("4. Performance Comparison")
        print("5. Run All Demos")
        print("6. Exit")
        print("-" * 50)
        
        choice = input("Select an option (1-6): ").strip()
        
        if choice == '1':
            demo_basic_detection()
        elif choice == '2':
            demo_advanced_features()
        elif choice == '3':
            demo_webcam()
        elif choice == '4':
            demo_performance_comparison()
        elif choice == '5':
            demo_basic_detection()
            demo_advanced_features()
            demo_performance_comparison()
            print("\n🎉 All demos completed!")
        elif choice == '6':
            print("Goodbye! 👋")
            break
        else:
            print("Invalid choice. Please select 1-6.")

def main():
    """Main demo function."""
    print("🚗 Vehicle Detection System Demo")
    print("Welcome to the interactive vehicle detection demonstration!")
    
    # Check if user wants interactive mode
    if len(input("Press Enter for interactive menu, or type 'auto' for automatic demo: ").strip()) == 0:
        interactive_menu()
    else:
        # Run automatic demo
        print("\nRunning automatic demo...")
        demo_basic_detection()
        demo_advanced_features()
        demo_performance_comparison()
        print("\n🎉 Demo completed! Check the generated images for results.")

if __name__ == "__main__":
    main()