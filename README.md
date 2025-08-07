# Bangladesh Road Accident Data Analysis

A comprehensive Python project to collect and analyze road accident data in Bangladesh from major news sources using web scraping, NLP, and LLM integration.

## Features

- **Web Scraping**: Collects accident news from major Bangladeshi newspapers
- **NLP Processing**: Extracts structured data from article text
- **LLM Integration**: Uses OpenAI/LangChain for improved data extraction
- **Geolocation**: Converts locations to coordinates for mapping
- **Data Analysis**: Comprehensive trend analysis and visualization
- **Ethical Scraping**: Respects robots.txt and implements rate limiting

## News Sources

- The Daily Star
- Prothom Alo
- Dhaka Tribune
- BDNews24

## Project Structure

```
bangladesh_accident_analysis/
├── src/
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base_scraper.py
│   │   ├── daily_star.py
│   │   ├── prothom_alo.py
│   │   ├── dhaka_tribune.py
│   │   └── bdnews24.py
│   ├── nlp/
│   │   ├── __init__.py
│   │   ├── text_processor.py
│   │   ├── llm_extractor.py
│   │   └── data_extractor.py
│   ├── geolocation/
│   │   ├── __init__.py
│   │   └── geocoder.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── data_cleaner.py
│   │   ├── trend_analyzer.py
│   │   └── visualizer.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       └── helpers.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── results/
├── notebooks/
├── config/
│   └── settings.yaml
├── main.py
├── requirements.txt
└── README.md
```

## Setup

1. **Clone and navigate to the project**:
   ```bash
   cd bangladesh_accident_analysis
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   export GOOGLE_MAPS_API_KEY="your_google_maps_api_key_here"  # Optional
   ```

4. **Download NLTK data**:
   ```python
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

## Usage

### Basic Usage

```python
from main import AccidentAnalyzer

# Initialize the analyzer
analyzer = AccidentAnalyzer()

# Collect data from all sources
analyzer.collect_data()

# Process and analyze the data
analyzer.analyze_data()

# Generate visualizations
analyzer.generate_visualizations()
```

### Command Line Usage

```bash
# Collect data from all sources
python main.py --collect

# Analyze collected data
python main.py --analyze

# Generate visualizations
python main.py --visualize

# Run complete pipeline
python main.py --full
```

## Configuration

Edit `config/settings.yaml` to customize:
- Scraping parameters (delays, timeouts)
- News source URLs
- LLM settings
- Analysis parameters

## Data Output

The project generates:
- Raw scraped articles (CSV)
- Processed accident data (CSV)
- Interactive visualizations (HTML)
- Static plots (PNG)
- Analysis reports (JSON)

## Ethical Considerations

- Respects robots.txt files
- Implements rate limiting (2-5 second delays)
- Uses proper user agents
- Handles errors gracefully
- Stores only publicly available data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Disclaimer

This project is for educational and research purposes. Always respect website terms of service and implement ethical scraping practices.