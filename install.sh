#!/bin/bash

# Bangladesh Road Accident Analysis - Installation Script

echo "=== Bangladesh Road Accident Analysis Installation ==="
echo "This script will set up the environment and install dependencies."

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✓ Python $python_version is installed (>= $required_version)"
else
    echo "✗ Python 3.8+ is required. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Download NLTK data
echo "Downloading NLTK data..."
python3 -c "
import nltk
try:
    nltk.download('punkt')
    nltk.download('stopwords')
    print('✓ NLTK data downloaded successfully')
except Exception as e:
    print(f'⚠ Warning: Could not download NLTK data: {e}')
"

# Create necessary directories
echo "Creating directories..."
mkdir -p data/raw data/processed data/results/visualizations logs

# Set up logging
echo "Setting up logging..."
touch logs/accident_analysis.log

# Make scripts executable
chmod +x main.py
chmod +x demo.py

echo ""
echo "=== Installation Completed Successfully ==="
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run the demo:"
echo "  python demo.py"
echo ""
echo "To run the full analysis:"
echo "  python main.py --full"
echo ""
echo "Optional: Set up API keys for enhanced features:"
echo "  export OPENAI_API_KEY='your_openai_api_key'"
echo "  export GOOGLE_MAPS_API_KEY='your_google_maps_api_key'"
echo ""
echo "For more information, see README.md"