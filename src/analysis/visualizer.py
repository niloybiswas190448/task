"""
Visualization utilities for accident analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from typing import Dict, Any, Optional
import logging
from pathlib import Path

from ..utils.config import config
from ..utils.helpers import setup_logging, ensure_directory


class Visualizer:
    """Visualization utilities for accident analysis."""
    
    def __init__(self):
        """Initialize visualizer."""
        self.logger = setup_logging("analysis.visualizer")
        self.output_config = config.get_output_config()
        self.analysis_config = config.get_analysis_config()
        
        # Set up plotting style
        self._setup_plotting_style()
        
        # Ensure visualization directory exists
        viz_dir = Path(self.output_config.get('visualizations_dir', 'data/results/visualizations'))
        ensure_directory(viz_dir)
    
    def _setup_plotting_style(self):
        """Set up matplotlib and seaborn plotting styles."""
        try:
            # Set seaborn style
            sns.set_style("whitegrid")
            sns.set_palette("husl")
            
            # Set matplotlib style
            plt.style.use('seaborn-v0_8')
            
            # Set figure size and DPI
            plt.rcParams['figure.figsize'] = self.analysis_config.get('figure_size', [12, 8])
            plt.rcParams['figure.dpi'] = self.analysis_config.get('dpi', 300)
            
        except Exception as e:
            self.logger.warning(f"Could not set plotting style: {e}")
    
    def create_time_series_plot(self, df: pd.DataFrame):
        """
        Create time series plot of accident trends.
        
        Args:
            df: Cleaned DataFrame
        """
        if df.empty or 'date' not in df.columns:
            self.logger.warning("No date data available for time series plot")
            return
        
        try:
            # Prepare data
            df_copy = df.copy()
            df_copy['date'] = pd.to_datetime(df_copy['date'])
            df_copy = df_copy.sort_values('date')
            
            # Monthly aggregation
            monthly_data = df_copy.groupby(df_copy['date'].dt.to_period('M')).agg({
                'deaths': 'sum',
                'injuries': 'sum',
                'id': 'count'
            }).reset_index()
            monthly_data['date'] = monthly_data['date'].dt.to_timestamp()
            
            # Create plot
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
            
            # Plot 1: Accident count over time
            ax1.plot(monthly_data['date'], monthly_data['id'], marker='o', linewidth=2, markersize=6)
            ax1.set_title('Monthly Accident Count in Bangladesh', fontsize=16, fontweight='bold')
            ax1.set_ylabel('Number of Accidents', fontsize=12)
            ax1.grid(True, alpha=0.3)
            
            # Plot 2: Deaths and injuries over time
            ax2.plot(monthly_data['date'], monthly_data['deaths'], marker='s', linewidth=2, markersize=6, label='Deaths', color='red')
            ax2.plot(monthly_data['date'], monthly_data['injuries'], marker='^', linewidth=2, markersize=6, label='Injuries', color='orange')
            ax2.set_title('Monthly Casualties in Bangladesh', fontsize=16, fontweight='bold')
            ax2.set_ylabel('Number of Casualties', fontsize=12)
            ax2.set_xlabel('Date', fontsize=12)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save plot
            output_path = Path(self.output_config.get('visualizations_dir', 'data/results/visualizations'))
            plt.savefig(output_path / 'time_series_trends.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info("Time series plot created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating time series plot: {e}")
    
    def create_hotspot_map(self, df: pd.DataFrame):
        """
        Create heatmap showing accident hotspots.
        
        Args:
            df: Cleaned DataFrame
        """
        if df.empty or 'latitude' not in df.columns or 'longitude' not in df.columns:
            self.logger.warning("No coordinate data available for hotspot map")
            return
        
        try:
            # Filter valid coordinates
            valid_coords = df.dropna(subset=['latitude', 'longitude'])
            
            if valid_coords.empty:
                self.logger.warning("No valid coordinates found for mapping")
                return
            
            # Create map centered on Bangladesh
            m = folium.Map(
                location=[23.6850, 90.3563],  # Center of Bangladesh
                zoom_start=7,
                tiles='OpenStreetMap'
            )
            
            # Add accident markers
            for _, row in valid_coords.iterrows():
                # Determine marker color based on severity
                if row['deaths'] > 0:
                    color = 'red'
                    radius = 8
                elif row['injuries'] > 0:
                    color = 'orange'
                    radius = 6
                else:
                    color = 'yellow'
                    radius = 4
                
                # Create popup content
                popup_content = f"""
                <b>{row.get('title', 'No title')}</b><br>
                Date: {row.get('date', 'Unknown')}<br>
                Location: {row.get('location', 'Unknown')}<br>
                Deaths: {row.get('deaths', 0)}<br>
                Injuries: {row.get('injuries', 0)}<br>
                Cause: {row.get('probable_cause', 'Unknown')}
                """
                
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=radius,
                    popup=folium.Popup(popup_content, max_width=300),
                    color=color,
                    fill=True,
                    fillOpacity=0.7
                ).add_to(m)
            
            # Save map
            output_path = Path(self.output_config.get('visualizations_dir', 'data/results/visualizations'))
            m.save(str(output_path / 'accident_hotspots.html'))
            
            self.logger.info("Hotspot map created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating hotspot map: {e}")
    
    def create_cause_analysis(self, df: pd.DataFrame):
        """
        Create analysis of accident causes.
        
        Args:
            df: Cleaned DataFrame
        """
        if df.empty or 'probable_cause' not in df.columns:
            self.logger.warning("No cause data available for cause analysis")
            return
        
        try:
            # Prepare data
            cause_data = df['probable_cause'].value_counts().head(10)
            
            # Create plot
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # Plot 1: Bar chart of causes
            cause_data.plot(kind='bar', ax=ax1, color='skyblue', edgecolor='black')
            ax1.set_title('Top 10 Accident Causes', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Cause', fontsize=12)
            ax1.set_ylabel('Number of Accidents', fontsize=12)
            ax1.tick_params(axis='x', rotation=45)
            
            # Plot 2: Pie chart of top causes
            top_causes = cause_data.head(5)
            other_causes = cause_data[5:].sum() if len(cause_data) > 5 else 0
            
            if other_causes > 0:
                plot_data = pd.concat([top_causes, pd.Series({'Other': other_causes})])
            else:
                plot_data = top_causes
            
            ax2.pie(plot_data.values, labels=plot_data.index, autopct='%1.1f%%', startangle=90)
            ax2.set_title('Distribution of Accident Causes', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            # Save plot
            output_path = Path(self.output_config.get('visualizations_dir', 'data/results/visualizations'))
            plt.savefig(output_path / 'cause_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info("Cause analysis plot created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating cause analysis: {e}")
    
    def create_vehicle_analysis(self, df: pd.DataFrame):
        """
        Create analysis of vehicle types involved in accidents.
        
        Args:
            df: Cleaned DataFrame
        """
        if df.empty or 'vehicle_types' not in df.columns:
            self.logger.warning("No vehicle data available for vehicle analysis")
            return
        
        try:
            # Prepare data - extract vehicle types from list
            vehicle_counts = {}
            for vehicles in df['vehicle_types']:
                if isinstance(vehicles, list):
                    for vehicle in vehicles:
                        vehicle_counts[vehicle] = vehicle_counts.get(vehicle, 0) + 1
                elif isinstance(vehicles, str):
                    # Try to parse string representation of list
                    try:
                        import ast
                        vehicle_list = ast.literal_eval(vehicles)
                        if isinstance(vehicle_list, list):
                            for vehicle in vehicle_list:
                                vehicle_counts[vehicle] = vehicle_counts.get(vehicle, 0) + 1
                    except:
                        pass
            
            if not vehicle_counts:
                self.logger.warning("No valid vehicle data found")
                return
            
            # Create plot
            vehicle_data = pd.Series(vehicle_counts).sort_values(ascending=False)
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            vehicle_data.plot(kind='bar', ax=ax, color='lightcoral', edgecolor='black')
            ax.set_title('Vehicle Types Involved in Accidents', fontsize=16, fontweight='bold')
            ax.set_xlabel('Vehicle Type', fontsize=12)
            ax.set_ylabel('Number of Accidents', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # Save plot
            output_path = Path(self.output_config.get('visualizations_dir', 'data/results/visualizations'))
            plt.savefig(output_path / 'vehicle_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info("Vehicle analysis plot created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating vehicle analysis: {e}")
    
    def create_severity_analysis(self, df: pd.DataFrame):
        """
        Create analysis of accident severity.
        
        Args:
            df: Cleaned DataFrame
        """
        if df.empty or 'severity' not in df.columns:
            self.logger.warning("No severity data available for severity analysis")
            return
        
        try:
            # Prepare data
            severity_data = df['severity'].value_counts()
            
            # Create plot
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # Plot 1: Bar chart of severity
            colors = {'fatal': 'red', 'major': 'orange', 'minor': 'yellow', 'unknown': 'gray'}
            color_list = [colors.get(severity, 'blue') for severity in severity_data.index]
            
            severity_data.plot(kind='bar', ax=ax1, color=color_list, edgecolor='black')
            ax1.set_title('Accident Severity Distribution', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Severity', fontsize=12)
            ax1.set_ylabel('Number of Accidents', fontsize=12)
            ax1.tick_params(axis='x', rotation=45)
            
            # Plot 2: Pie chart of severity
            ax2.pie(severity_data.values, labels=severity_data.index, autopct='%1.1f%%', startangle=90, colors=color_list)
            ax2.set_title('Severity Distribution', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            # Save plot
            output_path = Path(self.output_config.get('visualizations_dir', 'data/results/visualizations'))
            plt.savefig(output_path / 'severity_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info("Severity analysis plot created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating severity analysis: {e}")
    
    def create_location_analysis(self, df: pd.DataFrame):
        """
        Create analysis of accident locations.
        
        Args:
            df: Cleaned DataFrame
        """
        if df.empty or 'location' not in df.columns:
            self.logger.warning("No location data available for location analysis")
            return
        
        try:
            # Prepare data
            location_data = df['location'].value_counts().head(15)
            
            # Create plot
            fig, ax = plt.subplots(figsize=(14, 10))
            
            location_data.plot(kind='barh', ax=ax, color='lightgreen', edgecolor='black')
            ax.set_title('Top 15 Accident Locations in Bangladesh', fontsize=16, fontweight='bold')
            ax.set_xlabel('Number of Accidents', fontsize=12)
            ax.set_ylabel('Location', fontsize=12)
            
            plt.tight_layout()
            
            # Save plot
            output_path = Path(self.output_config.get('visualizations_dir', 'data/results/visualizations'))
            plt.savefig(output_path / 'location_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info("Location analysis plot created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating location analysis: {e}")
    
    def create_summary_dashboard(self, df: pd.DataFrame, analysis_results: Dict[str, Any]):
        """
        Create a comprehensive summary dashboard.
        
        Args:
            df: Cleaned DataFrame
            analysis_results: Analysis results
        """
        if df.empty:
            self.logger.warning("No data available for dashboard")
            return
        
        try:
            # Create subplots
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=(
                    'Monthly Accident Trends',
                    'Accident Severity Distribution',
                    'Top Accident Causes',
                    'Top Accident Locations',
                    'Casualties Over Time',
                    'Vehicle Types Involved'
                ),
                specs=[[{"type": "scatter"}, {"type": "pie"}],
                       [{"type": "bar"}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "bar"}]]
            )
            
            # Plot 1: Monthly trends
            if 'date' in df.columns:
                monthly_data = df.groupby(df['date'].dt.to_period('M')).size().reset_index()
                monthly_data['date'] = monthly_data['date'].dt.to_timestamp()
                
                fig.add_trace(
                    go.Scatter(x=monthly_data['date'], y=monthly_data[0], mode='lines+markers', name='Accidents'),
                    row=1, col=1
                )
            
            # Plot 2: Severity distribution
            if 'severity' in df.columns:
                severity_data = df['severity'].value_counts()
                fig.add_trace(
                    go.Pie(labels=severity_data.index, values=severity_data.values, name="Severity"),
                    row=1, col=2
                )
            
            # Plot 3: Top causes
            if 'probable_cause' in df.columns:
                cause_data = df['probable_cause'].value_counts().head(8)
                fig.add_trace(
                    go.Bar(x=cause_data.index, y=cause_data.values, name="Causes"),
                    row=2, col=1
                )
            
            # Plot 4: Top locations
            if 'location' in df.columns:
                location_data = df['location'].value_counts().head(8)
                fig.add_trace(
                    go.Bar(x=location_data.index, y=location_data.values, name="Locations"),
                    row=2, col=2
                )
            
            # Plot 5: Casualties over time
            if 'date' in df.columns and 'deaths' in df.columns and 'injuries' in df.columns:
                monthly_casualties = df.groupby(df['date'].dt.to_period('M')).agg({
                    'deaths': 'sum',
                    'injuries': 'sum'
                }).reset_index()
                monthly_casualties['date'] = monthly_casualties['date'].dt.to_timestamp()
                
                fig.add_trace(
                    go.Scatter(x=monthly_casualties['date'], y=monthly_casualties['deaths'], 
                              mode='lines+markers', name='Deaths'),
                    row=3, col=1
                )
                fig.add_trace(
                    go.Scatter(x=monthly_casualties['date'], y=monthly_casualties['injuries'], 
                              mode='lines+markers', name='Injuries'),
                    row=3, col=1
                )
            
            # Plot 6: Vehicle types
            if 'vehicle_types' in df.columns:
                vehicle_counts = {}
                for vehicles in df['vehicle_types']:
                    if isinstance(vehicles, list):
                        for vehicle in vehicles:
                            vehicle_counts[vehicle] = vehicle_counts.get(vehicle, 0) + 1
                
                if vehicle_counts:
                    vehicle_data = pd.Series(vehicle_counts).sort_values(ascending=False).head(8)
                    fig.add_trace(
                        go.Bar(x=vehicle_data.index, y=vehicle_data.values, name="Vehicles"),
                        row=3, col=2
                    )
            
            # Update layout
            fig.update_layout(
                title_text="Bangladesh Road Accident Analysis Dashboard",
                showlegend=False,
                height=1200
            )
            
            # Save dashboard
            output_path = Path(self.output_config.get('visualizations_dir', 'data/results/visualizations'))
            fig.write_html(str(output_path / 'analysis_dashboard.html'))
            
            self.logger.info("Summary dashboard created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating summary dashboard: {e}")
    
    def create_all_visualizations(self, df: pd.DataFrame, analysis_results: Dict[str, Any] = None):
        """
        Create all visualizations.
        
        Args:
            df: Cleaned DataFrame
            analysis_results: Analysis results (optional)
        """
        self.logger.info("Creating all visualizations")
        
        try:
            self.create_time_series_plot(df)
            self.create_hotspot_map(df)
            self.create_cause_analysis(df)
            self.create_vehicle_analysis(df)
            self.create_severity_analysis(df)
            self.create_location_analysis(df)
            self.create_summary_dashboard(df, analysis_results or {})
            
            self.logger.info("All visualizations created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating visualizations: {e}")