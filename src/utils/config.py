"""
Configuration management for Bangladesh Road Accident Analysis.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for the accident analysis project."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to configuration file. If None, uses default.
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Override with environment variables
        config = self._override_with_env(config)
        
        return config
    
    def _override_with_env(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Override configuration with environment variables."""
        # LLM settings
        if os.getenv('OPENAI_API_KEY'):
            config['llm']['api_key'] = os.getenv('OPENAI_API_KEY')
        
        if os.getenv('GOOGLE_MAPS_API_KEY'):
            config['geolocation']['google_api_key'] = os.getenv('GOOGLE_MAPS_API_KEY')
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'scraping.request_delay')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_scraping_config(self) -> Dict[str, Any]:
        """Get scraping configuration."""
        return self.get('scraping', {})
    
    def get_news_sources(self) -> Dict[str, Any]:
        """Get news sources configuration."""
        return self.get('news_sources', {})
    
    def get_nlp_config(self) -> Dict[str, Any]:
        """Get NLP configuration."""
        return self.get('nlp', {})
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return self.get('llm', {})
    
    def get_geolocation_config(self) -> Dict[str, Any]:
        """Get geolocation configuration."""
        return self.get('geolocation', {})
    
    def get_analysis_config(self) -> Dict[str, Any]:
        """Get analysis configuration."""
        return self.get('analysis', {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration."""
        return self.get('output', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get('logging', {})
    
    def reload(self):
        """Reload configuration from file."""
        self._config = self._load_config()
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access."""
        return self.get(key)
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in configuration."""
        return self.get(key) is not None


# Global configuration instance
config = Config()