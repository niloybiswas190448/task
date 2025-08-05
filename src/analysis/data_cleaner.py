"""
Data cleaning utilities for accident analysis.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging

from ..utils.config import config
from ..utils.helpers import setup_logging, save_dataframe, load_dataframe


class DataCleaner:
    """Data cleaning utilities for accident analysis."""
    
    def __init__(self):
        """Initialize data cleaner."""
        self.logger = setup_logging("analysis.data_cleaner")
        self.cleaning_config = config.get('data_processing', {})
        
    def clean_articles_data(self, articles: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Clean and convert articles data to DataFrame.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Cleaned DataFrame
        """
        if not articles:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(articles)
        
        # Clean the DataFrame
        df = self._clean_dataframe(df)
        
        return df
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean DataFrame by removing duplicates, handling missing values, etc.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df
        
        self.logger.info(f"Starting data cleaning for {len(df)} articles")
        
        # Remove duplicates
        if self.cleaning_config.get('remove_duplicates', True):
            initial_count = len(df)
            df = self._remove_duplicates(df)
            self.logger.info(f"Removed {initial_count - len(df)} duplicate articles")
        
        # Handle missing dates
        if self.cleaning_config.get('fill_missing_dates', True):
            df = self._fill_missing_dates(df)
        
        # Standardize locations
        if self.cleaning_config.get('standardize_locations', True):
            df = self._standardize_locations(df)
        
        # Clean text fields
        df = self._clean_text_fields(df)
        
        # Handle missing values
        df = self._handle_missing_values(df)
        
        # Convert data types
        df = self._convert_data_types(df)
        
        # Filter valid accident articles
        df = self._filter_accident_articles(df)
        
        self.logger.info(f"Data cleaning completed. Final dataset has {len(df)} articles")
        
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate articles.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with duplicates removed
        """
        if df.empty:
            return df
        
        # Remove exact duplicates
        df = df.drop_duplicates()
        
        # Remove duplicates based on URL
        df = df.drop_duplicates(subset=['url'], keep='first')
        
        # Remove duplicates based on title similarity
        df = df.drop_duplicates(subset=['title'], keep='first')
        
        return df
    
    def _fill_missing_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fill missing dates with reasonable defaults.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with filled dates
        """
        if df.empty:
            return df
        
        # Convert date columns to datetime
        date_columns = ['date', 'accident_date', 'llm_accident_date']
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Fill missing accident dates with article dates
        if 'accident_date' in df.columns and 'date' in df.columns:
            df['accident_date'] = df['accident_date'].fillna(df['date'])
        
        if 'llm_accident_date' in df.columns and 'accident_date' in df.columns:
            df['llm_accident_date'] = df['llm_accident_date'].fillna(df['accident_date'])
        
        return df
    
    def _standardize_locations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize location names.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with standardized locations
        """
        if df.empty:
            return df
        
        location_mapping = self.cleaning_config.get('location_mapping', {})
        
        # Standardize location column
        if 'location' in df.columns:
            df['location'] = df['location'].str.lower().map(location_mapping).fillna(df['location'])
        
        # Standardize LLM location column
        if 'llm_location' in df.columns:
            df['llm_location'] = df['llm_location'].str.lower().map(location_mapping).fillna(df['llm_location'])
        
        return df
    
    def _clean_text_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean text fields.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with cleaned text
        """
        if df.empty:
            return df
        
        text_columns = ['title', 'content', 'location', 'probable_cause', 'severity', 'area_type']
        
        for col in text_columns:
            if col in df.columns:
                # Remove extra whitespace
                df[col] = df[col].astype(str).str.strip()
                # Replace multiple spaces with single space
                df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
                # Replace empty strings with NaN
                df[col] = df[col].replace('', np.nan)
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the DataFrame.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with handled missing values
        """
        if df.empty:
            return df
        
        # Fill numeric missing values with 0
        numeric_columns = ['deaths', 'injuries', 'llm_deaths', 'llm_injuries']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        
        # Fill categorical missing values with 'unknown'
        categorical_columns = ['probable_cause', 'severity', 'area_type', 'llm_cause', 'llm_severity', 'llm_area_type']
        for col in categorical_columns:
            if col in df.columns:
                df[col] = df[col].fillna('unknown')
        
        # Fill list columns with empty lists
        list_columns = ['vehicle_types', 'llm_vehicles']
        for col in list_columns:
            if col in df.columns:
                df[col] = df[col].fillna('[]')
        
        return df
    
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert data types to appropriate types.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with correct data types
        """
        if df.empty:
            return df
        
        # Convert numeric columns
        numeric_columns = ['deaths', 'injuries', 'llm_deaths', 'llm_injuries']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Convert boolean columns
        boolean_columns = ['is_accident', 'llm_processed', 'coordinates_valid']
        for col in boolean_columns:
            if col in df.columns:
                df[col] = df[col].astype(bool)
        
        # Convert list columns
        list_columns = ['vehicle_types', 'llm_vehicles']
        for col in list_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._safe_eval_list)
        
        return df
    
    def _safe_eval_list(self, value):
        """
        Safely evaluate string representation of list.
        
        Args:
            value: Value to evaluate
            
        Returns:
            List or empty list if evaluation fails
        """
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            try:
                import ast
                return ast.literal_eval(value)
            except:
                return []
        else:
            return []
    
    def _filter_accident_articles(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter to keep only accident-related articles.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Filtered DataFrame
        """
        if df.empty:
            return df
        
        # Filter by is_accident flag
        if 'is_accident' in df.columns:
            df = df[df['is_accident'] == True]
        
        # Filter by minimum content length
        min_length = config.get('nlp.min_article_length', 100)
        if 'content' in df.columns:
            df = df[df['content'].str.len() >= min_length]
        
        return df
    
    def get_cleaning_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get statistics about the cleaned data.
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            Statistics dictionary
        """
        if df.empty:
            return {'total_articles': 0}
        
        stats = {
            'total_articles': len(df),
            'articles_with_dates': df['date'].notna().sum(),
            'articles_with_locations': df['location'].notna().sum(),
            'articles_with_coordinates': df['coordinates_valid'].sum() if 'coordinates_valid' in df.columns else 0,
            'articles_with_deaths': (df['deaths'] > 0).sum(),
            'articles_with_injuries': (df['injuries'] > 0).sum(),
            'llm_processed_articles': df['llm_processed'].sum() if 'llm_processed' in df.columns else 0,
            'date_range': {
                'start': df['date'].min().strftime('%Y-%m-%d') if df['date'].min() else None,
                'end': df['date'].max().strftime('%Y-%m-%d') if df['date'].max() else None
            },
            'sources': df['source'].value_counts().to_dict() if 'source' in df.columns else {},
            'severity_distribution': df['severity'].value_counts().to_dict() if 'severity' in df.columns else {},
            'area_type_distribution': df['area_type'].value_counts().to_dict() if 'area_type' in df.columns else {}
        }
        
        return stats
    
    def save_cleaned_data(self, df: pd.DataFrame, filepath: str, format: str = 'csv'):
        """
        Save cleaned data to file.
        
        Args:
            df: Cleaned DataFrame
            filepath: Output file path
            format: File format (csv, json, excel)
        """
        if df.empty:
            self.logger.warning("No data to save")
            return
        
        try:
            save_dataframe(df, filepath, format)
            self.logger.info(f"Cleaned data saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving cleaned data: {e}")
    
    def load_cleaned_data(self, filepath: str, format: str = 'csv') -> pd.DataFrame:
        """
        Load cleaned data from file.
        
        Args:
            filepath: Input file path
            format: File format (csv, json, excel)
            
        Returns:
            Loaded DataFrame
        """
        try:
            df = load_dataframe(filepath, format)
            self.logger.info(f"Cleaned data loaded from {filepath}")
            return df
        except Exception as e:
            self.logger.error(f"Error loading cleaned data: {e}")
            return pd.DataFrame()