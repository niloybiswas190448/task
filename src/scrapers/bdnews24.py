"""
BDNews24 news scraper.
"""

from typing import Optional
from datetime import date
from bs4 import BeautifulSoup
import re

from .base_scraper import BaseScraper
from ..utils.helpers import parse_date


class BDNews24Scraper(BaseScraper):
    """Scraper for BDNews24 news website."""
    
    def __init__(self):
        """Initialize BDNews24 scraper."""
        super().__init__(
            source_name="BDNews24",
            base_url="https://bdnews24.com"
        )
    
    def _get_search_url(self, page: int) -> str:
        """
        Get search URL for a specific page.
        
        Args:
            page: Page number
            
        Returns:
            Search URL
        """
        if page == 1:
            return "https://bdnews24.com/search?q=road+accident"
        else:
            return f"https://bdnews24.com/search?q=road+accident&page={page}"
    
    def extract_article_links(self, soup: BeautifulSoup) -> list[str]:
        """
        Extract article links from search results page.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of article URLs
        """
        links = []
        
        # Look for article containers
        article_containers = soup.find_all('div', class_='article-item') or \
                           soup.find_all('div', class_='search-result') or \
                           soup.find_all('article') or \
                           soup.find_all('div', class_='story-item') or \
                           soup.find_all('div', class_='news-item') or \
                           soup.find_all('div', class_='item')
        
        for container in article_containers:
            # Find link within container
            link_tag = container.find('a', href=True)
            if link_tag:
                href = link_tag['href']
                if self._is_article_link(href):
                    full_url = self._normalize_url(href)
                    if full_url not in links:
                        links.append(full_url)
        
        # Fallback: look for any links that match article patterns
        if not links:
            for link in soup.find_all('a', href=True):
                href = link['href']
                if self._is_article_link(href):
                    full_url = self._normalize_url(href)
                    if full_url not in links:
                        links.append(full_url)
        
        return links
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract article title.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Article title or None
        """
        # Try multiple selectors for title
        title_selectors = [
            'h1.article-title',
            'h1.title',
            '.article-header h1',
            'h1',
            '.headline',
            '.title',
            '.story-title',
            '.news-title',
            '.item-title'
        ]
        
        for selector in title_selectors:
            title_tag = soup.select_one(selector)
            if title_tag and title_tag.get_text().strip():
                return title_tag.get_text().strip()
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract article content.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Article content or None
        """
        # Try multiple selectors for content
        content_selectors = [
            '.article-content',
            '.article-body',
            '.content',
            '.story-content',
            '.article-text',
            '.body-content',
            '.story-body',
            '.news-content',
            '.item-content'
        ]
        
        for selector in content_selectors:
            content_tag = soup.select_one(selector)
            if content_tag:
                # Remove unwanted elements
                for unwanted in content_tag.find_all(['script', 'style', 'nav', 'header', 'footer']):
                    unwanted.decompose()
                
                # Extract text from paragraphs
                paragraphs = content_tag.find_all('p')
                if paragraphs:
                    content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if content:
                        return content
        
        # Fallback: look for any paragraph content
        paragraphs = soup.find_all('p')
        if paragraphs:
            content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            if len(content) > 100:  # Ensure minimum content length
                return content
        
        return None
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[date]:
        """
        Extract article date.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Article date or None
        """
        # Try multiple selectors for date
        date_selectors = [
            '.publish-date',
            '.article-date',
            '.date',
            '.time',
            '.published-date',
            'time',
            '.meta-date',
            '.story-date',
            '.news-date',
            '.item-date'
        ]
        
        for selector in date_selectors:
            date_tag = soup.select_one(selector)
            if date_tag:
                date_text = date_tag.get_text().strip()
                if date_text:
                    parsed_date = parse_date(date_text)
                    if parsed_date:
                        return parsed_date
        
        # Look for date in meta tags
        meta_date = soup.find('meta', property='article:published_time')
        if meta_date and meta_date.get('content'):
            parsed_date = parse_date(meta_date['content'])
            if parsed_date:
                return parsed_date
        
        return None
    
    def _normalize_url(self, href: str) -> str:
        """
        Normalize URL for BDNews24.
        
        Args:
            href: Relative or absolute URL
            
        Returns:
            Normalized absolute URL
        """
        if href.startswith('http'):
            return href
        elif href.startswith('/'):
            return f"{self.base_url}{href}"
        else:
            return f"{self.base_url}/{href}"
    
    def _is_article_link(self, href: str) -> bool:
        """
        Check if a link is likely an article link for BDNews24.
        
        Args:
            href: Link href
            
        Returns:
            True if likely an article link
        """
        # BDNews24 specific patterns
        article_patterns = [
            '/news/',
            '/article/',
            '/story/',
            '/report/',
            '/accident/',
            '/road-accident/',
            '/traffic/',
            '/bangladesh/',
            '/country/',
            '/national/',
            '/item/'
        ]
        
        href_lower = href.lower()
        
        # Must contain one of the article patterns
        if not any(pattern in href_lower for pattern in article_patterns):
            return False
        
        # Exclude non-article patterns
        exclude_patterns = [
            '/tag/',
            '/author/',
            '/category/',
            '/section/',
            '/page/',
            '/search',
            '/login',
            '/register',
            '/advertisement',
            '/ad',
            '/subscribe',
            '/video/',
            '/photo/'
        ]
        
        if any(pattern in href_lower for pattern in exclude_patterns):
            return False
        
        return True