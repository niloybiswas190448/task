"""
Helper utilities for Bangladesh Road Accident Analysis.
"""

import re
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import pandas as pd
from urllib.parse import urljoin, urlparse
import hashlib


def setup_logging(name: str, level: str = "INFO") -> logging.Logger:
    """
    Set up logging for a module.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def parse_date(date_str: str) -> Optional[date]:
    """
    Parse date string in various formats.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        Parsed date or None if parsing fails
    """
    if not date_str or not isinstance(date_str, str):
        return None
    
    # Common date formats
    date_formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%d %B %Y',
        '%B %d, %Y',
        '%Y/%m/%d',
        '%d.%m.%Y'
    ]
    
    # Clean the date string
    date_str = date_str.strip()
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    # Try to extract date using regex
    date_patterns = [
        r'(\d{4})-(\d{1,2})-(\d{1,2})',
        r'(\d{1,2})/(\d{1,2})/(\d{4})',
        r'(\d{1,2})-(\d{1,2})-(\d{4})'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                if len(match.group(1)) == 4:  # YYYY-MM-DD format
                    return datetime.strptime(f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}", '%Y-%m-%d').date()
                else:  # DD/MM/YYYY or DD-MM-YYYY format
                    return datetime.strptime(f"{match.group(3)}-{match.group(2).zfill(2)}-{match.group(1).zfill(2)}", '%Y-%m-%d').date()
            except ValueError:
                continue
    
    return None


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep Bengali and English letters, numbers, and basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\–\—\…\।\॥\্\া\ি\ী\ু\ূ\ৃ\ে\ৈ\ো\ৌ\্\ক\খ\গ\ঘ\ঙ\চ\ছ\জ\ঝ\ঞ\ট\ঠ\ড\ঢ\ণ\ত\থ\দ\ধ\ন\প\ফ\ব\ভ\ম\য\র\ল\শ\ষ\স\হ\ড়\ঢ়\য়\ৎ]', '', text)
    
    return text.strip()


def extract_numbers(text: str) -> List[int]:
    """
    Extract numbers from text.
    
    Args:
        text: Text to extract numbers from
        
    Returns:
        List of extracted numbers
    """
    if not text:
        return []
    
    # Find all numbers in the text
    numbers = re.findall(r'\d+', text)
    return [int(num) for num in numbers]


def extract_location(text: str) -> Optional[str]:
    """
    Extract location names from text.
    
    Args:
        text: Text to extract location from
        
    Returns:
        Extracted location or None
    """
    if not text:
        return None
    
    # Common Bangladeshi cities and districts
    locations = [
        'Dhaka', 'Chittagong', 'Sylhet', 'Rajshahi', 'Khulna', 'Barisal', 'Rangpur', 'Mymensingh',
        'Comilla', 'Narayanganj', 'Gazipur', 'Tangail', 'Bogra', 'Kushtia', 'Jessore', 'Faridpur',
        'Pabna', 'Dinajpur', 'Noakhali', 'Feni', 'Cox\'s Bazar', 'Chandpur', 'Lakshmipur',
        'ঢাকা', 'চট্টগ্রাম', 'সিলেট', 'রাজশাহী', 'খুলনা', 'বরিশাল', 'রংপুর', 'ময়মনসিংহ'
    ]
    
    text_lower = text.lower()
    
    for location in locations:
        if location.lower() in text_lower:
            return location
    
    return None


def generate_article_id(url: str, title: str) -> str:
    """
    Generate a unique ID for an article.
    
    Args:
        url: Article URL
        title: Article title
        
    Returns:
        Unique article ID
    """
    content = f"{url}{title}"
    return hashlib.md5(content.encode()).hexdigest()


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_dataframe(df: pd.DataFrame, filepath: Union[str, Path], format: str = 'csv') -> None:
    """
    Save DataFrame to file.
    
    Args:
        df: DataFrame to save
        filepath: Output file path
        format: File format (csv, json, excel)
    """
    filepath = Path(filepath)
    ensure_directory(filepath.parent)
    
    if format.lower() == 'csv':
        df.to_csv(filepath, index=False, encoding='utf-8')
    elif format.lower() == 'json':
        df.to_json(filepath, orient='records', indent=2, force_ascii=False)
    elif format.lower() == 'excel':
        df.to_excel(filepath, index=False)
    else:
        raise ValueError(f"Unsupported format: {format}")


def load_dataframe(filepath: Union[str, Path], format: str = 'csv') -> pd.DataFrame:
    """
    Load DataFrame from file.
    
    Args:
        filepath: Input file path
        format: File format (csv, json, excel)
        
    Returns:
        Loaded DataFrame
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    if format.lower() == 'csv':
        return pd.read_csv(filepath, encoding='utf-8')
    elif format.lower() == 'json':
        return pd.read_json(filepath, orient='records')
    elif format.lower() == 'excel':
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported format: {format}")


def is_valid_url(url: str) -> bool:
    """
    Check if URL is valid.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def normalize_url(url: str, base_url: str) -> str:
    """
    Normalize URL by joining with base URL if relative.
    
    Args:
        url: URL to normalize
        base_url: Base URL
        
    Returns:
        Normalized URL
    """
    if not url:
        return base_url
    
    if url.startswith('http'):
        return url
    else:
        return urljoin(base_url, url)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks.
    
    Args:
        lst: List to split
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get value from dictionary.
    
    Args:
        dictionary: Dictionary to search
        key: Key to look for
        default: Default value if key not found
        
    Returns:
        Value or default
    """
    return dictionary.get(key, default) if dictionary else default