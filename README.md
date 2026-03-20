# 🔍 URL Scanner & Website Opportunity Finder

A powerful web scraping and analysis tool built with Streamlit that helps identify websites with poor SEO/UI that may need redesign services. This tool can search for websites using Google Search API or analyze specific URLs for various opportunities.

## 🚀 Features

### 📊 Dual Mode Operation
- **🔍 Finder Mode**: Search for websites using Google Search with custom queries
- **📋 URL Scanner Mode**: Analyze specific URLs directly

### 🎯 Analysis Capabilities
- **SEO Analysis**: Meta tags, headings, structured data, page speed
- **UI/UX Assessment**: Visual design analysis, mobile responsiveness
- **Technology Detection**: Identify frameworks, CMS, and analytics tools
- **Content Analysis**: Duplicate content, readability, keyword density
- **Performance Metrics**: Page speed, image optimization, loading times

### 🌍 Multi-Provider Support
- Google Search API
- SerpApi
- Serper.dev
- Brave Search API
- Bing Search API

### 📤 Export Options
- CSV exports for leads and analysis results
- Excel exports with detailed website information
- JSON history files for tracking

## 📋 Prerequisites

- Python 3.8+
- Chrome/Chromium browser (for Selenium WebDriver)
- Google ChromeDriver (auto-managed)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd URL-Scanner
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up configuration**
   - Create a `config.py` file (see Configuration section)
   - Set up API keys for search providers

## 🔧 Configuration

### 1. Create `config.py` file

Create a file named `config.py` in the root directory with the following structure:

```python
# API Keys
GOOGLE_API_KEY = "your_google_api_key_here"
GOOGLE_CSE_ID = "your_google_cse_id_here"
SERPAPI_KEY = "your_serpapi_key_here"
SERPER_DEV_KEY = "your_serper_dev_key_here"
BRAVE_API_KEY = "your_brave_api_key_here"
BING_API_KEY = "your_bing_api_key_here"

# Search Settings
MAX_RESULTS_PER_QUERY = 50
REQUEST_DELAY = 2  # seconds between requests
MAX_CONCURRENT_REQUESTS = 5

# Analysis Settings
ENABLE_SEO_ANALYSIS = True
ENABLE_UI_ANALYSIS = True
ENABLE_PERFORMANCE_ANALYSIS = True
PAGE_SPEED_THRESHOLD = 50  # minimum score

# Export Settings
EXPORT_FORMAT = "csv"  # csv, excel, json
HISTORY_RETENTION_DAYS = 30
```

### 2. API Keys Setup

#### Google Search API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable "Custom Search API"
4. Create credentials (API Key)
5. Set up [Custom Search Engine](https://cse.google.com/cse/)
6. Get your CSE ID

#### Alternative Search APIs
- **SerpApi**: Get key from [serpapi.com](https://serpapi.com/)
- **Serper.dev**: Get key from [serper.dev](https://serper.dev/)
- **Brave Search**: Get key from [brave.com/search/api](https://brave.com/search/api/)
- **Bing Search**: Get key from [Microsoft Azure](https://azure.microsoft.com/en-us/services/cognitive-services/bing-web-search-api/)

## 🚀 Running the Application

### Method 1: Using Streamlit (Recommended)
```bash
streamlit run app.py
```

### Method 2: Using the main script
```bash
python main.py
```

The application will start in your default browser at `http://localhost:8501`

## 📖 Usage Guide

### 🔍 Finder Mode

1. **Select Template**: Choose from pre-built search templates or use custom
2. **Configure Search Query**: Modify the search query as needed
3. **Set Country/Region**: Filter results by specific country
4. **Configure Filters**: Set minimum criteria for opportunities
5. **Run Search**: Click "Start Search" to find websites

### 📋 URL Scanner Mode

1. **Enter URLs**: Input one URL per line in the text area
2. **Configure Analysis**: Select which analyses to perform
3. **Set Filters**: Configure opportunity detection criteria
4. **Run Analysis**: Click "Start Analysis" to process URLs

### ⚙️ Settings & Filters

#### Search Filters
- **Minimum Page Speed**: Filter by Google PageSpeed score
- **Mobile Friendly**: Only include mobile-responsive sites
- **Has SSL**: Filter by HTTPS availability
- **Age Filter**: Filter by website age/last updated

#### Analysis Options
- **SEO Analysis**: Meta tags, headings, structured data
- **UI Analysis**: Visual design, layout assessment
- **Performance**: Loading speed, optimization
- **Technology Stack**: Framework and CMS detection

## 📊 Understanding Results

### Opportunity Scoring
- **🔴 High Priority**: Poor SEO, outdated design, slow loading
- **🟡 Medium Priority**: Some issues, moderate potential
- **🟢 Low Priority**: Well-optimized, limited opportunity

### Export Formats
- **CSV**: Standard format for spreadsheet applications
- **Excel**: Rich format with multiple sheets
- **JSON**: Machine-readable format for integration

## 🗂️ File Structure

```
URL-Scanner/
├── app.py                      # Main Streamlit application
├── main.py                     # Alternative entry point
├── config.py                   # Configuration file (create this)
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore file
├── found_links_history.json     # Search history
├── scanned_sites_history.json  # Analysis history
├── website_leads.xlsx          # Exported leads (Excel)
└── website_leads_with_contacts.csv  # Exported leads (CSV)
```

## 🔒 Security & Privacy

- **Local Processing**: All analysis happens locally on your machine
- **API Keys**: Store securely in config.py, never share
- **Data Storage**: History files stored locally, can be deleted
- **Browser Automation**: Uses Selenium for accurate analysis

## 🛠️ Troubleshooting

### Common Issues

1. **ChromeDriver Issues**
   ```bash
   # Update ChromeDriver automatically
   webdriver-manager chrome
   ```

2. **API Rate Limits**
   - Increase `REQUEST_DELAY` in config.py
   - Use multiple API providers
   - Reduce concurrent requests

3. **Memory Issues**
   - Reduce `MAX_RESULTS_PER_QUERY`
   - Clear history files periodically
   - Close unused browser tabs

4. **SSL Certificate Errors**
   ```bash
   # Install certificates (macOS)
   /Applications/Python\ 3.x/Install\ Certificates.command
   ```

### Performance Optimization

- **Concurrent Processing**: Adjust `MAX_CONCURRENT_REQUESTS`
- **Caching**: Enable result caching in config
- **Selective Analysis**: Disable unnecessary analysis types

## 📝 Development

### Adding New Search Providers
1. Implement search function in `app.py`
2. Add API key to `config.py`
3. Update provider selection UI

### Custom Analysis Modules
1. Create analysis function
2. Add to analysis pipeline
3. Update results display

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check this README
2. Review the code comments
3. Check existing issues
4. Create new issue with detailed description

## 🔄 Updates

- **Version 1.0**: Initial release with basic scanning
- **Version 2.0**: Added multi-provider support
- **Version 3.0**: Enhanced UI and analysis features

---

**⚠️ Disclaimer**: Use responsibly and respect website terms of service and robots.txt files. This tool is intended for legitimate business development and analysis purposes only.
