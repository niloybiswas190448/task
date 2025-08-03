#!/bin/bash

# Vehicle Detection System Installation Script

echo "🚗 Vehicle Detection System - Installation"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "✓ pip3 found"

# Create virtual environment (optional)
read -p "Do you want to create a virtual environment? (y/n): " create_venv
if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ Virtual environment created and activated"
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Test installation
echo "Testing installation..."
python3 test_detector.py

if [ $? -eq 0 ]; then
    echo "✓ Installation test passed"
else
    echo "⚠️  Installation test had issues, but system may still work"
fi

echo ""
echo "🎉 Installation completed!"
echo ""
echo "Usage examples:"
echo "  python3 main.py                    # Run examples"
echo "  python3 demo.py                    # Interactive demo"
echo "  python3 main.py --mode webcam      # Use webcam"
echo "  python3 main.py --mode image --input image.jpg --output result.jpg"
echo ""
echo "For more information, see README.md"