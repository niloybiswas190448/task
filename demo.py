#!/usr/bin/env python3
"""
Demo script for Bangladesh Road Accident Analysis.
This script demonstrates the key features of the accident analysis system.
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, date
import json

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.config import config
from src.utils.helpers import setup_logging
from src.nlp.text_processor import TextProcessor
from src.nlp.llm_extractor import LLMExtractor
from src.geolocation.geocoder import Geocoder
from src.analysis.data_cleaner import DataCleaner
from src.analysis.visualizer import Visualizer
from src.analysis.trend_analyzer import TrendAnalyzer


def create_sample_data():
    """Create sample accident data for demonstration."""
    sample_articles = [
        {
            'id': 'sample_001',
            'source': 'The Daily Star',
            'url': 'https://example.com/accident1',
            'title': 'Bus accident in Dhaka leaves 5 dead, 15 injured',
            'content': 'A passenger bus collided with a truck on Dhaka-Chittagong highway yesterday, resulting in 5 deaths and 15 injuries. The accident occurred due to overspeeding and poor visibility caused by fog. The bus was carrying 40 passengers when it crashed into the truck near Narayanganj.',
            'date': date(2024, 1, 15),
            'scraped_at': datetime.now().isoformat()
        },
        {
            'id': 'sample_002',
            'source': 'Prothom Alo',
            'url': 'https://example.com/accident2',
            'title': 'সড়ক দুর্ঘটনায় ৩ জন নিহত, ৮ জন আহত',
            'content': 'চট্টগ্রামে একটি মোটরসাইকেল দুর্ঘটনায় ৩ জন নিহত এবং ৮ জন আহত হয়েছেন। দুর্ঘটনাটি রাত ১১টায় ঘটে। চালকের অসাবধানতার কারণে দুর্ঘটনাটি ঘটেছে বলে জানা গেছে।',
            'date': date(2024, 1, 20),
            'scraped_at': datetime.now().isoformat()
        },
        {
            'id': 'sample_003',
            'source': 'Dhaka Tribune',
            'url': 'https://example.com/accident3',
            'title': 'Truck overturns in Sylhet, 2 killed',
            'content': 'A truck carrying construction materials overturned in Sylhet district, killing 2 people and injuring 3 others. The accident was caused by mechanical failure of the truck brakes. The incident occurred on the Sylhet-Sunamganj road.',
            'date': date(2024, 2, 5),
            'scraped_at': datetime.now().isoformat()
        },
        {
            'id': 'sample_004',
            'source': 'BDNews24',
            'url': 'https://example.com/accident4',
            'title': 'Rickshaw accident in Rajshahi claims 1 life',
            'content': 'A rickshaw was hit by a speeding car in Rajshahi city, resulting in the death of one passenger and injuries to two others. The accident occurred due to driver negligence and poor road conditions.',
            'date': date(2024, 2, 10),
            'scraped_at': datetime.now().isoformat()
        },
        {
            'id': 'sample_005',
            'source': 'The Daily Star',
            'url': 'https://example.com/accident5',
            'title': 'Multiple vehicle collision in Khulna',
            'content': 'A major accident involving three vehicles occurred in Khulna city, leaving 4 dead and 12 injured. The collision involved a bus, a car, and a motorcycle. Poor weather conditions and driver error were cited as causes.',
            'date': date(2024, 2, 15),
            'scraped_at': datetime.now().isoformat()
        }
    ]
    
    return sample_articles


def demo_text_processing():
    """Demonstrate text processing capabilities."""
    print("\n=== Text Processing Demo ===")
    
    text_processor = TextProcessor()
    
    # Sample text
    sample_text = "A bus accident in Dhaka yesterday left 5 people dead and 15 injured due to overspeeding and fog."
    
    print(f"Sample text: {sample_text}")
    print(f"Is accident article: {text_processor.is_accident_article(sample_text)}")
    print(f"Vehicle types: {text_processor.extract_vehicle_types(sample_text)}")
    print(f"Probable cause: {text_processor.extract_cause(sample_text)}")
    print(f"Severity: {text_processor.extract_severity(sample_text)}")
    print(f"Area type: {text_processor.extract_area_type(sample_text)}")
    print(f"Deaths and injuries: {text_processor.extract_deaths_and_injuries(sample_text)}")
    print(f"Location: {text_processor.extract_location(sample_text)}")


def demo_llm_extraction():
    """Demonstrate LLM extraction capabilities."""
    print("\n=== LLM Extraction Demo ===")
    
    llm_extractor = LLMExtractor()
    
    if llm_extractor.is_available():
        print("LLM extraction is available")
        stats = llm_extractor.get_stats()
        print(f"LLM stats: {stats}")
    else:
        print("LLM extraction is not available (no API key configured)")
        print("This is normal for demo purposes")


def demo_geolocation():
    """Demonstrate geolocation capabilities."""
    print("\n=== Geolocation Demo ===")
    
    geocoder = Geocoder()
    
    # Test locations
    test_locations = ['Dhaka', 'Chittagong', 'Sylhet', 'Rajshahi']
    
    for location in test_locations:
        coords = geocoder.get_location_coordinates(location)
        if coords:
            print(f"{location}: {coords}")
        else:
            print(f"{location}: Not found")


def demo_data_cleaning():
    """Demonstrate data cleaning capabilities."""
    print("\n=== Data Cleaning Demo ===")
    
    # Create sample data
    sample_articles = create_sample_data()
    
    # Process with text processor
    text_processor = TextProcessor()
    processed_articles = []
    
    for article in sample_articles:
        processed_article = text_processor.process_article(article)
        processed_articles.append(processed_article)
    
    # Add geolocation
    geocoder = Geocoder()
    articles_with_geo = geocoder.add_coordinates_to_articles(processed_articles)
    
    # Clean data
    data_cleaner = DataCleaner()
    df = data_cleaner.clean_articles_data(articles_with_geo)
    
    print(f"Cleaned data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Get cleaning stats
    stats = data_cleaner.get_cleaning_stats(df)
    print(f"Cleaning statistics: {json.dumps(stats, indent=2, default=str)}")
    
    return df


def demo_analysis(df):
    """Demonstrate analysis capabilities."""
    print("\n=== Analysis Demo ===")
    
    if df.empty:
        print("No data to analyze")
        return
    
    trend_analyzer = TrendAnalyzer()
    
    # Analyze trends
    trend_results = trend_analyzer.analyze_trends(df)
    print(f"Trend analysis results: {json.dumps(trend_results, indent=2, default=str)}")
    
    # Analyze hotspots
    hotspot_results = trend_analyzer.analyze_hotspots(df)
    print(f"Hotspot analysis results: {json.dumps(hotspot_results, indent=2, default=str)}")
    
    # Get summary statistics
    summary_stats = trend_analyzer.get_summary_statistics(df)
    print(f"Summary statistics: {json.dumps(summary_stats, indent=2, default=str)}")


def demo_visualization(df):
    """Demonstrate visualization capabilities."""
    print("\n=== Visualization Demo ===")
    
    if df.empty:
        print("No data to visualize")
        return
    
    visualizer = Visualizer()
    
    try:
        # Create visualizations
        visualizer.create_time_series_plot(df)
        visualizer.create_cause_analysis(df)
        visualizer.create_severity_analysis(df)
        visualizer.create_location_analysis(df)
        visualizer.create_summary_dashboard(df, {})
        
        print("Visualizations created successfully!")
        print("Check the 'data/results/visualizations' directory for output files")
        
    except Exception as e:
        print(f"Error creating visualizations: {e}")


def demo_configuration():
    """Demonstrate configuration capabilities."""
    print("\n=== Configuration Demo ===")
    
    # Show current configuration
    print("Current configuration:")
    print(f"Scraping delay: {config.get('scraping.request_delay')} seconds")
    print(f"News sources: {list(config.get_news_sources().keys())}")
    print(f"NLP keywords: {len(config.get_nlp_config().get('accident_keywords', []))}")
    print(f"LLM provider: {config.get_llm_config().get('provider')}")
    print(f"Geolocation provider: {config.get_geolocation_config().get('provider')}")


def main():
    """Run the complete demo."""
    print("=== Bangladesh Road Accident Analysis Demo ===")
    print("This demo showcases the key features of the accident analysis system.")
    
    # Set up logging
    logger = setup_logging("demo")
    
    try:
        # Demo 1: Configuration
        demo_configuration()
        
        # Demo 2: Text Processing
        demo_text_processing()
        
        # Demo 3: LLM Extraction
        demo_llm_extraction()
        
        # Demo 4: Geolocation
        demo_geolocation()
        
        # Demo 5: Data Cleaning
        df = demo_data_cleaning()
        
        # Demo 6: Analysis
        demo_analysis(df)
        
        # Demo 7: Visualization
        demo_visualization(df)
        
        print("\n=== Demo Completed Successfully ===")
        print("The system is ready for real data collection and analysis!")
        print("\nTo run the full pipeline with real data:")
        print("1. Set up your API keys (optional):")
        print("   export OPENAI_API_KEY='your_key_here'")
        print("2. Run the main script:")
        print("   python main.py --full")
        print("3. Or run individual components:")
        print("   python main.py --collect  # Collect data")
        print("   python main.py --analyze  # Analyze data")
        print("   python main.py --visualize  # Generate visualizations")
        
    except Exception as e:
        logger.error(f"Error in demo: {e}")
        print(f"Demo failed with error: {e}")


if __name__ == "__main__":
    main()