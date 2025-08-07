"""
Trend analysis utilities for accident analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging

from ..utils.helpers import setup_logging


class TrendAnalyzer:
    """Trend analysis utilities for accident data."""
    
    def __init__(self):
        """Initialize trend analyzer."""
        self.logger = setup_logging("analysis.trend_analyzer")
    
    def analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze temporal trends in accident data.
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            Dictionary with trend analysis results
        """
        if df.empty:
            return {}
        
        try:
            # Ensure date column is datetime
            df_copy = df.copy()
            df_copy['date'] = pd.to_datetime(df_copy['date'])
            
            # Monthly trends
            df_copy['month'] = df_copy['date'].dt.to_period('M')
            monthly_stats = df_copy.groupby('month').agg({
                'deaths': 'sum',
                'injuries': 'sum',
                'id': 'count'
            }).reset_index()
            monthly_stats['month'] = monthly_stats['month'].astype(str)
            
            # Yearly trends
            df_copy['year'] = df_copy['date'].dt.year
            yearly_stats = df_copy.groupby('year').agg({
                'deaths': 'sum',
                'injuries': 'sum',
                'id': 'count'
            }).reset_index()
            
            # Weekly trends
            df_copy['week'] = df_copy['date'].dt.isocalendar().week
            weekly_stats = df_copy.groupby(['year', 'week']).agg({
                'deaths': 'sum',
                'injuries': 'sum',
                'id': 'count'
            }).reset_index()
            
            return {
                'monthly_trends': monthly_stats.to_dict('records'),
                'yearly_trends': yearly_stats.to_dict('records'),
                'weekly_trends': weekly_stats.to_dict('records')
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {e}")
            return {}
    
    def analyze_hotspots(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze accident hotspots.
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            Dictionary with hotspot analysis results
        """
        if df.empty:
            return {}
        
        try:
            # Location-based hotspots
            location_stats = df.groupby('location').agg({
                'deaths': 'sum',
                'injuries': 'sum',
                'id': 'count'
            }).sort_values('deaths', ascending=False).head(20)
            
            # Time-based hotspots (hour of day)
            if 'date' in df.columns:
                df_copy = df.copy()
                df_copy['date'] = pd.to_datetime(df_copy['date'])
                df_copy['hour'] = df_copy['date'].dt.hour
                hourly_stats = df_copy.groupby('hour').agg({
                    'deaths': 'sum',
                    'injuries': 'sum',
                    'id': 'count'
                }).reset_index()
            else:
                hourly_stats = pd.DataFrame()
            
            # Day of week hotspots
            if 'date' in df.columns:
                df_copy['day_of_week'] = df_copy['date'].dt.day_name()
                day_stats = df_copy.groupby('day_of_week').agg({
                    'deaths': 'sum',
                    'injuries': 'sum',
                    'id': 'count'
                }).reset_index()
            else:
                day_stats = pd.DataFrame()
            
            return {
                'location_hotspots': location_stats.to_dict('index'),
                'hourly_hotspots': hourly_stats.to_dict('records') if not hourly_stats.empty else [],
                'day_of_week_hotspots': day_stats.to_dict('records') if not day_stats.empty else []
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing hotspots: {e}")
            return {}
    
    def analyze_seasonal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze seasonal patterns in accident data.
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            Dictionary with seasonal analysis results
        """
        if df.empty or 'date' not in df.columns:
            return {}
        
        try:
            df_copy = df.copy()
            df_copy['date'] = pd.to_datetime(df_copy['date'])
            
            # Monthly patterns
            df_copy['month'] = df_copy['date'].dt.month
            monthly_patterns = df_copy.groupby('month').agg({
                'deaths': 'sum',
                'injuries': 'sum',
                'id': 'count'
            }).reset_index()
            
            # Seasonal patterns (Bangladesh has 6 seasons)
            def get_bangladesh_season(month):
                if month in [11, 12, 1]:
                    return 'Winter'
                elif month in [2, 3]:
                    return 'Spring'
                elif month in [4, 5]:
                    return 'Summer'
                elif month in [6, 7]:
                    return 'Monsoon'
                elif month in [8, 9]:
                    return 'Autumn'
                else:
                    return 'Late Autumn'
            
            df_copy['season'] = df_copy['month'].apply(get_bangladesh_season)
            seasonal_patterns = df_copy.groupby('season').agg({
                'deaths': 'sum',
                'injuries': 'sum',
                'id': 'count'
            }).reset_index()
            
            return {
                'monthly_patterns': monthly_patterns.to_dict('records'),
                'seasonal_patterns': seasonal_patterns.to_dict('records')
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing seasonal patterns: {e}")
            return {}
    
    def analyze_correlation_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze correlations between different variables.
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            Dictionary with correlation analysis results
        """
        if df.empty:
            return {}
        
        try:
            # Select numeric columns for correlation
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            correlation_matrix = df[numeric_cols].corr()
            
            # Find correlations with deaths and injuries
            death_correlations = {}
            injury_correlations = {}
            
            if 'deaths' in correlation_matrix.columns:
                death_correlations = correlation_matrix['deaths'].sort_values(ascending=False).to_dict()
            
            if 'injuries' in correlation_matrix.columns:
                injury_correlations = correlation_matrix['injuries'].sort_values(ascending=False).to_dict()
            
            return {
                'correlation_matrix': correlation_matrix.to_dict(),
                'death_correlations': death_correlations,
                'injury_correlations': injury_correlations
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing correlations: {e}")
            return {}
    
    def get_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive summary statistics.
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        if df.empty:
            return {}
        
        try:
            stats = {
                'total_accidents': len(df),
                'total_deaths': df['deaths'].sum() if 'deaths' in df.columns else 0,
                'total_injuries': df['injuries'].sum() if 'injuries' in df.columns else 0,
                'date_range': {
                    'start': df['date'].min().strftime('%Y-%m-%d') if 'date' in df.columns and df['date'].min() else None,
                    'end': df['date'].max().strftime('%Y-%m-%d') if 'date' in df.columns and df['date'].max() else None
                },
                'unique_locations': df['location'].nunique() if 'location' in df.columns else 0,
                'unique_sources': df['source'].nunique() if 'source' in df.columns else 0,
                'avg_deaths_per_accident': df['deaths'].mean() if 'deaths' in df.columns else 0,
                'avg_injuries_per_accident': df['injuries'].mean() if 'injuries' in df.columns else 0
            }
            
            # Add categorical distributions
            if 'severity' in df.columns:
                stats['severity_distribution'] = df['severity'].value_counts().to_dict()
            
            if 'probable_cause' in df.columns:
                stats['cause_distribution'] = df['probable_cause'].value_counts().head(10).to_dict()
            
            if 'area_type' in df.columns:
                stats['area_type_distribution'] = df['area_type'].value_counts().to_dict()
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating summary statistics: {e}")
            return {}