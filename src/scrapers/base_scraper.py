"""
Base scraper class for news sources.
"""

import time
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from bs4 import BeautifulSoup
import logging
from fake_useragent import UserAgent

from ..utils.config import config
from ..utils.helpers import setup_logging, parse_date, clean_text, generate_article_id, normalize_url


class BaseScraper(ABC):
    """Base class for all news scrapers."""
    
    def __init__(self, source_name: str, base_url: str):
        """
        Initialize base scraper.
        
        Args:
            source_name: Name of the news source
            base_url: Base URL of the news source
        """
        self.source_name = source_name
        self.base_url = base_url
        self.logger = setup_logging(f"scraper.{source_name.lower()}")
        
        # Get scraping configuration
        scraping_config = config.get_scraping_config()
        self.request_delay = scraping_config.get('request_delay', 3)
        self.timeout = scraping_config.get('timeout', 30)
        self.max_retries = scraping_config.get('max_retries', 3)
        
        # Initialize session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': UserAgent().random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Store scraped articles
        self.articles = []
        
    def make_request(self, url: str, retries: int = None) -> Optional[requests.Response]:
        """
        Make HTTP request with retry logic.
        
        Args:
            url: URL to request
            retries: Number of retries (uses config default if None)
            
        Returns:
            Response object or None if failed
        """
        if retries is None:
            retries = self.max_retries
            
        for attempt in range(retries + 1):
            try:
                self.logger.info(f"Requesting: {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                # Respect rate limiting
                time.sleep(self.request_delay)
                
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < retries:
                    time.sleep(self.request_delay * (attempt + 1))  # Exponential backoff
                else:
                    self.logger.error(f"Failed to fetch {url} after {retries + 1} attempts")
                    return None
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """
        Parse HTML content.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html_content, 'html.parser')
    
    def extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract article links from search results page.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of article URLs
        """
        links = []
        
        # This is a generic implementation - subclasses should override
        for link in soup.find_all('a', href=True):
            href = link['href']
            if self._is_article_link(href):
                full_url = normalize_url(href, self.base_url)
                if full_url not in links:
                    links.append(full_url)
        
        return links
    
    def _is_article_link(self, href: str) -> bool:
        """
        Check if a link is likely an article link.
        
        Args:
            href: Link href
            
        Returns:
            True if likely an article link
        """
        # Common patterns for article links
        article_patterns = [
            '/news/',
            '/article/',
            '/story/',
            '/report/',
            '/accident/',
            '/road-accident/',
            '/traffic/'
        ]
        
        href_lower = href.lower()
        return any(pattern in href_lower for pattern in article_patterns)
    
    def extract_article_data(self, soup: BeautifulSoup, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract article data from parsed HTML.
        
        Args:
            soup: BeautifulSoup object of the article page
            url: Article URL
            
        Returns:
            Dictionary with article data or None if extraction fails
        """
        try:
            # Extract title
            title = self._extract_title(soup)
            if not title:
                return None
            
            # Extract content
            content = self._extract_content(soup)
            if not content:
                return None
            
            # Extract date
            article_date = self._extract_date(soup)
            
            # Generate article ID
            article_id = generate_article_id(url, title)
            
            article_data = {
                'id': article_id,
                'source': self.source_name,
                'url': url,
                'title': clean_text(title),
                'content': clean_text(content),
                'date': article_date,
                'scraped_at': datetime.now().isoformat()
            }
            
            return article_data
            
        except Exception as e:
            self.logger.error(f"Error extracting article data from {url}: {e}")
            return None
    
    @abstractmethod
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract article title.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Article title or None
        """
        pass
    
    @abstractmethod
    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract article content.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Article content or None
        """
        pass
    
    @abstractmethod
    def _extract_date(self, soup: BeautifulSoup) -> Optional[date]:
        """
        Extract article date.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Article date or None
        """
        pass
    
    def scrape_articles(self, max_pages: int = None) -> List[Dict[str, Any]]:
        """
        Scrape articles from the news source.
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of scraped articles
        """
        if max_pages is None:
            max_pages = config.get('scraping.max_pages_per_source', 50)
        
        self.logger.info(f"Starting to scrape articles from {self.source_name}")
        
        page = 1
        total_articles = 0
        
        while page <= max_pages:
            try:
                # Get search results page
                search_url = self._get_search_url(page)
                response = self.make_request(search_url)
                
                if not response:
                    self.logger.warning(f"Failed to fetch page {page}")
                    break
                
                soup = self.parse_html(response.text)
                
                # Extract article links
                article_links = self.extract_article_links(soup)
                
                if not article_links:
                    self.logger.info(f"No more articles found on page {page}")
                    break
                
                self.logger.info(f"Found {len(article_links)} articles on page {page}")
                
                # Scrape each article
                for link in article_links:
                    article_data = self._scrape_single_article(link)
                    if article_data:
                        self.articles.append(article_data)
                        total_articles += 1
                
                page += 1
                
            except Exception as e:
                self.logger.error(f"Error scraping page {page}: {e}")
                break
        
        self.logger.info(f"Scraped {total_articles} articles from {self.source_name}")
        return self.articles
    
    def _scrape_single_article(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single article.
        
        Args:
            url: Article URL
            
        Returns:
            Article data or None if failed
        """
        try:
            response = self.make_request(url)
            if not response:
                return None
            
            soup = self.parse_html(response.text)
            return self.extract_article_data(soup, url)
            
        except Exception as e:
            self.logger.error(f"Error scraping article {url}: {e}")
            return None
    
    @abstractmethod
    def _get_search_url(self, page: int) -> str:
        """
        Get search URL for a specific page.
        
        Args:
            page: Page number
            
        Returns:
            Search URL
        """
        pass
    
    def get_articles(self) -> List[Dict[str, Any]]:
        """
        Get all scraped articles.
        
        Returns:
            List of articles
        """
        return self.articles
    
    def clear_articles(self):
        """Clear stored articles."""
        self.articles = []