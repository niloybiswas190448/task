"""
Text processing utilities for accident analysis.
"""

import re
from typing import List, Dict, Any, Optional, Set
from datetime import date
import logging

from ..utils.config import config
from ..utils.helpers import setup_logging, clean_text, extract_numbers, extract_location


class TextProcessor:
    """Text processing utilities for accident articles."""
    
    def __init__(self):
        """Initialize text processor."""
        self.logger = setup_logging("nlp.text_processor")
        self.nlp_config = config.get_nlp_config()
        
        # Load accident keywords
        self.accident_keywords = set(self.nlp_config.get('accident_keywords', []))
        
        # Vehicle type keywords
        self.vehicle_keywords = {
            'bus': ['bus', 'বাস', 'coach', 'minibus'],
            'truck': ['truck', 'ট্রাক', 'lorry', 'pickup'],
            'car': ['car', 'গাড়ি', 'sedan', 'suv', 'jeep'],
            'motorcycle': ['motorcycle', 'মোটরসাইকেল', 'bike', 'scooter'],
            'rickshaw': ['rickshaw', 'রিকশা', 'auto-rickshaw', 'tuk-tuk'],
            'bicycle': ['bicycle', 'সাইকেল', 'bike', 'cycle'],
            'train': ['train', 'ট্রেন', 'railway'],
            'boat': ['boat', 'নৌকা', 'ferry', 'launch']
        }
        
        # Cause keywords
        self.cause_keywords = {
            'overspeeding': ['overspeeding', 'speed', 'fast', 'দুর্ঘটনা', 'গতি'],
            'fog': ['fog', 'mist', 'visibility', 'কুয়াশা'],
            'road_condition': ['road condition', 'pothole', 'bad road', 'রাস্তার অবস্থা'],
            'driver_fault': ['driver fault', 'driver error', 'negligence', 'চালকের ভুল'],
            'mechanical_failure': ['mechanical failure', 'brake failure', 'engine failure'],
            'weather': ['rain', 'storm', 'weather', 'বৃষ্টি', 'ঝড়'],
            'overloading': ['overloading', 'overload', 'excess passengers'],
            'alcohol': ['alcohol', 'drunk', 'intoxicated', 'মদ']
        }
        
        # Severity keywords
        self.severity_keywords = {
            'fatal': ['fatal', 'death', 'dead', 'মৃত্যু', 'নিহত'],
            'major': ['major', 'serious', 'critical', 'গুরুতর'],
            'minor': ['minor', 'slight', 'small', 'ছোট']
        }
        
        # Area type keywords
        self.area_keywords = {
            'urban': ['city', 'urban', 'town', 'ঢাকা', 'শহর'],
            'rural': ['rural', 'village', 'countryside', 'গ্রাম', 'পল্লী']
        }
    
    def is_accident_article(self, text: str) -> bool:
        """
        Check if text is about a road accident.
        
        Args:
            text: Text to check
            
        Returns:
            True if about accident, False otherwise
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check for accident keywords
        for keyword in self.accident_keywords:
            if keyword.lower() in text_lower:
                return True
        
        return False
    
    def extract_vehicle_types(self, text: str) -> List[str]:
        """
        Extract vehicle types mentioned in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of vehicle types found
        """
        if not text:
            return []
        
        text_lower = text.lower()
        found_vehicles = []
        
        for vehicle_type, keywords in self.vehicle_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    found_vehicles.append(vehicle_type)
                    break
        
        return list(set(found_vehicles))  # Remove duplicates
    
    def extract_cause(self, text: str) -> Optional[str]:
        """
        Extract probable cause of accident.
        
        Args:
            text: Text to analyze
            
        Returns:
            Probable cause or None
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Find the most likely cause based on keyword frequency
        cause_scores = {}
        
        for cause, keywords in self.cause_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1
            if score > 0:
                cause_scores[cause] = score
        
        if cause_scores:
            # Return the cause with highest score
            return max(cause_scores, key=cause_scores.get)
        
        return None
    
    def extract_severity(self, text: str) -> str:
        """
        Extract accident severity.
        
        Args:
            text: Text to analyze
            
        Returns:
            Severity level (fatal, major, minor)
        """
        if not text:
            return 'unknown'
        
        text_lower = text.lower()
        
        # Check for severity keywords
        for severity, keywords in self.severity_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return severity
        
        return 'unknown'
    
    def extract_area_type(self, text: str) -> str:
        """
        Extract area type (urban/rural).
        
        Args:
            text: Text to analyze
            
        Returns:
            Area type (urban, rural, unknown)
        """
        if not text:
            return 'unknown'
        
        text_lower = text.lower()
        
        # Check for area keywords
        for area_type, keywords in self.area_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return area_type
        
        return 'unknown'
    
    def extract_deaths_and_injuries(self, text: str) -> Dict[str, int]:
        """
        Extract number of deaths and injuries.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with deaths and injuries counts
        """
        if not text:
            return {'deaths': 0, 'injuries': 0}
        
        # Extract all numbers from text
        numbers = extract_numbers(text)
        
        # Look for death-related patterns
        death_patterns = [
            r'(\d+)\s*(?:people|person|persons)\s*(?:died|killed|dead|নিহত)',
            r'(?:died|killed|dead|নিহত)\s*(\d+)\s*(?:people|person|persons)',
            r'(\d+)\s*(?:deaths|fatalities)',
            r'death\s*toll\s*(\d+)'
        ]
        
        deaths = 0
        for pattern in death_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                deaths = max(deaths, max(int(match) for match in matches))
        
        # Look for injury-related patterns
        injury_patterns = [
            r'(\d+)\s*(?:people|person|persons)\s*(?:injured|wounded|আহত)',
            r'(?:injured|wounded|আহত)\s*(\d+)\s*(?:people|person|persons)',
            r'(\d+)\s*(?:injuries|wounded)'
        ]
        
        injuries = 0
        for pattern in injury_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                injuries = max(injuries, max(int(match) for match in matches))
        
        return {
            'deaths': deaths,
            'injuries': injuries
        }
    
    def extract_accident_date(self, text: str) -> Optional[date]:
        """
        Extract accident date from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Accident date or None
        """
        if not text:
            return None
        
        # Common date patterns in accident reports
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
            r'(\d{1,2})\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Try to parse the first match
                    match = matches[0]
                    if len(match) == 3:
                        if len(match[0]) == 4:  # YYYY-MM-DD format
                            return date(int(match[0]), int(match[1]), int(match[2]))
                        else:  # DD/MM/YYYY format
                            return date(int(match[2]), int(match[1]), int(match[0]))
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def process_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a complete article and extract structured data.
        
        Args:
            article_data: Article data dictionary
            
        Returns:
            Enhanced article data with extracted information
        """
        if not article_data:
            return article_data
        
        title = article_data.get('title', '')
        content = article_data.get('content', '')
        full_text = f"{title} {content}"
        
        # Check if it's an accident article
        if not self.is_accident_article(full_text):
            return article_data
        
        # Extract structured data
        extracted_data = {
            'is_accident': True,
            'vehicle_types': self.extract_vehicle_types(full_text),
            'probable_cause': self.extract_cause(full_text),
            'severity': self.extract_severity(full_text),
            'area_type': self.extract_area_type(full_text),
            'accident_date': self.extract_accident_date(full_text),
            'location': extract_location(full_text)
        }
        
        # Extract death and injury counts
        casualty_data = self.extract_deaths_and_injuries(full_text)
        extracted_data.update(casualty_data)
        
        # Update article data
        article_data.update(extracted_data)
        
        return article_data
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get processing statistics.
        
        Returns:
            Dictionary with processing statistics
        """
        return {
            'accident_keywords_count': len(self.accident_keywords),
            'vehicle_types_count': len(self.vehicle_keywords),
            'cause_types_count': len(self.cause_keywords),
            'severity_levels_count': len(self.severity_keywords),
            'area_types_count': len(self.area_keywords)
        }