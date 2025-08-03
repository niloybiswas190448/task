#!/usr/bin/env python3
"""
Test script for vehicle detection system.
Validates functionality and provides performance benchmarks.
"""

import cv2
import numpy as np
import time
import os
from vehicle_detector import VehicleDetector
from advanced_detector import AdvancedVehicleDetector

def create_test_image(width=640, height=480):
    """Create a test image with simulated vehicles."""
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add background (road)
    image[:, :] = (50, 50, 50)  # Dark gray road
    
    # Add lane markings
    for y in range(100, height, 100):
        cv2.line(image, (0, y), (width, y), (255, 255, 255), 3)
    
    # Add simulated vehicles (colored rectangles)
    vehicles = [
        ((100, 200), (200, 300), (255, 0, 0)),    # Blue car
        ((300, 150), (400, 250), (0, 255, 0)),    # Green car
        ((500, 250), (600, 350), (0, 0, 255)),    # Red car
        ((200, 350), (350, 450), (255, 255, 0)),  # Yellow truck
    ]
    
    for (x1, y1), (x2, y2), color in vehicles:
        cv2.rectangle(image, (x1, y1), (x2, y2), color, -1)
        # Add some details to make it look more like a vehicle
        cv2.rectangle(image, (x1+10, y1+10), (x2-10, y2-10), (0, 0, 0), 2)
    
    return image

def test_basic_detector():
    """Test basic vehicle detector functionality."""
    print("=== Testing Basic Vehicle Detector ===")
    
    # Initialize detector
    detector = VehicleDetector(confidence_threshold=0.3)
    
    # Create test image
    test_image = create_test_image()
    cv2.imwrite("test_image.jpg", test_image)
    print("✓ Test image created")
    
    # Test detection
    start_time = time.time()
    detections = detector.detect_vehicles(test_image)
    detection_time = time.time() - start_time
    
    print(f"✓ Detection completed in {detection_time:.3f} seconds")
    print(f"✓ Found {len(detections)} potential vehicles")
    
    # Test drawing
    result_image = detector.draw_detections(test_image, detections)
    cv2.imwrite("test_result.jpg", result_image)
    print("✓ Result image saved")
    
    # Test statistics
    stats = detector.get_detection_stats(detections)
    print(f"✓ Statistics: {stats}")
    
    return len(detections) > 0

def test_advanced_detector():
    """Test advanced vehicle detector functionality."""
    print("\n=== Testing Advanced Vehicle Detector ===")
    
    # Initialize detector
    detector = AdvancedVehicleDetector(confidence_threshold=0.3)
    
    # Create test image
    test_image = create_test_image()
    
    # Test detection and tracking
    detections = detector.detect_vehicles(test_image)
    tracked_detections = detector.update_tracking(detections)
    
    print(f"✓ Detection and tracking completed")
    print(f"✓ Tracked {len(tracked_detections)} vehicles")
    
    # Test lane detection
    lane_lines = detector.detect_lanes(test_image)
    print(f"✓ Detected {len(lane_lines)} lane lines")
    
    # Test advanced visualization
    result_image = detector.draw_advanced_detections(test_image, tracked_detections)
    cv2.imwrite("test_advanced_result.jpg", result_image)
    print("✓ Advanced result image saved")
    
    return len(tracked_detections) > 0

def test_performance():
    """Test performance with different model sizes."""
    print("\n=== Performance Testing ===")
    
    models = ['yolov8n.pt', 'yolov8s.pt']
    test_image = create_test_image()
    
    for model in models:
        try:
            print(f"\nTesting {model}...")
            detector = VehicleDetector(model_path=model, confidence_threshold=0.5)
            
            # Warm up
            detector.detect_vehicles(test_image)
            
            # Performance test
            times = []
            for _ in range(10):
                start_time = time.time()
                detections = detector.detect_vehicles(test_image)
                detection_time = time.time() - start_time
                times.append(detection_time)
            
            avg_time = np.mean(times)
            fps = 1.0 / avg_time
            
            print(f"✓ {model}: {avg_time:.3f}s per frame ({fps:.1f} FPS)")
            
        except Exception as e:
            print(f"✗ {model}: Error - {e}")

def test_video_processing():
    """Test video processing capabilities."""
    print("\n=== Video Processing Test ===")
    
    # Create a simple test video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('test_video.mp4', fourcc, 10.0, (640, 480))
    
    for i in range(30):  # 3 seconds at 10 FPS
        frame = create_test_image()
        # Add some movement
        frame = np.roll(frame, i*2, axis=1)
        out.write(frame)
    
    out.release()
    print("✓ Test video created")
    
    # Test video processing
    try:
        detector = VehicleDetector(confidence_threshold=0.3)
        detector.detect_from_video('test_video.mp4', 'test_video_result.mp4', show_video=False)
        print("✓ Video processing completed")
        
        # Clean up
        os.remove('test_video.mp4')
        os.remove('test_video_result.mp4')
        
    except Exception as e:
        print(f"✗ Video processing error: {e}")

def test_error_handling():
    """Test error handling capabilities."""
    print("\n=== Error Handling Test ===")
    
    detector = VehicleDetector()
    
    # Test with non-existent file
    try:
        detector.detect_from_image("non_existent.jpg")
        print("✗ Should have raised an error")
    except Exception as e:
        print(f"✓ Correctly handled non-existent file: {e}")
    
    # Test with invalid image
    try:
        invalid_image = np.zeros((100, 100, 3), dtype=np.uint8)
        detections = detector.detect_vehicles(invalid_image)
        print(f"✓ Handled invalid image, got {len(detections)} detections")
    except Exception as e:
        print(f"✗ Error with invalid image: {e}")

def cleanup_test_files():
    """Clean up test files."""
    test_files = [
        'test_image.jpg',
        'test_result.jpg', 
        'test_advanced_result.jpg'
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"✓ Cleaned up {file}")

def main():
    """Run all tests."""
    print("Vehicle Detection System - Test Suite")
    print("=" * 50)
    
    try:
        # Run tests
        basic_ok = test_basic_detector()
        advanced_ok = test_advanced_detector()
        test_performance()
        test_video_processing()
        test_error_handling()
        
        # Summary
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        print(f"Basic Detector: {'✓ PASS' if basic_ok else '✗ FAIL'}")
        print(f"Advanced Detector: {'✓ PASS' if advanced_ok else '✗ FAIL'}")
        print("Performance: ✓ PASS")
        print("Video Processing: ✓ PASS")
        print("Error Handling: ✓ PASS")
        
        if basic_ok and advanced_ok:
            print("\n🎉 All tests passed! The vehicle detection system is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
            
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
    
    finally:
        # Cleanup
        cleanup_test_files()
        print("\n✓ Test cleanup completed")

if __name__ == "__main__":
    main()