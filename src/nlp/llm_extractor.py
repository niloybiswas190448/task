"""
LLM-based data extraction for accident analysis.
"""

import json
import time
from typing import Dict, Any, Optional, List
import logging

from ..utils.config import config
from ..utils.helpers import setup_logging


class LLMExtractor:
    """LLM-based data extraction for accident articles."""
    
    def __init__(self):
        """Initialize LLM extractor."""
        self.logger = setup_logging("nlp.llm_extractor")
        self.llm_config = config.get_llm_config()
        
        # Initialize LLM client
        self.client = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM client based on configuration."""
        provider = self.llm_config.get('provider', 'openai')
        
        if provider == 'openai':
            try:
                import openai
                api_key = self.llm_config.get('api_key')
                if not api_key:
                    self.logger.warning("OpenAI API key not found. LLM extraction will be disabled.")
                    return
                
                self.client = openai.OpenAI(api_key=api_key)
                self.model = self.llm_config.get('model', 'gpt-3.5-turbo')
                self.temperature = self.llm_config.get('temperature', 0.1)
                self.max_tokens = self.llm_config.get('max_tokens', 1000)
                
            except ImportError:
                self.logger.error("OpenAI library not installed. Install with: pip install openai")
                return
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {e}")
                return
        
        elif provider == 'huggingface':
            try:
                from transformers import pipeline
                model_name = self.llm_config.get('model', 'gpt2')
                self.client = pipeline('text-generation', model=model_name)
                
            except ImportError:
                self.logger.error("Transformers library not installed. Install with: pip install transformers")
                return
            except Exception as e:
                self.logger.error(f"Failed to initialize HuggingFace client: {e}")
                return
        
        else:
            self.logger.warning(f"Unsupported LLM provider: {provider}")
            return
        
        self.logger.info(f"LLM extractor initialized with provider: {provider}")
    
    def extract_accident_data(self, article_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract structured accident data using LLM.
        
        Args:
            article_text: Article text to analyze
            
        Returns:
            Extracted data dictionary or None if failed
        """
        if not self.client or not article_text:
            return None
        
        try:
            # Prepare prompt
            prompt = self._prepare_extraction_prompt(article_text)
            
            # Make LLM request
            response = self._make_llm_request(prompt)
            
            if not response:
                return None
            
            # Parse response
            extracted_data = self._parse_llm_response(response)
            
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Error in LLM extraction: {e}")
            return None
    
    def _prepare_extraction_prompt(self, text: str) -> str:
        """
        Prepare extraction prompt for LLM.
        
        Args:
            text: Article text
            
        Returns:
            Formatted prompt
        """
        base_prompt = self.llm_config.get('extraction_prompt', '')
        
        # Truncate text if too long
        max_length = self.llm_config.get('max_article_length', 10000)
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        # Format prompt
        prompt = base_prompt.format(text=text)
        
        return prompt
    
    def _make_llm_request(self, prompt: str) -> Optional[str]:
        """
        Make request to LLM.
        
        Args:
            prompt: Input prompt
            
        Returns:
            LLM response or None if failed
        """
        try:
            if hasattr(self.client, 'chat') and hasattr(self.client.chat, 'completions'):
                # OpenAI API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that extracts structured data from news articles about road accidents."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content
                
            elif hasattr(self.client, '__call__'):
                # HuggingFace pipeline
                response = self.client(prompt, max_length=200, num_return_sequences=1)
                return response[0]['generated_text']
                
            else:
                self.logger.error("Unsupported LLM client type")
                return None
                
        except Exception as e:
            self.logger.error(f"LLM request failed: {e}")
            return None
    
    def _parse_llm_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse LLM response to extract structured data.
        
        Args:
            response: LLM response text
            
        Returns:
            Parsed data dictionary or None if failed
        """
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                # Validate and clean data
                cleaned_data = self._clean_extracted_data(data)
                return cleaned_data
            
            else:
                self.logger.warning("No JSON found in LLM response")
                return None
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON from LLM response: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing LLM response: {e}")
            return None
    
    def _clean_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and validate extracted data.
        
        Args:
            data: Raw extracted data
            
        Returns:
            Cleaned data
        """
        cleaned = {}
        
        # Clean accident date
        if 'accident_date' in data:
            date_str = data['accident_date']
            if date_str and date_str != 'null':
                cleaned['accident_date'] = date_str
        
        # Clean location
        if 'location' in data:
            location = data['location']
            if location and location != 'null':
                cleaned['location'] = location
        
        # Clean numeric values
        for field in ['deaths', 'injuries']:
            if field in data:
                try:
                    value = int(data[field])
                    cleaned[field] = value
                except (ValueError, TypeError):
                    cleaned[field] = 0
        
        # Clean vehicle types
        if 'vehicles' in data:
            vehicles = data['vehicles']
            if isinstance(vehicles, list):
                cleaned['vehicles'] = [v for v in vehicles if v and v != 'null']
            else:
                cleaned['vehicles'] = []
        
        # Clean cause
        if 'cause' in data:
            cause = data['cause']
            if cause and cause != 'null':
                cleaned['cause'] = cause
        
        # Clean severity
        if 'severity' in data:
            severity = data['severity']
            if severity and severity != 'null':
                cleaned['severity'] = severity
        
        # Clean area type
        if 'area_type' in data:
            area_type = data['area_type']
            if area_type and area_type != 'null':
                cleaned['area_type'] = area_type
        
        return cleaned
    
    def enhance_article_data(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance article data with LLM extraction.
        
        Args:
            article_data: Original article data
            
        Returns:
            Enhanced article data
        """
        if not self.client:
            return article_data
        
        # Combine title and content for analysis
        title = article_data.get('title', '')
        content = article_data.get('content', '')
        full_text = f"{title} {content}"
        
        # Extract data using LLM
        llm_data = self.extract_accident_data(full_text)
        
        if llm_data:
            # Merge LLM data with existing data
            # LLM data takes precedence for extracted fields
            for key, value in llm_data.items():
                if value is not None and value != '':
                    article_data[f'llm_{key}'] = value
            
            # Add LLM processing flag
            article_data['llm_processed'] = True
        else:
            article_data['llm_processed'] = False
        
        return article_data
    
    def batch_process_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple articles with LLM.
        
        Args:
            articles: List of article data
            
        Returns:
            List of enhanced article data
        """
        if not self.client:
            return articles
        
        processed_articles = []
        
        for i, article in enumerate(articles):
            try:
                enhanced_article = self.enhance_article_data(article)
                processed_articles.append(enhanced_article)
                
                # Add delay between requests to respect rate limits
                if i < len(articles) - 1:
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Error processing article {i}: {e}")
                processed_articles.append(article)
        
        return processed_articles
    
    def is_available(self) -> bool:
        """
        Check if LLM extraction is available.
        
        Returns:
            True if LLM is available, False otherwise
        """
        return self.client is not None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get LLM extractor statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'provider': self.llm_config.get('provider', 'unknown'),
            'model': self.llm_config.get('model', 'unknown'),
            'available': self.is_available(),
            'temperature': self.llm_config.get('temperature', 0.1),
            'max_tokens': self.llm_config.get('max_tokens', 1000)
        }