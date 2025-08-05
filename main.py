"""
Main entry point for Bangladesh Road Accident Analysis.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.config import config
from src.utils.helpers import setup_logging, ensure_directory
from src.scrapers.daily_star import DailyStarScraper
from src.scrapers.prothom_alo import ProthomAloScraper
from src.scrapers.dhaka_tribune import DhakaTribuneScraper
from src.scrapers.bdnews24 import BDNews24Scraper
from src.nlp.text_processor import TextProcessor
from src.nlp.llm_extractor import LLMExtractor
from src.geolocation.geocoder import Geocoder
from src.analysis.data_cleaner import DataCleaner
from src.analysis.visualizer import Visualizer
from src.analysis.trend_analyzer import TrendAnalyzer


class AccidentAnalyzer:
    """Main class for orchestrating accident analysis."""
    
    def __init__(self):
        """Initialize the accident analyzer."""
        self.logger = setup_logging("main.analyzer")
        
        # Initialize components
        self.scrapers = self._initialize_scrapers()
        self.text_processor = TextProcessor()
        self.llm_extractor = LLMExtractor()
        self.geocoder = Geocoder()
        self.data_cleaner = DataCleaner()
        self.visualizer = Visualizer()
        
        # Get output configuration
        self.output_config = config.get_output_config()
        
        # Ensure output directories exist
        self._ensure_directories()
        
        self.logger.info("Accident analyzer initialized successfully")
    
    def _initialize_scrapers(self) -> List:
        """Initialize news scrapers."""
        scrapers = []
        news_sources = config.get_news_sources()
        
        for source_id, source_config in news_sources.items():
            if source_config.get('enabled', True):
                try:
                    if source_id == 'daily_star':
                        scrapers.append(DailyStarScraper())
                    elif source_id == 'prothom_alo':
                        scrapers.append(ProthomAloScraper())
                    elif source_id == 'dhaka_tribune':
                        scrapers.append(DhakaTribuneScraper())
                    elif source_id == 'bdnews24':
                        scrapers.append(BDNews24Scraper())
                    
                    self.logger.info(f"Initialized scraper for {source_config['name']}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to initialize scraper for {source_id}: {e}")
        
        return scrapers
    
    def _ensure_directories(self):
        """Ensure all output directories exist."""
        directories = [
            self.output_config.get('raw_data_dir', 'data/raw'),
            self.output_config.get('processed_data_dir', 'data/processed'),
            self.output_config.get('results_dir', 'data/results'),
            self.output_config.get('visualizations_dir', 'data/results/visualizations')
        ]
        
        for directory in directories:
            ensure_directory(directory)
    
    def collect_data(self, max_pages_per_source: int = None) -> List[Dict[str, Any]]:
        """
        Collect data from all news sources.
        
        Args:
            max_pages_per_source: Maximum pages to scrape per source
            
        Returns:
            List of collected articles
        """
        self.logger.info("Starting data collection from news sources")
        
        all_articles = []
        
        for scraper in self.scrapers:
            try:
                self.logger.info(f"Scraping articles from {scraper.source_name}")
                articles = scraper.scrape_articles(max_pages_per_source)
                all_articles.extend(articles)
                self.logger.info(f"Collected {len(articles)} articles from {scraper.source_name}")
                
            except Exception as e:
                self.logger.error(f"Error scraping from {scraper.source_name}: {e}")
        
        self.logger.info(f"Data collection completed. Total articles: {len(all_articles)}")
        
        # Save raw data
        if all_articles:
            self._save_raw_data(all_articles)
        
        return all_articles
    
    def process_data(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process collected articles with NLP and LLM.
        
        Args:
            articles: List of raw articles
            
        Returns:
            List of processed articles
        """
        self.logger.info("Starting data processing")
        
        processed_articles = []
        
        for i, article in enumerate(articles):
            try:
                # Process with text processor
                processed_article = self.text_processor.process_article(article)
                
                # Enhance with LLM if available
                if self.llm_extractor.is_available():
                    processed_article = self.llm_extractor.enhance_article_data(processed_article)
                
                processed_articles.append(processed_article)
                
                if (i + 1) % 10 == 0:
                    self.logger.info(f"Processed {i + 1}/{len(articles)} articles")
                    
            except Exception as e:
                self.logger.error(f"Error processing article {i}: {e}")
                processed_articles.append(article)
        
        self.logger.info(f"Data processing completed. Processed {len(processed_articles)} articles")
        
        return processed_articles
    
    def add_geolocation(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add geolocation data to articles.
        
        Args:
            articles: List of processed articles
            
        Returns:
            Articles with geolocation data
        """
        self.logger.info("Adding geolocation data")
        
        articles_with_geo = self.geocoder.add_coordinates_to_articles(articles)
        
        self.logger.info("Geolocation data added")
        
        return articles_with_geo
    
    def clean_data(self, articles: List[Dict[str, Any]]) -> 'pd.DataFrame':
        """
        Clean and prepare data for analysis.
        
        Args:
            articles: List of processed articles
            
        Returns:
            Cleaned DataFrame
        """
        self.logger.info("Cleaning data")
        
        df = self.data_cleaner.clean_articles_data(articles)
        
        # Save cleaned data
        if not df.empty:
            self._save_cleaned_data(df)
        
        # Print cleaning statistics
        stats = self.data_cleaner.get_cleaning_stats(df)
        self.logger.info(f"Data cleaning statistics: {stats}")
        
        return df
    
    def analyze_data(self, df: 'pd.DataFrame') -> Dict[str, Any]:
        """
        Perform data analysis.
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            Analysis results
        """
        self.logger.info("Starting data analysis")
        
        if df.empty:
            self.logger.warning("No data to analyze")
            return {}
        
        # Perform trend analysis
        trend_analyzer = TrendAnalyzer()
        trend_results = trend_analyzer.analyze_trends(df)
        
        # Perform hotspot analysis
        hotspot_results = trend_analyzer.analyze_hotspots(df)
        
        # Combine results
        analysis_results = {
            'trends': trend_results,
            'hotspots': hotspot_results,
            'summary_stats': self._get_summary_stats(df)
        }
        
        # Save analysis results
        self._save_analysis_results(analysis_results)
        
        self.logger.info("Data analysis completed")
        
        return analysis_results
    
    def generate_visualizations(self, df: 'pd.DataFrame', analysis_results: Dict[str, Any]):
        """
        Generate visualizations.
        
        Args:
            df: Cleaned DataFrame
            analysis_results: Analysis results
        """
        self.logger.info("Generating visualizations")
        
        if df.empty:
            self.logger.warning("No data to visualize")
            return
        
        try:
            # Generate various visualizations
            self.visualizer.create_time_series_plot(df)
            self.visualizer.create_hotspot_map(df)
            self.visualizer.create_cause_analysis(df)
            self.visualizer.create_vehicle_analysis(df)
            self.visualizer.create_severity_analysis(df)
            
            self.logger.info("Visualizations generated successfully")
            
        except Exception as e:
            self.logger.error(f"Error generating visualizations: {e}")
    
    def run_full_pipeline(self):
        """Run the complete analysis pipeline."""
        self.logger.info("Starting full accident analysis pipeline")
        
        try:
            # Step 1: Collect data
            articles = self.collect_data()
            
            if not articles:
                self.logger.warning("No articles collected. Exiting.")
                return
            
            # Step 2: Process data
            processed_articles = self.process_data(articles)
            
            # Step 3: Add geolocation
            articles_with_geo = self.add_geolocation(processed_articles)
            
            # Step 4: Clean data
            df = self.clean_data(articles_with_geo)
            
            if df.empty:
                self.logger.warning("No valid data after cleaning. Exiting.")
                return
            
            # Step 5: Analyze data
            analysis_results = self.analyze_data(df)
            
            # Step 6: Generate visualizations
            self.generate_visualizations(df, analysis_results)
            
            self.logger.info("Full pipeline completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in full pipeline: {e}")
            raise
    
    def _save_raw_data(self, articles: List[Dict[str, Any]]):
        """Save raw collected data."""
        try:
            import pandas as pd
            df = pd.DataFrame(articles)
            
            raw_data_path = Path(self.output_config.get('raw_data_dir', 'data/raw'))
            df.to_csv(raw_data_path / 'raw_articles.csv', index=False, encoding='utf-8')
            df.to_json(raw_data_path / 'raw_articles.json', orient='records', indent=2, force_ascii=False)
            
            self.logger.info(f"Raw data saved to {raw_data_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving raw data: {e}")
    
    def _save_cleaned_data(self, df: 'pd.DataFrame'):
        """Save cleaned data."""
        try:
            processed_data_path = Path(self.output_config.get('processed_data_dir', 'data/processed'))
            df.to_csv(processed_data_path / 'cleaned_articles.csv', index=False, encoding='utf-8')
            df.to_json(processed_data_path / 'cleaned_articles.json', orient='records', indent=2, force_ascii=False)
            
            self.logger.info(f"Cleaned data saved to {processed_data_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving cleaned data: {e}")
    
    def _save_analysis_results(self, results: Dict[str, Any]):
        """Save analysis results."""
        try:
            import json
            
            results_path = Path(self.output_config.get('results_dir', 'data/results'))
            with open(results_path / 'analysis_results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            
            self.logger.info(f"Analysis results saved to {results_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving analysis results: {e}")
    
    def _get_summary_stats(self, df: 'pd.DataFrame') -> Dict[str, Any]:
        """Get summary statistics."""
        if df.empty:
            return {}
        
        stats = {
            'total_accidents': len(df),
            'total_deaths': df['deaths'].sum(),
            'total_injuries': df['injuries'].sum(),
            'date_range': {
                'start': df['date'].min().strftime('%Y-%m-%d') if df['date'].min() else None,
                'end': df['date'].max().strftime('%Y-%m-%d') if df['date'].max() else None
            },
            'top_locations': df['location'].value_counts().head(10).to_dict(),
            'top_causes': df['probable_cause'].value_counts().head(10).to_dict(),
            'severity_distribution': df['severity'].value_counts().to_dict()
        }
        
        return stats


class TrendAnalyzer:
    """Trend analysis utilities."""
    
    def __init__(self):
        """Initialize trend analyzer."""
        self.logger = setup_logging("analysis.trend_analyzer")
    
    def analyze_trends(self, df: 'pd.DataFrame') -> Dict[str, Any]:
        """Analyze temporal trends in accident data."""
        if df.empty:
            return {}
        
        try:
            # Monthly trends
            df['month'] = df['date'].dt.to_period('M')
            monthly_stats = df.groupby('month').agg({
                'deaths': 'sum',
                'injuries': 'sum',
                'id': 'count'
            }).reset_index()
            
            # Yearly trends
            df['year'] = df['date'].dt.year
            yearly_stats = df.groupby('year').agg({
                'deaths': 'sum',
                'injuries': 'sum',
                'id': 'count'
            }).reset_index()
            
            return {
                'monthly_trends': monthly_stats.to_dict('records'),
                'yearly_trends': yearly_stats.to_dict('records')
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {e}")
            return {}
    
    def analyze_hotspots(self, df: 'pd.DataFrame') -> Dict[str, Any]:
        """Analyze accident hotspots."""
        if df.empty:
            return {}
        
        try:
            # Location-based hotspots
            location_stats = df.groupby('location').agg({
                'deaths': 'sum',
                'injuries': 'sum',
                'id': 'count'
            }).sort_values('deaths', ascending=False).head(20)
            
            return {
                'location_hotspots': location_stats.to_dict('index')
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing hotspots: {e}")
            return {}


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Bangladesh Road Accident Analysis')
    parser.add_argument('--collect', action='store_true', help='Collect data from news sources')
    parser.add_argument('--analyze', action='store_true', help='Analyze collected data')
    parser.add_argument('--visualize', action='store_true', help='Generate visualizations')
    parser.add_argument('--full', action='store_true', help='Run complete pipeline')
    parser.add_argument('--max-pages', type=int, default=None, help='Maximum pages to scrape per source')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = AccidentAnalyzer()
    
    if args.full:
        # Run complete pipeline
        analyzer.run_full_pipeline()
    
    elif args.collect:
        # Collect data only
        articles = analyzer.collect_data(args.max_pages)
        print(f"Collected {len(articles)} articles")
    
    elif args.analyze:
        # Analyze existing data
        try:
            import pandas as pd
            df = pd.read_csv('data/processed/cleaned_articles.csv')
            results = analyzer.analyze_data(df)
            print("Analysis completed")
        except FileNotFoundError:
            print("No cleaned data found. Run data collection first.")
    
    elif args.visualize:
        # Generate visualizations
        try:
            import pandas as pd
            df = pd.read_csv('data/processed/cleaned_articles.csv')
            analyzer.generate_visualizations(df, {})
            print("Visualizations generated")
        except FileNotFoundError:
            print("No cleaned data found. Run data collection first.")
    
    else:
        # Default: run complete pipeline
        analyzer.run_full_pipeline()


if __name__ == "__main__":
    main()