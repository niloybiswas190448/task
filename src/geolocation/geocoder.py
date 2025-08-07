"""
Geocoding utilities for accident analysis.
"""

import time
from typing import Dict, Any, Optional, Tuple
import logging

from ..utils.config import config
from ..utils.helpers import setup_logging


class Geocoder:
    """Geocoding utilities for converting locations to coordinates."""
    
    def __init__(self):
        """Initialize geocoder."""
        self.logger = setup_logging("geolocation.geocoder")
        self.geo_config = config.get_geolocation_config()
        
        # Initialize geocoding service
        self.geocoder = None
        self._initialize_geocoder()
        
        # Cache for geocoding results
        self.cache = {}
    
    def _initialize_geocoder(self):
        """Initialize geocoding service based on configuration."""
        provider = self.geo_config.get('provider', 'nominatim')
        
        if provider == 'nominatim':
            try:
                from geopy.geocoders import Nominatim
                from geopy.exc import GeocoderTimedOut
                
                self.geocoder = Nominatim(
                    user_agent="bangladesh_accident_analysis",
                    timeout=self.geo_config.get('timeout', 10)
                )
                self.provider = 'nominatim'
                
            except ImportError:
                self.logger.error("Geopy library not installed. Install with: pip install geopy")
                return
            except Exception as e:
                self.logger.error(f"Failed to initialize Nominatim geocoder: {e}")
                return
        
        elif provider == 'google':
            try:
                from geopy.geocoders import GoogleV3
                
                api_key = self.geo_config.get('google_api_key')
                if not api_key:
                    self.logger.warning("Google Maps API key not found. Using Nominatim as fallback.")
                    self._initialize_geocoder_fallback()
                    return
                
                self.geocoder = GoogleV3(
                    api_key=api_key,
                    timeout=self.geo_config.get('timeout', 10)
                )
                self.provider = 'google'
                
            except ImportError:
                self.logger.error("Geopy library not installed. Install with: pip install geopy")
                return
            except Exception as e:
                self.logger.error(f"Failed to initialize Google geocoder: {e}")
                return
        
        else:
            self.logger.warning(f"Unsupported geocoding provider: {provider}")
            return
        
        self.logger.info(f"Geocoder initialized with provider: {provider}")
    
    def _initialize_geocoder_fallback(self):
        """Initialize fallback geocoder (Nominatim)."""
        try:
            from geopy.geocoders import Nominatim
            
            self.geocoder = Nominatim(
                user_agent="bangladesh_accident_analysis",
                timeout=self.geo_config.get('timeout', 10)
            )
            self.provider = 'nominatim'
            
        except Exception as e:
            self.logger.error(f"Failed to initialize fallback geocoder: {e}")
    
    def geocode_location(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Geocode a location to get coordinates.
        
        Args:
            location: Location name
            
        Returns:
            Tuple of (latitude, longitude) or None if failed
        """
        if not self.geocoder or not location:
            return None
        
        # Check cache first
        if location in self.cache:
            return self.cache[location]
        
        try:
            # Add country code for better results
            country_code = self.geo_config.get('country_code', 'BD')
            search_query = f"{location}, {country_code}"
            
            # Geocode the location
            location_obj = self.geocoder.geocode(search_query)
            
            if location_obj:
                coordinates = (location_obj.latitude, location_obj.longitude)
                
                # Cache the result
                self.cache[location] = coordinates
                
                # Add delay to respect rate limits
                time.sleep(self.geo_config.get('delay', 1))
                
                return coordinates
            else:
                self.logger.warning(f"Could not geocode location: {location}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error geocoding {location}: {e}")
            return None
    
    def batch_geocode(self, locations: list[str]) -> Dict[str, Optional[Tuple[float, float]]]:
        """
        Geocode multiple locations.
        
        Args:
            locations: List of location names
            
        Returns:
            Dictionary mapping locations to coordinates
        """
        results = {}
        
        for location in locations:
            if location:
                coordinates = self.geocode_location(location)
                results[location] = coordinates
        
        return results
    
    def get_bangladesh_coordinates(self) -> Dict[str, Tuple[float, float]]:
        """
        Get coordinates for major Bangladeshi cities.
        
        Returns:
            Dictionary of city coordinates
        """
        return {
            'Dhaka': (23.8103, 90.4125),
            'Chittagong': (22.3419, 91.8132),
            'Sylhet': (24.8949, 91.8687),
            'Rajshahi': (24.3745, 88.6042),
            'Khulna': (22.8456, 89.5403),
            'Barisal': (22.7010, 90.3535),
            'Rangpur': (25.7466, 89.2517),
            'Mymensingh': (24.7471, 90.4203),
            'Comilla': (23.4607, 91.1809),
            'Narayanganj': (23.6237, 90.4999),
            'Gazipur': (24.0023, 90.4264),
            'Tangail': (24.2513, 89.9167),
            'Bogra': (24.8510, 89.3711),
            'Kushtia': (23.9089, 89.1220),
            'Jessore': (23.1707, 89.2097),
            'Faridpur': (23.6061, 89.8406),
            'Pabna': (24.0023, 89.2376),
            'Dinajpur': (25.6279, 88.6332),
            'Noakhali': (22.8333, 91.1000),
            'Feni': (23.0159, 91.3976),
            'Cox\'s Bazar': (21.4272, 92.0058),
            'Chandpur': (23.2333, 90.6500),
            'Lakshmipur': (22.9500, 90.8333)
        }
    
    def get_location_coordinates(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Get coordinates for a location, using predefined coordinates first.
        
        Args:
            location: Location name
            
        Returns:
            Coordinates tuple or None
        """
        # Check predefined coordinates first
        bangladesh_coords = self.get_bangladesh_coordinates()
        
        # Try exact match
        if location in bangladesh_coords:
            return bangladesh_coords[location]
        
        # Try case-insensitive match
        location_lower = location.lower()
        for city, coords in bangladesh_coords.items():
            if city.lower() == location_lower:
                return coords
        
        # Try partial match
        for city, coords in bangladesh_coords.items():
            if location_lower in city.lower() or city.lower() in location_lower:
                return coords
        
        # If not found in predefined coordinates, try geocoding
        return self.geocode_location(location)
    
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """
        Validate if coordinates are within Bangladesh.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            True if coordinates are within Bangladesh
        """
        # Bangladesh bounding box (approximate)
        min_lat, max_lat = 20.7434, 26.6340
        min_lon, max_lon = 88.0104, 92.6737
        
        return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon
    
    def get_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """
        Calculate distance between two coordinates in kilometers.
        
        Args:
            coord1: First coordinate tuple (lat, lon)
            coord2: Second coordinate tuple (lat, lon)
            
        Returns:
            Distance in kilometers
        """
        try:
            from geopy.distance import geodesic
            return geodesic(coord1, coord2).kilometers
        except ImportError:
            self.logger.error("Geopy library not installed. Cannot calculate distance.")
            return 0.0
        except Exception as e:
            self.logger.error(f"Error calculating distance: {e}")
            return 0.0
    
    def add_coordinates_to_articles(self, articles: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """
        Add coordinates to articles based on location.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Articles with added coordinates
        """
        for article in articles:
            location = article.get('location')
            if location:
                coordinates = self.get_location_coordinates(location)
                if coordinates:
                    article['latitude'] = coordinates[0]
                    article['longitude'] = coordinates[1]
                    article['coordinates_valid'] = self.validate_coordinates(*coordinates)
                else:
                    article['latitude'] = None
                    article['longitude'] = None
                    article['coordinates_valid'] = False
            else:
                article['latitude'] = None
                article['longitude'] = None
                article['coordinates_valid'] = False
        
        return articles
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get geocoder statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'provider': self.provider if hasattr(self, 'provider') else 'none',
            'available': self.geocoder is not None,
            'cache_size': len(self.cache),
            'timeout': self.geo_config.get('timeout', 10),
            'delay': self.geo_config.get('delay', 1),
            'country_code': self.geo_config.get('country_code', 'BD')
        }
    
    def clear_cache(self):
        """Clear geocoding cache."""
        self.cache.clear()
        self.logger.info("Geocoding cache cleared")