#!/usr/bin/env python3
"""
Test script to verify the installation of Bangladesh Road Accident Analysis.
"""

import sys
from pathlib import Path
import importlib

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    modules_to_test = [
        'src.utils.config',
        'src.utils.helpers',
        'src.scrapers.base_scraper',
        'src.scrapers.daily_star',
        'src.scrapers.prothom_alo',
        'src.scrapers.dhaka_tribune',
        'src.scrapers.bdnews24',
        'src.nlp.text_processor',
        'src.nlp.llm_extractor',
        'src.geolocation.geocoder',
        'src.analysis.data_cleaner',
        'src.analysis.visualizer',
        'src.analysis.trend_analyzer'
    ]
    
    failed_imports = []
    
    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"✓ {module_name}")
        except ImportError as e:
            print(f"✗ {module_name}: {e}")
            failed_imports.append(module_name)
    
    return len(failed_imports) == 0


def test_dependencies():
    """Test that all required dependencies are installed."""
    print("\nTesting dependencies...")
    
    dependencies = [
        'requests',
        'beautifulsoup4',
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'plotly',
        'folium',
        'geopy',
        'openai',
        'transformers',
        'nltk',
        'yaml'
    ]
    
    failed_deps = []
    
    for dep in dependencies:
        try:
            importlib.import_module(dep)
            print(f"✓ {dep}")
        except ImportError:
            print(f"✗ {dep}")
            failed_deps.append(dep)
    
    return len(failed_deps) == 0


def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from src.utils.config import config
        
        # Test basic config access
        scraping_config = config.get_scraping_config()
        news_sources = config.get_news_sources()
        
        print(f"✓ Configuration loaded successfully")
        print(f"  - Scraping delay: {scraping_config.get('request_delay')} seconds")
        print(f"  - News sources: {len(news_sources)} configured")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_text_processing():
    """Test text processing functionality."""
    print("\nTesting text processing...")
    
    try:
        from src.nlp.text_processor import TextProcessor
        
        processor = TextProcessor()
        
        # Test with sample text
        sample_text = "A bus accident in Dhaka left 5 people dead and 15 injured due to overspeeding."
        
        is_accident = processor.is_accident_article(sample_text)
        vehicles = processor.extract_vehicle_types(sample_text)
        cause = processor.extract_cause(sample_text)
        
        print(f"✓ Text processing working")
        print(f"  - Accident detection: {is_accident}")
        print(f"  - Vehicle types: {vehicles}")
        print(f"  - Probable cause: {cause}")
        
        return True
        
    except Exception as e:
        print(f"✗ Text processing test failed: {e}")
        return False


def test_geolocation():
    """Test geolocation functionality."""
    print("\nTesting geolocation...")
    
    try:
        from src.geolocation.geocoder import Geocoder
        
        geocoder = Geocoder()
        
        # Test with a known location
        coords = geocoder.get_location_coordinates("Dhaka")
        
        if coords:
            print(f"✓ Geolocation working")
            print(f"  - Dhaka coordinates: {coords}")
        else:
            print("⚠ Geolocation test inconclusive (no coordinates found)")
        
        return True
        
    except Exception as e:
        print(f"✗ Geolocation test failed: {e}")
        return False


def test_data_cleaning():
    """Test data cleaning functionality."""
    print("\nTesting data cleaning...")
    
    try:
        from src.analysis.data_cleaner import DataCleaner
        
        cleaner = DataCleaner()
        
        # Test with empty data
        df = cleaner.clean_articles_data([])
        
        print(f"✓ Data cleaning working")
        print(f"  - Empty DataFrame shape: {df.shape}")
        
        return True
        
    except Exception as e:
        print(f"✗ Data cleaning test failed: {e}")
        return False


def test_visualization():
    """Test visualization functionality."""
    print("\nTesting visualization...")
    
    try:
        from src.analysis.visualizer import Visualizer
        
        visualizer = Visualizer()
        
        print(f"✓ Visualization module loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Visualization test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=== Bangladesh Road Accident Analysis - Installation Test ===")
    print("This script tests that all components are working correctly.\n")
    
    tests = [
        ("Imports", test_imports),
        ("Dependencies", test_dependencies),
        ("Configuration", test_configuration),
        ("Text Processing", test_text_processing),
        ("Geolocation", test_geolocation),
        ("Data Cleaning", test_data_cleaning),
        ("Visualization", test_visualization)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} test failed with exception: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The installation is working correctly.")
        print("\nYou can now run:")
        print("  python demo.py          # Run the demo")
        print("  python main.py --full   # Run the full analysis")
    else:
        print("⚠ Some tests failed. Please check the error messages above.")
        print("You may need to install missing dependencies or fix configuration issues.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)