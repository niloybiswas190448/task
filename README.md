# Vehicle Detection System

A comprehensive vehicle detection system built with Python, OpenCV, and YOLO (You Only Look Once). This system can detect vehicles in images, videos, and real-time webcam feeds with advanced features like tracking, counting, and lane detection.

## Features

### Basic Vehicle Detection
- **Multi-class detection**: Cars, motorcycles, buses, and trucks
- **Real-time processing**: Fast detection using YOLOv8
- **Confidence thresholding**: Adjustable detection sensitivity
- **Multiple input sources**: Images, videos, and webcam feeds

### Advanced Features
- **Vehicle tracking**: Track individual vehicles across frames
- **Vehicle counting**: Count vehicles crossing designated lines
- **Lane detection**: Detect lane markings in traffic scenes
- **Speed estimation**: Estimate vehicle speeds based on tracking data
- **Visualization**: Rich visual output with bounding boxes, labels, and statistics

## Installation

### Prerequisites
- Python 3.8 or higher
- CUDA-compatible GPU (optional, for faster processing)

### Install Dependencies

1. Clone or download this repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

The system will automatically download the YOLOv8 model on first run.

## Usage

### Command Line Interface

#### Basic Usage

```bash
# Process an image
python main.py --mode image --input path/to/image.jpg --output result.jpg

# Process a video
python main.py --mode video --input path/to/video.mp4 --output result.mp4

# Use webcam
python main.py --mode webcam
```

#### Advanced Options

```bash
# Adjust confidence threshold
python main.py --mode image --input image.jpg --confidence 0.7

# Use different YOLO model
python main.py --mode video --input video.mp4 --model yolov8s.pt

# Process video without display
python main.py --mode video --input video.mp4 --no-display

# Use specific camera
python main.py --mode webcam --camera 1
```

### Python API

#### Basic Vehicle Detection

```python
from vehicle_detector import VehicleDetector

# Initialize detector
detector = VehicleDetector(confidence_threshold=0.5)

# Detect vehicles in image
detections = detector.detect_vehicles(image)
result_image = detector.draw_detections(image, detections)

# Process image file
result = detector.detect_from_image("input.jpg", "output.jpg")

# Process video
detector.detect_from_video("input.mp4", "output.mp4")

# Use webcam
detector.detect_from_webcam()
```

#### Advanced Vehicle Detection

```python
from advanced_detector import AdvancedVehicleDetector

# Initialize advanced detector
detector = AdvancedVehicleDetector(confidence_threshold=0.5)

# Process video with tracking and counting
detector.process_video_advanced(
    video_path="traffic.mp4",
    output_path="result.mp4",
    counting_line_y=300  # Set counting line at y=300
)
```

### Interactive Examples

Run the examples without arguments:

```bash
python main.py
```

This will:
1. Create a sample traffic image
2. Process it with vehicle detection
3. Start webcam detection (if available)

## File Structure

```
vehicle-detection/
├── vehicle_detector.py      # Basic vehicle detection class
├── advanced_detector.py     # Advanced features (tracking, counting)
├── main.py                  # Command-line interface and examples
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Configuration

### Model Options
- `yolov8n.pt`: Nano model (fastest, least accurate)
- `yolov8s.pt`: Small model (balanced)
- `yolov8m.pt`: Medium model (more accurate)
- `yolov8l.pt`: Large model (very accurate)
- `yolov8x.pt`: Extra large model (most accurate)

### Confidence Threshold
- Range: 0.0 to 1.0
- Default: 0.5
- Higher values = fewer detections but higher confidence
- Lower values = more detections but may include false positives

## Performance

### Speed vs Accuracy Trade-offs

| Model | Speed | Accuracy | Memory Usage |
|-------|-------|----------|--------------|
| YOLOv8n | Fastest | Good | Low |
| YOLOv8s | Fast | Better | Medium |
| YOLOv8m | Medium | Best | High |
| YOLOv8l | Slow | Excellent | Very High |
| YOLOv8x | Slowest | Outstanding | Highest |

### Hardware Recommendations

- **CPU-only**: Use YOLOv8n or YOLOv8s
- **GPU (CUDA)**: Can use larger models for better accuracy
- **Real-time applications**: Use YOLOv8n with confidence threshold 0.6+

## Examples

### Basic Image Detection
```python
from vehicle_detector import VehicleDetector

detector = VehicleDetector()
result = detector.detect_from_image("traffic.jpg", "result.jpg")
print(f"Detection completed!")
```

### Video Processing with Statistics
```python
from vehicle_detector import VehicleDetector

detector = VehicleDetector(confidence_threshold=0.6)
detector.detect_from_video("traffic.mp4", "output.mp4", show_video=True)
```

### Advanced Tracking and Counting
```python
from advanced_detector import AdvancedVehicleDetector

detector = AdvancedVehicleDetector()
detector.process_video_advanced(
    video_path="highway.mp4",
    output_path="tracked.mp4",
    counting_line_y=400,
    show_video=True
)
```

## Troubleshooting

### Common Issues

1. **Model download fails**
   - Check internet connection
   - Try downloading manually from Ultralytics

2. **CUDA errors**
   - Install CPU-only PyTorch: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu`

3. **Webcam not working**
   - Check camera permissions
   - Try different camera ID: `--camera 1`

4. **Low FPS**
   - Use smaller model (YOLOv8n)
   - Increase confidence threshold
   - Reduce input resolution

### Performance Tips

- Use GPU acceleration when available
- Process videos without display for faster processing
- Adjust confidence threshold based on your needs
- Use appropriate model size for your use case

## Contributing

Feel free to contribute to this project by:
- Reporting bugs
- Suggesting new features
- Improving documentation
- Adding new detection models

## License

This project is open source and available under the MIT License.

## Acknowledgments

- [Ultralytics](https://github.com/ultralytics/ultralytics) for YOLOv8
- [OpenCV](https://opencv.org/) for computer vision capabilities
- [PyTorch](https://pytorch.org/) for deep learning framework