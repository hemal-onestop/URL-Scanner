import streamlit as st
import requests
import pandas as pd
import time
import config
import random
import os
import json
import re
import concurrent.futures
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse, urljoin, quote_plus
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import tempfile
import base64
from io import BytesIO

st.set_page_config(page_title="Website Opportunity Finder", layout="wide")

# Enhanced CSS for better UI with theme toggle
st.markdown("""
<style>
    /* Theme Toggle Button */
    .theme-toggle {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        background: rgba(0, 0, 0, 0.8);
        border: none;
        border-radius: 50px;
        width: 50px;
        height: 50px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .theme-toggle:hover {
        background: rgba(0, 0, 0, 0.9);
        transform: scale(1.1);
    }
    
    /* Light Theme Variables */
    [data-theme="light"] {
        --bg-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --bg-secondary: #f8fafc;
        --bg-tertiary: white;
        --text-primary: #1a202c;
        --text-secondary: #374151;
        --text-tertiary: #64748b;
        --border-color: #e2e8f0;
        --accent-color: #667eea;
        --shadow-color: rgba(0, 0, 0, 0.1);
        --hover-shadow: rgba(0, 0, 0, 0.2);
    }
    
    /* Dark Theme Variables */
    [data-theme="dark"] {
        --bg-primary: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        --bg-secondary: #374151;
        --bg-tertiary: #1f2937;
        --text-primary: #f8fafc;
        --text-secondary: #e2e8f0;
        --text-tertiary: #94a3b8;
        --border-color: #4b5563;
        --accent-color: #10b981;
        --shadow-color: rgba(0, 0, 0, 0.3);
        --hover-shadow: rgba(0, 0, 0, 0.5);
    }
    
    /* Main App Styling - Theme Adaptive */
    .stApp {
        background: var(--bg-primary);
        min-height: 100vh;
        color: var(--text-primary);
        transition: all 0.3s ease;
    }
    
    .main-header {
        background: var(--bg-primary);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        text-align: center;
        color: white;
        box-shadow: var(--shadow-color);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.15), transparent);
        transform: rotate(45deg);
        animation: shimmer 3s infinite;
    }
    
    /* Sidebar Styling - Theme Adaptive */
    .css-1d391kg {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-color);
        box-shadow: var(--shadow-color);
    }
    
    .css-17ziqus {
        background-color: var(--bg-secondary) !important;
        padding: 1rem !important;
    }
    
    /* Reduced White Sections - Theme Adaptive */
    .template-section {
        background: var(--bg-secondary);
        padding: 0.8rem 1rem;
        border-radius: 10px;
        border: 1px solid var(--border-color);
        margin-bottom: 0.8rem;
        box-shadow: var(--shadow-color);
        position: relative;
        overflow: hidden;
        color: var(--text-primary);
    }
    
    .template-section::before {
        content: '📋';
        position: absolute;
        top: 8px;
        right: 12px;
        font-size: 1.1rem;
        opacity: 0.3;
        color: var(--accent-color);
    }
    
    .search-container {
        background: var(--bg-secondary);
        padding: 0.8rem 1rem;
        border-radius: 10px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-color);
        margin-bottom: 0.8rem;
        transition: all 0.3s ease;
        position: relative;
        color: var(--text-primary);
    }
    
    .search-container:hover {
        box-shadow: var(--hover-shadow);
        transform: translateY(-1px);
        border-color: var(--accent-color);
    }
    
    .search-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent-color), var(--bg-tertiary), var(--accent-color));
        border-radius: 10px 10px 0 0;
        opacity: 0.7;
    }
    
    /* Input Styling - Theme Adaptive */
    .stTextArea > div > div > textarea {
        border: 1px solid var(--border-color);
        border-radius: 8px;
        font-size: 14px;
        transition: all 0.3s ease;
        background: var(--bg-tertiary);
        padding: 10px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: var(--text-primary);
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-color);
        box-shadow: 0 0 0 3px var(--accent-color);
        background: var(--bg-secondary);
        outline: none;
        color: var(--text-primary);
    }
    
    .stSelectbox > div > div > div[data-testid="stSelectbox"] {
        background-color: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px;
        color: var(--text-primary) !important;
    }
    
    .stSelectbox > div > div > div[data-testid="stSelectbox"]:focus-within {
        border-color: var(--accent-color) !important;
        box-shadow: 0 0 0 3px var(--accent-color);
        background: var(--bg-secondary);
    }
    
    /* Button Styling - Enhanced Theme Adaptive */
    .stButton > button {
        background: var(--bg-primary);
        color: white;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-color);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--hover-shadow);
        background: var(--bg-tertiary);
        color: var(--text-primary);
        border-color: var(--accent-color);
    }
    
    /* Metric Cards - Theme Adaptive */
    .metric-card {
        background: var(--bg-secondary);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-color);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        color: var(--text-primary);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent-color), var(--bg-tertiary), var(--accent-color));
        border-radius: 10px 10px 0 0;
        opacity: 0.7;
    }
    
    .metric-card:hover {
        transform: translateY(-1px);
        box-shadow: var(--hover-shadow);
        border-color: var(--accent-color);
    }
    
    /* Data Display - Theme Adaptive */
    .dataframe-container {
        background: var(--bg-secondary);
        border-radius: 10px;
        padding: 1rem;
        box-shadow: var(--shadow-color);
        border: 1px solid var(--border-color);
        color: var(--text-primary);
    }
    
    /* Horizontal Rule for separation - Theme Adaptive */
    .st-hr {
        border: none;
        border-top: 1px solid var(--border-color);
        margin: 1rem 0;
    }
    
    /* Better Font Rendering */
    body {
        font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Streamlit Overrides - Theme Adaptive */
    .element-container {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
    }
    
    /* Success/Error Messages - Theme Adaptive */
    .stSuccess {
        background: var(--bg-primary);
        border-radius: 8px;
        padding: 1rem;
        color: white;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stWarning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        border-radius: 8px;
        padding: 1rem;
        color: white;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stError {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        border-radius: 8px;
        padding: 1rem;
        color: white;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Loading States - Theme Adaptive */
    .stSpinner > div {
        border-color: var(--accent-color) !important;
        border-top-color: transparent !important;
    }
    
    /* Slider Styling - Theme Adaptive */
    .stSlider > div > div > div {
        background-color: var(--border-color) !important;
    }
    
    .stSlider > div > div > div > div {
        background-color: var(--accent-color) !important;
    }
    
    /* Checkbox Styling - Theme Adaptive */
    .stCheckbox > div > label > span {
        background-color: var(--border-color) !important;
        border-color: var(--accent-color) !important;
    }
    
    .stCheckbox > div > label > span:hover {
        background-color: var(--accent-color) !important;
        border-color: var(--bg-tertiary) !important;
    }
    
    /* Smooth Scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .template-section, .search-container, .metric-card {
            padding: 0.8rem 1rem;
            margin-bottom: 0.6rem;
        }
        
        .stButton > button {
            padding: 8px 16px;
            font-size: 13px;
        }
    }
    
    @media (max-width: 480px) {
        .main-header {
            padding: 1rem;
        }
        
        .template-section, .search-container, .metric-card {
            padding: 0.6rem 0.8rem;
        }
        
        .stTextArea > div > div > textarea {
            font-size: 13px;
        }
    }
    /* Terminal Console */
    .terminal-console {
        background: #0d0d0d !important;
        color: #00ff00 !important;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
        padding: 0.8rem;
        border-radius: 8px;
        height: 180px;
        overflow-y: auto;
        font-size: 0.75rem;
        line-height: 1.3;
        border: 1px solid #333;
        margin: 0.5rem 0;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
        white-space: pre-wrap;
        word-break: break-all;
    }
    .terminal-line {
        margin-bottom: 3px;
        border-bottom: 1px solid rgba(0,255,0,0.05);
        padding-bottom: 2px;
    }
    .term-info { color: #00ff00 !important; }
    .term-warn { color: #ffff00 !important; }
    .term-error { color: #ff5555 !important; }
    .term-blue { color: #00bbff !important; }
    .term-gray { color: #888 !important; }
</style>
""", unsafe_allow_html=True)

# Theme toggle functionality
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Theme toggle button in top-right corner
st.markdown("""
<button class="theme-toggle" onclick="toggleTheme()" title="Toggle Theme">
    <span id="theme-icon">🌙</span>
</button>

<script>
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    document.getElementById('theme-icon').textContent = newTheme === 'dark' ? '🌙' : '🌞';
}

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'dark';
document.documentElement.setAttribute('data-theme', savedTheme);
document.getElementById('theme-icon').textContent = savedTheme === 'dark' ? '🌙' : '🌞';

// Set initial theme in session state
</script>
""", unsafe_allow_html=True)

# Custom header
st.markdown("""
<div class="main-header">
    <h1>🔎 Website Opportunity Finder</h1>
    <p>Find websites with poor SEO/UI that may need redesign</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# Terminal Logging Helpers
# ----------------------------

def log_to_terminal(message, level="info"):
    """Add a message to the terminal console logs."""
    if 'terminal_logs' not in st.session_state:
        st.session_state.terminal_logs = []
    
    timestamp = time.strftime("%H:%M:%S")
    color_class = {
        "info": "term-info",
        "warn": "term-warn",
        "error": "term-error",
        "blue": "term-blue",
        "gray": "term-gray"
    }.get(level, "term-info")
    
    # Escape some HTML special chars for safe rendering
    safe_msg = message.replace("<", "&lt;").replace(">", "&gt;")
    
    log_entry = f'<div class="terminal-line"><span class="term-blue">[{timestamp}]</span> <span class="{color_class}">{safe_msg}</span></div>'
    st.session_state.terminal_logs.append(log_entry)
    
    # Keep only last 100 logs
    if len(st.session_state.terminal_logs) > 100:
        st.session_state.terminal_logs.pop(0)

def render_terminal(container):
    """Render the terminal logs in a Streamlit container. Always shows the console box."""
    logs = st.session_state.get('terminal_logs', [])
    if logs:
        logs_html = "".join(logs)
    else:
        logs_html = '<div class="terminal-line"><span class="term-gray">[system] Terminal ready. Start a search to see live progress...</span></div>'
    container.markdown(f"""
    <div class="terminal-console" id="terminal-console">{logs_html}</div>
    <script>
        var terminal = document.getElementById('terminal-console');
        if (terminal) {{
            terminal.scrollTop = terminal.scrollHeight;
        }}
    </script>
    """, unsafe_allow_html=True)

# ----------------------------
# Search Templates
# ----------------------------

SEARCH_TEMPLATES = {
    "Real Estate": 'site:.com "real estate" "our listings"',
    "Restaurants": 'site:.com "restaurant" "our menu" "contact us"',
    "Local Business": 'site:.com "small business" "about us" "services"',
    "E-commerce": 'site:.com "online store" "shop now" "products"',
    "Healthcare": 'site:.com "medical" "appointment" "patient portal"',
    "Law Firms": 'site:.com "law firm" "practice areas" "contact"',
    "Dentists": 'site:.com "dentist" "book appointment" "dental services"',
    "Contractors": 'site:.com "contractor" "our services" "free quote"',
    "Hotels": 'site:.com "hotel" "book now" "rooms"',
    "Auto Dealers": 'site:.com "car dealership" "inventory" "contact us"',
    "Plumbers": 'site:.com "plumber" "emergency service" "call now"',
    "Electricians": 'site:.com "electrician" "electrical services" "free estimate"',
    "Roofing": 'site:.com "roofing" "free inspection" "contact us"',
    "Landscaping": 'site:.com "landscaping" "our services" "get quote"',
    "Cleaning Services": 'site:.com "cleaning service" "book now" "contact"',
    "Accounting": 'site:.com "accounting" "tax services" "contact us"',
    "Marketing": 'site:.com "marketing agency" "our services" "contact"',
    "Web Design": 'site:.com "web design" "portfolio" "contact us"',
    "Consulting": 'site:.com "consulting" "our services" "get started"',
    "Insurance": 'site:.com "insurance" "get quote" "contact us"'
}

# Query Builder with Country-First Filtering
def build_search_query(base_query, country_code=""):
    """Build search query with country filter applied first."""
    exclusions = " ".join([f"-site:{d}" for d in BLOCKED_DOMAINS[:5]])
    
    # Apply country filter first if specified
    if country_code:
        # Country-specific search - apply country filter first, then keywords
        country_query = f"site:{country_code} {base_query}"
        enhanced_query = f"{country_query} {exclusions}"
    else:
        # Worldwide search - just apply keywords and exclusions
        enhanced_query = f"{base_query} {exclusions}"
    
    return enhanced_query

# ----------------------------
# Fast Lead Assessment System
# ----------------------------

def quick_site_assessment(url, timeout=5):
    """Fast pre-filtering assessment (under 1 second)"""
    try:
        # Quick HTTP check
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code != 200:
            return None
            
        # Get minimal HTML content
        response = requests.get(url, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0'})
        html = response.text[:50000]  # Limit to first 50KB
        
        soup = BeautifulSoup(html, "html.parser")
        
        assessment = {
            'url': url,
            'status_code': response.status_code,
            'has_contact': False,
            'old_technology': False,
            'poor_ui_indicators': 0,
            'maintenance_issues': 0,
            'contact_methods': [],
            'should_analyze_fully': False
        }
        
        # Quick contact detection
        contact_indicators = ['contact', 'email', 'phone', 'call', 'reach', 'mailto:', 'tel:']
        for indicator in contact_indicators:
            if indicator in html.lower():
                assessment['has_contact'] = True
                assessment['contact_methods'].append(indicator)
                break
        
        # Old technology detection
        old_tech_patterns = [
            'jquery-1.', 'jquery-2.', 'bootstrap3', 'bootstrap 3', 
            'wordpress-4.', 'wordpress-5.0', 'wordpress-5.1',
            '<!DOCTYPE html PUBLIC', 'xhtml1', 'flashplayer',
            'table cellpadding', 'table width=', '<font face='
        ]
        
        for pattern in old_tech_patterns:
            if pattern in html.lower():
                assessment['old_technology'] = True
                break
        
        # Poor UI indicators (quick checks)
        poor_ui_patterns = [
            '<table', '<font', '<marquee', '<blink>', 'style="',
            'bgcolor=', 'text=', 'link=', 'vlink='
        ]
        
        for pattern in poor_ui_patterns:
            if pattern in html.lower():
                assessment['poor_ui_indicators'] += 1
        
        # Maintenance issues
        maintenance_patterns = [
            '© 20', 'last updated', 'since 20', 'est. 20',
            'all rights reserved', 'powered by'
        ]
        
        for pattern in maintenance_patterns:
            if pattern in html.lower():
                assessment['maintenance_issues'] += 1
        
        # Determine if worth full analysis
        assessment['should_analyze_fully'] = (
            assessment['has_contact'] and 
            (assessment['old_technology'] or assessment['poor_ui_indicators'] >= 2)
        )
        
        return assessment
        
    except Exception:
        return None

def detect_old_technology_detailed(html_content):
    """Detailed old technology detection"""
    old_tech = {
        'jquery_old': bool(re.search(r'jquery-[12]\.', html_content.lower())),
        'bootstrap_old': bool(re.search(r'bootstrap[ _]?[34]', html_content.lower())),
        'wordpress_old': bool(re.search(r'wordpress-[45]\.[0-9]', html_content.lower())),
        'flash_usage': 'flash' in html_content.lower() or 'swf' in html_content.lower(),
        'xhtml_doctype': 'xhtml' in html_content.lower()[:200],
        'table_layouts': html_content.lower().count('<table') > 5,
        'font_tags': '<font' in html_content.lower(),
        'inline_styles': html_content.lower().count('style="') > 10
    }
    
    return old_tech, sum(old_tech.values())

def extract_contact_info_fast(html_content):
    """Fast contact information extraction"""
    contacts = {'emails': [], 'phones': [], 'contact_pages': []}
    
    # Email extraction
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, html_content)
    contacts['emails'] = list(set(emails[:5]))  # Max 5 unique emails
    
    # Phone extraction
    phone_patterns = [
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
        r'\+?1[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}'
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, html_content)
        contacts['phones'].extend(phones)
    
    contacts['phones'] = list(set(contacts['phones'][:5]))  # Max 5 unique phones
    
    # Contact page detection
    contact_link_pattern = r'<a[^>]*>([^<]*(?:contact|call|reach|email|phone)[^<]*)</a>'
    contact_links = re.findall(contact_link_pattern, html_content, re.IGNORECASE)
    contacts['contact_pages'] = list(set(contact_links[:3]))
    
    return contacts

# ----------------------------
# Poor Site Lead Scoring System
# ----------------------------

def calculate_poor_site_lead_score(site_data, url):
    """Calculate lead score for poor sites (higher score = worse site = better lead)"""
    try:
        score = 50  # Base score
        
        # UI Score (inverted - poor UI gets higher score)
        ui_score = site_data.get("UI Score", 50)
        if isinstance(ui_score, (int, float)):
            if ui_score <= 30:  # Very poor UI
                score += 30
            elif ui_score <= 50:  # Poor UI
                score += 20
            elif ui_score <= 70:  # Fair UI
                score += 10
        
        # Visual Analysis (if available)
        visual_score = site_data.get("Visual Score", 75)
        if isinstance(visual_score, (int, float)):
            if visual_score <= 40:  # Very poor visual
                score += 25
            elif visual_score <= 60:  # Poor visual
                score += 15
        
        # Design Score (inverted - poor design gets higher score)
        design_score = site_data.get("Design Score", 75)
        if isinstance(design_score, (int, float)):
            if design_score <= 40:  # Very poor design
                score += 20
            elif design_score <= 60:  # Poor design
                score += 10
        
        # Performance (poor performance = higher score)
        perf_score = site_data.get("Performance", 50)
        if isinstance(perf_score, (int, float)):
            if perf_score <= 30:  # Very poor performance
                score += 15
            elif perf_score <= 50:  # Poor performance
                score += 8
        
        # SEO (poor SEO = higher score)
        seo_score = site_data.get("SEO Score", 50)
        if isinstance(seo_score, (int, float)):
            if seo_score <= 30:  # Very poor SEO
                score += 10
            elif seo_score <= 50:  # Poor SEO
                score += 5
        
        # Contact Information (has contact = higher score)
        has_email = site_data.get("Emails", "N/A") != "N/A"
        has_phone = site_data.get("Phone Numbers", "N/A") != "N/A"
        
        if has_email:
            score += 10
        if has_phone:
            score += 5
        
        # Technology (old technology = higher score)
        tech = site_data.get("Technology", "")
        old_tech_indicators = ["wordpress", "jquery", "bootstrap", "html4", "php"]
        for indicator in old_tech_indicators:
            if indicator.lower() in tech.lower():
                score += 5
                break
        
        # Visual Issues (more issues = higher score)
        visual_issues = site_data.get("Visual Issues", [])
        if isinstance(visual_issues, list):
            score += min(len(visual_issues) * 2, 15)
        
        return min(max(score, 0), 100)  # Clamp between 0-100
        
    except Exception:
        return 50

def is_poor_site_lead(site_data, ui_filter):
    """Check if site meets poor site lead criteria"""
    try:
        # Get UI score
        ui_score = site_data.get("UI Score", 50)
        if isinstance(ui_score, str):
            try:
                ui_score = int(ui_score) if ui_score != "N/A" else 50
            except:
                ui_score = 50
        
        # Primary filter: Poor UI (inverted logic)
        if ui_score >= ui_filter:  # This finds poor sites when filter is set high
            return True
        
        # Secondary filters for poor sites
        visual_score = site_data.get("Visual Score", 75)
        if isinstance(visual_score, (int, float)) and visual_score <= 50:
            return True
        
        design_score = site_data.get("Design Score", 75)
        if isinstance(design_score, (int, float)) and design_score <= 50:
            return True
        
        # Has contact information (required for lead)
        has_contact = (
            site_data.get("Emails", "N/A") != "N/A" or 
            site_data.get("Phone Numbers", "N/A") != "N/A"
        )
        
        if not has_contact:
            return False
        
        # Technology indicators
        tech = site_data.get("Technology", "")
        old_tech = any(indicator in tech.lower() for indicator in ["wordpress", "jquery", "php", "html4"])
        
        if old_tech and ui_score <= 70:  # Old tech with fair/poor UI
            return True
        
        return False
        
    except Exception:
        return False


# ----------------------------
# URL Validation
# ----------------------------

def is_website_active(url, timeout=10):
    """Check if a website is active and accessible."""
    try:
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Make a HEAD request first (faster than GET)
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        
        # If HEAD fails, try GET
        if response.status_code >= 400:
            response = requests.get(url, timeout=timeout, allow_redirects=True)
        
        # Check if status code indicates success
        return response.status_code < 400
        
    except requests.exceptions.RequestException:
        # Any exception means the site is not accessible
        return False
    except Exception:
        # Any other error means the site is not accessible
        return False

def validate_and_analyze_site(site, pagespeed_key, max_pages, terminal_container=None):
    """Validate site is active before analyzing, return None if inactive."""
    msg = f"🔍 Checking if {site} is accessible..."
    if terminal_container:
        log_to_terminal(msg, level="info")
        render_terminal(terminal_container)
    else:
        st.info(msg)
    
    if not is_website_active(site):
        warn_msg = f"⚠️ Skipping {site} - Inactive"
        if terminal_container:
            log_to_terminal(warn_msg, level="warn")
            render_terminal(terminal_container)
        else:
            st.warning(warn_msg)
        return None
    
    # If site is active, proceed with analysis
    return analyze_site(site, pagespeed_key, max_pages)

# ----------------------------
# Link History Management
# ----------------------------

HISTORY_FILE = "found_links_history.json"
SCANNED_SITES_FILE = "scanned_sites_history.json"  # Track ALL scanned sites

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_history(links):
    history = load_history()
    history.update(links)
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(list(history), f)
    except Exception as e:
        st.error(f"Failed to save history: {e}")

def load_scanned_sites():
    """Load ALL previously scanned sites."""
    if os.path.exists(SCANNED_SITES_FILE):
        try:
            with open(SCANNED_SITES_FILE, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_scanned_sites(sites):
    """Save ALL scanned sites to avoid re-scanning."""
    scanned = load_scanned_sites()
    scanned.update(sites)
    try:
        with open(SCANNED_SITES_FILE, "w") as f:
            json.dump(list(scanned), f)
    except Exception as e:
        st.error(f"Failed to save scanned sites: {e}")

def is_site_already_scanned(site):
    """Check if site was already scanned before."""
    scanned_sites = load_scanned_sites()
    return site in scanned_sites

# ----------------------------
# Crawling Logic (Scan Important Pages)
# ----------------------------

def get_pages_to_scan(url, max_pages=5):
    """Find the homepage and other key pages (about, contact, services, etc.)."""
    pages = [url]  # Always include homepage
    important_keywords = ['about', 'service', 'contact', 'blog', 'listing', 'property', 'portfolio']
    
    try:
        r = requests.get(url, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        
        found_links = []
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a["href"])
            # Only internal links
            if link.startswith(url) and link != url and link != url + "/":
                # Clean URL (remove fragments/queries)
                clean_link = link.split("#")[0].split("?")[0].rstrip("/")
                if clean_link not in pages and clean_link not in found_links:
                    found_links.append(clean_link)
        
        # Sort found_links to prioritize important keywords
        def link_priority(link):
            for i, kw in enumerate(important_keywords):
                if kw in link.lower():
                    return i
            return len(important_keywords)
            
        found_links.sort(key=link_priority)
        pages.extend(found_links[:max_pages-1])
        
    except Exception as e:
        # print(f"Crawl error for {url}: {e}")
        pass
        
    return pages[:max_pages]

# ----------------------------
# Blocked Domains (Exclude Big Platforms)
# ----------------------------

BLOCKED_DOMAINS = [
"youtube.com",
"instagram.com",
"facebook.com",
"linkedin.com",
"twitter.com",
"x.com",
"tiktok.com",
"pinterest.com",
"reddit.com",
"snapchat.com",
"telegram.org",
"discord.com",

"openai.com",
"anthropic.com",
"mistral.ai",
"huggingface.co",
"perplexity.ai",
"runwayml.com",

"google.com",
"microsoft.com",
"apple.com",
"amazon.com",
"meta.com",
"nvidia.com",
"ibm.com",
"oracle.com",
"adobe.com",
"salesforce.com",

"zillow.com",
"realtor.com",
"redfin.com",
"trulia.com",

"github.com",
"stackoverflow.com",
"medium.com",
"dev.to"
]

def is_blocked(url):
    """Check if the URL belongs to a blocked high-authority domain."""
    domain = urlparse(url).netloc.lower()
    
    # Remove 'www.' prefix for cleaner comparison
    if domain.startswith("www."):
        domain = domain[4:]
        
    # Check against the blacklist
    for blocked in BLOCKED_DOMAINS:
        if blocked in domain:
            log_to_terminal(f"🚫 Blocked: {domain} ({blocked})", level="gray")
            return True
            
    # Skip .gov, .edu, and .mil domains
    if domain.endswith(".gov") or domain.endswith(".edu") or domain.endswith(".mil"):
        log_to_terminal(f"🚫 Restricted TLD: {domain}", level="gray")
        return True
        
    return False

# ----------------------------
# Sidebar - Configuration & Filters
# ----------------------------

with st.sidebar:
    st.markdown("""
    <div class="template-section">
        <h4 style="margin-bottom: 0.8rem; color: #e0e0e0; font-weight: 600; font-size: 0.9rem;">🔧 Scan Mode</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Mode selection
    scan_mode = st.radio(
        "Select Mode",
        ["🔍 Finder Mode", "📋 URL Scanner Mode"],
        help="Choose between keyword search or direct URL scanning",
        index=0
    )
    
    st.markdown('<hr class="st-hr">', unsafe_allow_html=True)
    
    # Show different sections based on mode
    if scan_mode == "🔍 Finder Mode":
        st.markdown("""
        <div class="template-section">
            <h4 style="margin-bottom: 0.8rem; color: #e0e0e0; font-weight: 600; font-size: 0.9rem;">📋 Templates</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Template selection with optimized layout
        selected_template = st.selectbox(
            "Select Template", 
            ["Custom"] + list(SEARCH_TEMPLATES.keys()),
            help="Choose a pre-built search template",
            index=0
        )
        
        # Add horizontal rule separator
        st.markdown('<hr class="st-hr">', unsafe_allow_html=True)
        
        # Set query based on template selection
        default_query = SEARCH_TEMPLATES.get(selected_template, '"real estate" "our listings" site:.com') if selected_template != "Custom" else '"real estate" "our listings" site:.com'
        
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        st.markdown('<h4 style="margin-bottom: 0.8rem; color: #e0e0e0; font-weight: 600; font-size: 0.9rem;">🔍 Search Query</h4>', unsafe_allow_html=True)
        query = st.text_area(
            "",
            value=default_query,
            height=100,
            help="Enter your search query with keywords in quotes",
            placeholder="e.g., site:.com \"real estate\" \"our listings\"",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="search-container">
            <h4 style="margin-bottom: 0.8rem; color: #e0e0e0; font-weight: 600; font-size: 0.9rem;">📋 URL Input</h4>
        </div>
        """, unsafe_allow_html=True)
        
        url_input = st.text_area(
            "Enter URLs to scan",
            height=150,
            help="Enter one URL per line. Each URL will be analyzed based on your filter criteria.",
            placeholder="https://example1.com\nhttps://example2.com\nhttps://example3.com"
        )
        
        # Parse URLs from input and store in session state
        if url_input:
            urls_to_scan = [line.strip() for line in url_input.split('\n') if line.strip()]
        else:
            urls_to_scan = []
        
        # Store URLs in session state
        st.session_state.urls_to_scan = urls_to_scan
        
        # Debug info (can be removed later)
        if urls_to_scan:
            st.info(f"📋 Found {len(urls_to_scan)} URLs to scan")

    st.markdown('<hr class="st-hr">', unsafe_allow_html=True)

    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.markdown('<h4 style="margin-bottom: 0.8rem; color: #e0e0e0; font-weight: 600; font-size: 0.9rem;">⚙️ Settings</h4>', unsafe_allow_html=True)

    # ── Collect API keys first so we can build available-provider list ──
    # (Keys section rendered later but values captured here via session state trick)
    # We read from config + sidebar inputs collected in a temporary pass
    _api_keys_preview = {
        "Zenserp":    config.ZENSERP_API_KEY,
        "SerpApi":    config.SERPAPI_KEY,
        "ScraperAPI": config.SCRAPERAPI_KEY,
        "Bright Data":config.BRIGHTDATA_KEY,
        "Oxylabs":    config.OXYLABS_KEY,
        "Smartproxy": config.SMARTPROXY_KEY,
        "ZenRows":    config.ZENROWS_KEY,
        "ScraperBot": config.SCRAPERBOT_KEY,
        "SearchAPI":  config.SEARCHAPI_KEY,
    }
    # Session state holds manually-entered keys between reruns
    for _p, _v in _api_keys_preview.items():
        _sk = f"_key_{_p.replace(' ','_')}"
        if _v and not st.session_state.get(_sk):
            st.session_state[_sk] = _v

    def _has_key(provider):
        """Return True if this provider has a key loaded (config or manual entry)."""
        sk = f"_key_{provider.replace(' ','_')}"
        return bool(st.session_state.get(sk, ""))

    # Build available provider list (Google Search never needs a key)
    ALL_PROVIDERS = ["Google Search", "Zenserp", "SerpApi", "ScraperAPI",
                     "Bright Data", "Oxylabs", "Smartproxy", "ZenRows", "ScraperBot", "SearchAPI"]
    available_providers = [p for p in ALL_PROVIDERS if p == "Google Search" or _has_key(p)]
    locked_providers  = [p for p in ALL_PROVIDERS if p != "Google Search" and not _has_key(p)]

    col1, col2 = st.columns(2)
    with col1:
        search_provider = st.selectbox(
            "🔌 Provider",
            available_providers,
            help="Only providers with a valid API key are shown. Add keys in the 🔑 API Keys section below.",
            index=0
        )
        limit = st.number_input(
            "📊 Lead Target",
            min_value=1,
            max_value=10000,
            value=20,
            help="Auto-Analyze will keep scanning until this many qualified leads are found (unlimited scan budget)"
        )
    with col2:
        search_engine = st.selectbox(
            "🔎 Search Engine",
            ("Google", "Bing", "Yahoo", "DuckDuckGo"),
            help="Actual search engine to query. Not all providers support every engine.",
            index=0
        )
        if search_provider == "Google Search":
            skip_pages = st.number_input(
                "⏭️ Skip Pages",
                min_value=0, max_value=50, value=0,
                help="Skip this many Google result pages before starting"
            )
        else:
            skip_pages = 0

    col3, col4 = st.columns(2)
    with col3:
        max_pages_to_scan = st.slider("📄 Pages/Site", 1, 10, 3, help="Pages to analyze per website")
    with col4:
        concurrency = st.slider("⚡ Threads", 1, 5, 3, help="Parallel threads for faster site analysis")

    # Show locked providers legend
    if locked_providers:
        locked_str = ", ".join(locked_providers)
        st.markdown(f"""
        <div style="background: rgba(255,193,7,0.12); border-left: 3px solid #ffc107;
                    padding: 0.5rem 0.8rem; border-radius: 6px; margin-top: 0.6rem;">
            <small style="color:#ffc107;">
                🔒 <b>Locked</b> (no API key): {locked_str}<br>
                Add keys in the <b>🔑 API Keys</b> section below to unlock them.
            </small>
        </div>
        """, unsafe_allow_html=True)

    # Country selector
    COUNTRIES = {
        "🌍 Worldwide": "",
        "🇺🇸 United States": "us",
        "🇬🇧 United Kingdom": "uk",
        "🇨🇦 Canada": "ca",
        "🇦🇺 Australia": "au",
        "🇮🇳 India": "in",
        "🇩🇪 Germany": "de",
        "🇫🇷 France": "fr",
        "🇧🇷 Brazil": "br",
        "🇲🇽 Mexico": "mx",
        "🇿🇦 South Africa": "za",
        "🇸🇬 Singapore": "sg",
        "🇦🇪 UAE": "ae",
        "🇯🇵 Japan": "jp",
        "🇳🇱 Netherlands": "nl",
        "🇸🇪 Sweden": "se",
        "🇳🇿 New Zealand": "nz",
        "🇮🇪 Ireland": "ie",
        "🇵🇭 Philippines": "ph",
        "🇵🇰 Pakistan": "pk",
        "🇳🇬 Nigeria": "ng",
        "🇰🇪 Kenya": "ke",
    }
    country_label = st.selectbox(
        "🌐 Country",
        list(COUNTRIES.keys()),
        help="Filter results to a specific country's search index",
        index=0
    )
    country_code = COUNTRIES[country_label]
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="st-hr">', unsafe_allow_html=True)

    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.markdown('<h4 style="margin-bottom: 0.8rem; color: #e0e0e0; font-weight: 600; font-size: 0.9rem;">🎯 Filters</h4>', unsafe_allow_html=True)
    
    # Optimized layout for filters
    col1, col2 = st.columns(2)
    with col1:
        ui_filter = st.slider("UI Score ≤ ", 0, 100, 50, help="Maximum UI score")
        perf_filter = st.slider("Perf Score ≤ ", 0, 100, 50, help="Maximum Performance score")
    with col2:
        seo_filter = st.slider("SEO Score ≤ ", 0, 100, 60, help="Maximum SEO score")
        auto_analyze = st.checkbox(
            "🤖 Auto-Analyze", 
            value=False, 
            help="Analyze during search"
        )
        avoid_history = st.checkbox(
            "🚫 Avoid History", 
            value=True, 
            help="Skip previously found URLs"
        )
        enable_screenshots = st.checkbox(
            "📸 Enable Screenshots", 
            value=True, 
            help="Capture screenshots for visual analysis (slower but more detailed)"
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Conditional URLs to skip section
    if avoid_history:
        st.markdown('<hr class="st-hr">', unsafe_allow_html=True)
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        st.markdown('<h4 style="margin-bottom: 0.5rem; color: #e0e0e0; font-weight: 600; font-size: 0.9rem;">📝 Skip URLs</h4>', unsafe_allow_html=True)
        manual_avoid_input = st.text_area(
            "", 
            height=60,
            help="Enter URLs to skip manually",
            placeholder="example.com\nanother-site.com"
        )
        if manual_avoid_input:
            manual_avoid_list = [line.strip().lower() for line in manual_avoid_input.split("\n") if line.strip()]
        else:
            manual_avoid_list = []
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        manual_avoid_list = []

    st.markdown('<hr class="st-hr">', unsafe_allow_html=True)

    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.markdown('<h4 style="margin-bottom: 0.8rem; color: #e0e0e0; font-weight: 600; font-size: 0.9rem;">🔑 API Keys</h4>', unsafe_allow_html=True)

    def _key_field(label, config_val, help_txt):
        sk = f"_key_{label.replace(' ','_')}"
        if config_val:
            st.success(f"✅ {label} loaded from config")
            st.session_state[sk] = config_val
            return config_val
        val = st.text_input(f"🔐 {label}", type="password", help=help_txt,
                           key=f"input_{sk}")
        if val:
            st.session_state[sk] = val
        elif sk in st.session_state and not config_val:
            # Keep previously typed value across reruns
            val = st.session_state.get(sk, "")
        return val

    pagespeed_key  = _key_field("PageSpeed",  config.PAGESPEED_API_KEY,  "Google PageSpeed Insights")
    serpapi_key    = _key_field("Zenserp",    config.ZENSERP_API_KEY,    "Zenserp.com API key")
    serpapi_key_alt= _key_field("SerpApi",    config.SERPAPI_KEY,        "SerpApi.com API key")
    scraperapi_key = _key_field("ScraperAPI", config.SCRAPERAPI_KEY,     "ScraperAPI.com API key")
    brightdata_key = _key_field("Bright Data",config.BRIGHTDATA_KEY,     "Bright Data Bearer token")
    oxylabs_key    = _key_field("Oxylabs",    config.OXYLABS_KEY,        "Oxylabs user:password")
    smartproxy_key = _key_field("Smartproxy", config.SMARTPROXY_KEY,     "Smartproxy Bearer token")
    zenrows_key    = _key_field("ZenRows",    config.ZENROWS_KEY,        "ZenRows.com API key")
    scraperbot_key = _key_field("ScraperBot", config.SCRAPERBOT_KEY,     "ScraperBot.io Bearer token")
    searchapi_key  = _key_field("SearchAPI",  config.SEARCHAPI_KEY,      "SearchAPI.io API key")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# Shared helpers
# ----------------------------

# ----------------------------
# API error helper
# ----------------------------

def _show_api_error(provider, status=None, exc=None):
    """Show a clear, actionable error message for API failures."""
    if status == 401:
        st.error(
            f"🔑 **{provider}: Invalid API Key** — The key you entered was rejected. "
            f"Please check your key in the 🔑 API Keys section or at the {provider} dashboard."
        )
    elif status == 403:
        st.error(
            f"🚫 **{provider}: Access Denied** — Your account may not have permission for this endpoint. "
            f"Check your plan or IP whitelist settings on {provider}."
        )
    elif status == 429:
        st.warning(
            f"💳 **{provider}: Plan Limit / Credits Exhausted** — You've used up your quota or monthly credits. "
            f"Please either:\n"
            f"- 🔄 Switch to another provider in the **🔌 Provider** dropdown, or\n"
            f"- 💰 Upgrade your {provider} subscription / add more credits."
        )
    elif status:
        st.error(f"⚠️ **{provider}: HTTP {status}** — {exc or 'Unexpected API error. Please try again.'}")
    else:
        st.error(f"🌐 **{provider}: Connection Error** — {exc or 'Could not reach the API. Check your internet connection.'}")


# ----------------------------

ENGINE_URLS = {
    "Google":     lambda q, n, start: f"https://www.google.com/search?q={quote_plus(q)}&num={n}&start={start}",
    "Bing":        lambda q, n, start: f"https://www.bing.com/search?q={quote_plus(q)}&count={n}&first={start+1}",
    "Yahoo":       lambda q, n, start: f"https://search.yahoo.com/search?p={quote_plus(q)}&n={n}&b={start+1}",
    "DuckDuckGo":  lambda q, n, start: f"https://html.duckduckgo.com/html/?q={quote_plus(q)}",
}

def _parse_html_results(html, engine, base_url_filter=None):
    """Extract organic result URLs from raw HTML for any supported search engine."""
    soup = BeautifulSoup(html, "html.parser")
    urls = []

    if engine == "Google":
        for a in soup.select("a"):
            href = a.get("href", "")
            if href.startswith("http") and "google" not in href:
                urls.append(href)
    elif engine == "Bing":
        for li in soup.select("li.b_algo"):
            a = li.find("a")
            if a and a.get("href", "").startswith("http"):
                urls.append(a["href"])
    elif engine == "Yahoo":
        for div in soup.select("div.algo-sr"):
            a = div.find("a")
            if a:
                href = a.get("href", "")
                if href.startswith("http") and "yahoo" not in href:
                    urls.append(href)
        if not urls:  # fallback
            for a in soup.select(".compTitle a"):
                href = a.get("href", "")
                if href.startswith("http") and "yahoo" not in href:
                    urls.append(href)
    elif engine == "DuckDuckGo":
        for a in soup.select(".result__a"):
            href = a.get("href", "")
            if href.startswith("http"):
                urls.append(href)
        if not urls:
            for a in soup.find_all("a", class_="result__url"):
                href = a.get("href", "")
                if href.startswith("http"):
                    urls.append(href)
    else:
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("http"):
                urls.append(href)

    return urls


def _filter_urls(raw_urls, history, manual_avoid, skip_history):
    """Apply blocked-domain, history and manual-avoid filters. Exclude PDFs and documents."""
    out = []
    for href in raw_urls:
        if not href or is_blocked(href):
            continue
        
        url_lower = href.lower()
        
        # Skip PDFs and documents
        document_extensions = [
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.txt', '.rtf', '.odt', '.ods', '.odp', '.csv', '.zip',
            '.rar', '.tar', '.gz', '.7z', '.exe', '.msi', '.dmg',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico',
            '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'
        ]
        
        # Check if URL ends with any document/media extension
        if any(url_lower.endswith(ext) for ext in document_extensions):
            continue
            
        # Check if URL contains document indicators
        document_indicators = [
            'download', 'file', 'attachment', 'document', 'media',
            'assets', 'static', 'resources', 'uploads', 'files'
        ]
        
        # Skip if URL has document indicators AND file extensions in path
        if any(indicator in url_lower for indicator in document_indicators):
            if any(f'.{ext}' in url_lower for ext in ['pdf', 'doc', 'xls', 'ppt', 'jpg', 'png', 'mp3', 'mp4']):
                continue
        
        if skip_history and (url_lower in history or any(av in url_lower for av in manual_avoid)):
            continue
        out.append(href)
    return out


# ----------------------------
# SerpApi Search
# ----------------------------

def serpapi_search(query, limit, api_key, offset=0, skip_history=False,
                   manual_avoid_list=None, country_code="", engine="Google"):
    """Fetch websites from SerpApi with engine + country support."""
    urls = []
    history = load_history() if skip_history else set()
    manual_avoid = set(manual_avoid_list or [])

    # Build query with country filter applied first
    enhanced_query = build_search_query(query, country_code)

    engine_map = {"Google": "google", "Bing": "bing", "Yahoo": "yahoo", "DuckDuckGo": "duckduckgo"}
    params = {
        "q": enhanced_query,
        "num": min(limit, 100),
        "start": offset,
        "api_key": api_key,
        "engine": engine_map.get(engine, "google")
    }
    if country_code:
        params["gl"] = country_code

    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=(5, 30))
        response.raise_for_status()
        data = response.json()
        raw = [r.get("link", "") for r in data.get("organic_results", [])]
        urls = _filter_urls(raw, history, manual_avoid, skip_history)
    except requests.exceptions.HTTPError as e:
        _show_api_error("SerpApi", status=e.response.status_code, exc=str(e))
    except requests.exceptions.ConnectionError:
        _show_api_error("SerpApi")
    except Exception as e:
        _show_api_error("SerpApi", exc=str(e))

    return list(dict.fromkeys(urls))[:limit]  # preserve order, dedupe

# ----------------------------
# ScraperAPI Search
# ----------------------------

def scraperapi_search(query, limit, api_key, offset=0, skip_history=False,
                      manual_avoid_list=None, country_code="us", engine="Google"):
    """Fetch websites using ScraperAPI (proxies chosen engine)."""
    urls = []
    history = load_history() if skip_history else set()
    manual_avoid = set(manual_avoid_list or [])

    # Build query with country filter applied first
    enhanced_query = build_search_query(query, country_code)
    target_url = ENGINE_URLS.get(engine, ENGINE_URLS["Google"])(enhanced_query, min(limit, 100), offset)

    params = {
        "api_key": api_key,
        "url": target_url,
        "country_code": country_code or "us"
    }

    try:
        response = requests.get("http://api.scraperapi.com", params=params, timeout=(5, 60))
        response.raise_for_status()
        raw = _parse_html_results(response.text, engine)
        urls = _filter_urls(raw, history, manual_avoid, skip_history)
    except requests.exceptions.HTTPError as e:
        _show_api_error("ScraperAPI", status=e.response.status_code, exc=str(e))
    except requests.exceptions.ConnectionError:
        _show_api_error("ScraperAPI")
    except Exception as e:
        _show_api_error("ScraperAPI", exc=str(e))

    return list(dict.fromkeys(urls))[:limit]

# ----------------------------
# Bright Data Search
# ----------------------------

def brightdata_search(query, limit, api_key, offset=0, skip_history=False,
                      manual_avoid_list=None, country_code="", engine="Google"):
    """Fetch websites using Bright Data SERP API."""
    urls = []
    history = load_history() if skip_history else set()
    manual_avoid = set(manual_avoid_list or [])

    # Build query with country filter applied first
    enhanced_query = build_search_query(query, country_code)
    target_url = ENGINE_URLS.get(engine, ENGINE_URLS["Google"])(enhanced_query, min(limit, 100), offset)
    if country_code:
        target_url += f"&gl={country_code}"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"zone": "serp_api", "url": target_url}

    try:
        response = requests.post("https://api.brightdata.com/serp", headers=headers,
                                 json=payload, timeout=(5, 60))
        response.raise_for_status()
        data = response.json()
        raw = [r.get("link", "") for r in data.get("organic_results", [])]
        if not raw:
            raw = _parse_html_results(data.get("html", ""), engine)
        urls = _filter_urls(raw, history, manual_avoid, skip_history)
    except requests.exceptions.HTTPError as e:
        _show_api_error("Bright Data", status=e.response.status_code, exc=str(e))
    except requests.exceptions.ConnectionError:
        _show_api_error("Bright Data")
    except Exception as e:
        _show_api_error("Bright Data", exc=str(e))

    return list(dict.fromkeys(urls))[:limit]

# ----------------------------
# Oxylabs Search
# ----------------------------

def oxylabs_search(query, limit, api_key, offset=0, skip_history=False,
                   manual_avoid_list=None, country_code="", engine="Google"):
    """Fetch websites using Oxylabs SERP API."""
    urls = []
    history = load_history() if skip_history else set()
    manual_avoid = set(manual_avoid_list or [])

    # Build query with country filter applied first
    enhanced_query = build_search_query(query, country_code)

    source_map = {"Google": "google_search", "Bing": "bing_search", "Yahoo": "yahoo_search", "DuckDuckGo": "universal"}
    payload = {
        "source": source_map.get(engine, "google_search"),
        "query": enhanced_query,
        "parse": True,
        "start_page": max(1, offset // 10 + 1),
        "num": min(limit, 100)
    }
    if country_code:
        payload["geo_location"] = country_code

    try:
        response = requests.post(
            f"https://{api_key}:@realtime.oxylabs.io/v1/queries",
            headers={"Content-Type": "application/json"},
            json=payload, timeout=(5, 60)
        )
        response.raise_for_status()
        data = response.json()
        organic = (data.get("results", [{}])[0]
                       .get("content", {})
                       .get("results", {})
                       .get("organic", []))
        raw = [r.get("url", "") for r in organic]
        urls = _filter_urls(raw, history, manual_avoid, skip_history)
    except requests.exceptions.HTTPError as e:
        _show_api_error("Oxylabs", status=e.response.status_code, exc=str(e))
    except requests.exceptions.ConnectionError:
        _show_api_error("Oxylabs")
    except Exception as e:
        _show_api_error("Oxylabs", exc=str(e))

    return list(dict.fromkeys(urls))[:limit]

# ----------------------------
# Smartproxy Search
# ----------------------------

def smartproxy_search(query, limit, api_key, offset=0, skip_history=False,
                      manual_avoid_list=None, country_code="", engine="Google"):
    """Fetch websites using Smartproxy SERP API."""
    urls = []
    history = load_history() if skip_history else set()
    manual_avoid = set(manual_avoid_list or [])

    # Build query with country filter applied first
    enhanced_query = build_search_query(query, country_code)
    target_url = ENGINE_URLS.get(engine, ENGINE_URLS["Google"])(enhanced_query, min(limit, 100), offset)

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"url": target_url, "source": f"{engine.lower()}_search"}
    if country_code:
        payload["target_country"] = country_code

    try:
        response = requests.post("https://scraper-api.smartproxy.com/v1/scrape",
                                 headers=headers, json=payload, timeout=(5, 60))
        response.raise_for_status()
        data = response.json()
        raw = _parse_html_results(data.get("content", ""), engine)
        urls = _filter_urls(raw, history, manual_avoid, skip_history)
    except requests.exceptions.HTTPError as e:
        _show_api_error("Smartproxy", status=e.response.status_code, exc=str(e))
    except requests.exceptions.ConnectionError:
        _show_api_error("Smartproxy")
    except Exception as e:
        _show_api_error("Smartproxy", exc=str(e))

    return list(dict.fromkeys(urls))[:limit]

# ----------------------------
# ZenRows Search
# ----------------------------

def zenrows_search(query, limit, api_key, offset=0, skip_history=False,
                   manual_avoid_list=None, country_code="", engine="Google"):
    """Fetch websites using ZenRows API."""
    urls = []
    history = load_history() if skip_history else set()
    manual_avoid = set(manual_avoid_list or [])

    # Build query with country filter applied first
    enhanced_query = build_search_query(query, country_code)
    target_url = ENGINE_URLS.get(engine, ENGINE_URLS["Google"])(enhanced_query, min(limit, 100), offset)

    params = {
        "api_key": api_key,
        "url": target_url,
        "js_render": "true",
        "premium_proxy": "true"
    }
    if country_code:
        params["premium_proxy_country"] = country_code

    try:
        response = requests.get("https://api.zenrows.com/v1/", params=params, timeout=(5, 60))
        response.raise_for_status()
        raw = _parse_html_results(response.text, engine)
        urls = _filter_urls(raw, history, manual_avoid, skip_history)
    except requests.exceptions.HTTPError as e:
        _show_api_error("ZenRows", status=e.response.status_code, exc=str(e))
    except requests.exceptions.ConnectionError:
        _show_api_error("ZenRows")
    except Exception as e:
        _show_api_error("ZenRows", exc=str(e))

    return list(dict.fromkeys(urls))[:limit]

# ----------------------------
# ScraperBot Search
# ----------------------------

def scraperbot_search(query, limit, api_key, offset=0, skip_history=False,
                      manual_avoid_list=None, country_code="", engine="Google"):
    """Fetch websites using ScraperBot API."""
    urls = []
    history = load_history() if skip_history else set()
    manual_avoid = set(manual_avoid_list or [])

    # Build query with country filter applied first
    enhanced_query = build_search_query(query, country_code)
    target_url = ENGINE_URLS.get(engine, ENGINE_URLS["Google"])(enhanced_query, min(limit, 100), offset)

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"url": target_url}
    if country_code:
        payload["country"] = country_code

    try:
        response = requests.post("https://api.scraperbot.io/scrape",
                                 headers=headers, json=payload, timeout=(5, 60))
        response.raise_for_status()
        data = response.json()
        raw = _parse_html_results(data.get("html", ""), engine)
        urls = _filter_urls(raw, history, manual_avoid, skip_history)
    except requests.exceptions.HTTPError as e:
        _show_api_error("ScraperBot", status=e.response.status_code, exc=str(e))
    except requests.exceptions.ConnectionError:
        _show_api_error("ScraperBot")
    except Exception as e:
        _show_api_error("ScraperBot", exc=str(e))

    return list(dict.fromkeys(urls))[:limit]

# ----------------------------
# SearchAPI.io Search
# ----------------------------

def searchapi_search(query, limit, api_key, offset=0, skip_history=False,
                     manual_avoid_list=None, country_code="", engine="Google"):
    """Fetch websites using SearchAPI.io."""
    urls = []
    history = load_history() if skip_history else set()
    manual_avoid = set(manual_avoid_list or [])

    # Build query with country filter applied first
    enhanced_query = build_search_query(query, country_code)

    engine_map = {"Google": "google", "Bing": "bing", "Yahoo": "yahoo"}
    params = {
        "api_key": api_key,
        "engine": engine_map.get(engine, "google"),
        "q": enhanced_query,
        "num": min(limit, 100),
        "start": offset
    }
    if country_code:
        params["gl"] = country_code

    try:
        response = requests.get("https://api.searchapi.io/v1/search", params=params, timeout=(5, 30))
        response.raise_for_status()
        data = response.json()
        raw = [r.get("link", "") for r in data.get("organic_results", [])]
        urls = _filter_urls(raw, history, manual_avoid, skip_history)
    except requests.exceptions.HTTPError as e:
        _show_api_error("SearchAPI", status=e.response.status_code, exc=str(e))
    except requests.exceptions.ConnectionError:
        _show_api_error("SearchAPI")
    except Exception as e:
        _show_api_error("SearchAPI", exc=str(e))

    return list(dict.fromkeys(urls))[:limit]

# ----------------------------
# Google Search via Zenserp
# ----------------------------

def find_sites(query, limit, serpapi_key, offset=0, skip_history=False,
              manual_avoid_list=None, country_code="", engine="Google"):
    """Fetch websites from Zenserp. Supports paging for large limits."""
    urls = []
    history = load_history() if skip_history else set()
    manual_avoid = set(manual_avoid_list or [])

    # Build query with country filter applied first
    enhanced_query = build_search_query(query, country_code)

    current_offset = offset
    remaining_limit = limit

    # Zenserp only supports Google natively; warn if another engine selected
    if engine != "Google":
        log_to_terminal(f"⚠️ Zenserp only supports Google search. Ignoring '{engine}' selection.", level="warn")

    while remaining_limit > 0:
        batch_size = min(remaining_limit, 100)
        params = {
            "q": enhanced_query,
            "num": batch_size,
            "start": current_offset
        }
        if country_code:
            params["gl"] = country_code

        headers = {"apikey": serpapi_key}

        try:
            response = requests.get("https://app.zenserp.com/api/v2/search",
                                    params=params, headers=headers, timeout=(5, 30))
            response.raise_for_status()
            data = response.json()

            organic = data.get("organic", [])
            if not organic:
                break

            batch_urls = _filter_urls(
                [r.get("url", "") for r in organic],
                history, manual_avoid, skip_history
            )
            urls.extend(batch_urls)

            if len(urls) >= limit:
                break

            current_offset += batch_size
            remaining_limit -= batch_size

            if len(organic) < batch_size:
                break

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            _show_api_error("Zenserp", status=status, exc=str(e))
            break
        except requests.exceptions.ConnectionError:
            _show_api_error("Zenserp")
            break
        except Exception as e:
            _show_api_error("Zenserp", exc=str(e))
            break

    return list(dict.fromkeys(urls))[:limit]

# ----------------------------
# Google Search (Selenium)
# ----------------------------

def google_search(query, limit=20, callback=None, skip_pages=0, skip_history=False,
                  manual_avoid_list=None, terminal_container=None, country_code="", engine="Google"):
    """
    Search using Selenium. Supports Google, Bing, Yahoo, DuckDuckGo.
    If callback is provided, called for every URL found.
    Callback returns True to continue, False to stop.
    """
    history = load_history() if skip_history else set()
    manual_avoid = set(manual_avoid_list or [])

    # Build query with country filter applied first
    enhanced_query = build_search_query(query, country_code)

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    urls = []
    stop_search = False

    # Build engine-specific start URL
    start_offset = skip_pages * 10
    enc_q = quote_plus(enhanced_query)
    country_suffix = f"&gl={country_code}" if country_code else ""

    engine_start_urls = {
        "Google":      f"https://www.google.com/search?q={enc_q}&start={start_offset}{country_suffix}",
        "Bing":         f"https://www.bing.com/search?q={enc_q}&first={start_offset+1}",
        "Yahoo":        f"https://search.yahoo.com/search?p={enc_q}&b={start_offset+1}",
        "DuckDuckGo":   f"https://html.duckduckgo.com/html/?q={enc_q}",
    }
    start_url = engine_start_urls.get(engine, engine_start_urls["Google"])

    # Result link selectors per engine
    result_selectors = {
        "Google":     "//a[h3]",
        "Bing":        "//li[contains(@class,'b_algo')]//h2/a",
        "Yahoo":       "//div[contains(@class,'algo-sr')]//h3/a",
        "DuckDuckGo": "//a[@class='result__a']",
    }
    xpath_sel = result_selectors.get(engine, "//a[h3]")

    # Next-page selectors per engine
    next_selectors = {
        "Google":    "pnnext",
        "Bing":       "pnnext",
        "Yahoo":      None,  # handled via XPath below
        "DuckDuckGo": None,  # single page
    }

    try:
        driver.get(start_url)
        time.sleep(4)

        # Allow unlimited pages when using callback (until limit met or results exhausted)
        page = 0
        while True:
            if stop_search:
                break

            results = driver.find_elements(By.XPATH, xpath_sel)

            for r in results:
                href = r.get_attribute("href")
                if href and not is_blocked(href):
                    url_lower = href.lower()
                    if skip_history and (url_lower in history or any(av in url_lower for av in manual_avoid)):
                        continue
                    if callback:
                        should_continue = callback(href)
                        if not should_continue:
                            stop_search = True
                            break
                    else:
                        if href not in urls:
                            urls.append(href)
                        if len(urls) >= limit:
                            stop_search = True
                            break

            if terminal_container:
                render_terminal(terminal_container)

            if stop_search:
                break

            # Navigate to next page
            try:
                if engine == "Yahoo":
                    next_btn = driver.find_element(By.XPATH, "//a[@class='next']")
                    next_btn.click()
                elif engine in ("DuckDuckGo",):
                    break  # DDG html doesn't paginate well
                else:
                    next_btn = driver.find_element(By.ID, "pnnext")
                    next_btn.click()
                time.sleep(random.uniform(3, 5))
                page += 1
            except:
                break  # No more pages

    finally:
        driver.quit()

    return list(dict.fromkeys(urls))[:limit] if not callback else []

# ----------------------------
# PageSpeed / Lighthouse Scores
# ----------------------------

def get_lighthouse_scores(url, pagespeed_key):
    """Fetch all relevant Lighthouse categories and specific audits from PageSpeed API."""
    try:
        api = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {
            "url": url,
            "key": pagespeed_key,
            "category": ["performance", "accessibility", "best-practices", "seo"]
        }
        r = requests.get(api, params=params, timeout=60) # Longer timeout for PageSpeed
        data = r.json()
        
        if "lighthouseResult" not in data:
            return None, None, None, None, {}, []

        lh = data["lighthouseResult"]
        categories = lh["categories"]
        audits = lh["audits"]
        
        # 1. Main Category Scores
        performance = int(categories["performance"]["score"] * 100)
        accessibility = int(categories["accessibility"]["score"] * 100)
        best_practices = int(categories["best-practices"]["score"] * 100)
        seo = int(categories["seo"]["score"] * 100)
        
        # 2. Detailed Metrics for Weighting/Reporting
        detailed = {
            "lcp": audits.get("largest-contentful-paint", {}).get("displayValue", "N/A"),
            "cls": audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A"),
            "tbt": audits.get("total-blocking-time", {}).get("displayValue", "N/A"),
            "tap_targets": audits.get("tap-targets", {}).get("score", 1.0),
            "font_size": audits.get("font-size", {}).get("score", 1.0),
        }
        
        # 3. Identify High-Impact Failed Audits
        failed_audits = []
        high_impact_ids = [
            "tap-targets", "font-size", "color-contrast", "cumulative-layout-shift", 
            "largest-contentful-paint", "image-aspect-ratio", "unsized-images",
            "viewport", "content-width", "link-text", "images-alt"
        ]
        
        for aid in high_impact_ids:
            audit = audits.get(aid)
            if audit and audit.get("score") is not None and audit.get("score") < 0.9:
                title = audit.get("title", aid)
                desc = audit.get("description", "")
                failed_audits.append(f"{title}: {desc.split('.')[0]}.")
        
        return performance, accessibility, best_practices, seo, detailed, failed_audits

    except Exception as e:
        try:
            error_data = r.json()
            if "error" in error_data:
                st.error(f"PageSpeed API Error: {error_data['error'].get('message')}")
        except:
            pass
        return None, None, None, None, {}, []

# ----------------------------
# UI Scoring Logic
# ----------------------------

def get_light_seo_check(html, url=""):
    """Light HTML-based SEO audit (checking meta tags, headers)."""
    score = 100
    penalties = []
    
    if '<title>' not in html.lower():
        score -= 20
        penalties.append("Missing <title> tag")
    if 'name="description"' not in html.lower():
        score -= 20
        penalties.append("Missing Meta Description")
    if '<h1>' not in html.lower():
        score -= 15
        penalties.append("Missing H1 header")
    if 'alt="' not in html.lower() and '<img' in html.lower():
        score -= 10
        penalties.append("Missing Image Alt tags")
    
    # HTTPS Check
    if url.startswith("http://"):
        score -= 15
        penalties.append("Insecure Connection (HTTP)")
        
    return max(0, score), penalties

def detect_ui_issues(html):
    """Detect outdated vs modern HTML/CSS practices for a UI penalty score."""
    penalty = 0
    bonus = 0
    issues = []
    html_lower = html.lower()
    
    # ────────────────────────────────────────────────
    # 🏚️  OUTDATED / LEGACY SIGNALS  (Penalties)
    # ────────────────────────────────────────────────

    # --- Old Layout ---
    has_table  = "<table" in html_lower
    has_flex   = "display: flex" in html_lower or "display:flex" in html_lower
    has_grid   = "display: grid" in html_lower or "display:grid" in html_lower
    if has_table and not has_flex and not has_grid:
        penalty += 50    # purely table-driven layout
        issues.append("Legacy table-based layout")
    elif has_table:
        penalty += 15    # tables exist but modern layout also present
        issues.append("Mixed table + modern layout")

    # --- Deprecated HTML Tags ---
    deprecated = {
        "<font":    ("Deprecated <font> tags",    25),
        "<center>":  ("Deprecated <center> tags",  20),
        "<marquee": ("Obsolete <marquee>",          30),
        "<blink":   ("Obsolete <blink>",            30),
        "<frameset":("Obsolete frameset",           40),
        "<iframe":  ("Embedded iframe (old UX)",    10),
    }
    for tag, (msg, pts) in deprecated.items():
        if tag in html_lower:
            penalty += pts
            issues.append(msg)

    # --- Old Frameworks / Platforms ---
    old_tech = {
        "jquery-1.":          ("Old jQuery 1.x",                   20),
        "jquery/1.":          ("Old jQuery 1.x",                   20),
        "bootstrap/3":        ("Old Bootstrap 3",                  25),
        "bootstrap-2":        ("Very Old Bootstrap 2",             30),
        "mootools":           ("Outdated MooTools",                25),
        "prototype.js":       ("Outdated Prototype.js",            25),
        "scriptaculous":      ("Outdated Scriptaculous",           20),
        "__viewstate":        ("ASP.NET WebForms (Very Old)",      35),
        "__dopostback":       ("ASP.NET WebForms PostBack",        30),
        "macromedia":         ("Flash/Macromedia content",         35),
        ".swf":               ("Flash SWF embed",                  35),
        "silverlight":        ("Silverlight plugin (obsolete)",    30),
        "msofficewebs":       ("MS Office Web Components",         25),
        "dreamweaver":        ("Dreamweaver signature (old)",      15),
        "microsoft frontpage":("FrontPage signature (old)",        20),
    }
    for sig, (msg, pts) in old_tech.items():
        if sig in html_lower:
            penalty += pts
            issues.append(msg)

    # --- Excessive inline styles (maintenance debt) ---
    inline_count = html.count('style="')
    if inline_count > 30:
        penalty += 25
        issues.append(f"Heavy inline styles ({inline_count} occurrences)")
    elif inline_count > 15:
        penalty += 10
        issues.append(f"Moderate inline styles ({inline_count} occurrences)")

    # --- Mobile / Responsiveness ---
    if 'name="viewport"' not in html:
        penalty += 60          # absolutely critical for modern UX
        issues.append("Not Mobile Friendly (No viewport)")

    # --- Image Clutter ---
    soup = BeautifulSoup(html, "html.parser")
    images = soup.find_all("img")
    html_len = len(html)
    density_threshold = max(30, html_len // 2000)   # proportional
    if len(images) > density_threshold:
        penalty += 15
        issues.append(f"High image density ({len(images)} images)")

    # ────────────────────────────────────────────────
    # ✅  MODERN SIGNALS  (Bonuses — capped if site is heavily legacy)
    # ────────────────────────────────────────────────
    if penalty < 60:       # only award bonuses if not already quite bad
        modern_signals = {
            'display: flex':  8,
            'display:flex':   8,
            'display: grid':  12,
            'display:grid':   12,
            '<section':       4,
            '<main':          4,
            '<article':       3,
            '<nav':           3,
            'var(--':         8,   # CSS custom properties
            'rem;':           4,
            'vh;':            3,
        }
        for signal, value in modern_signals.items():
            if signal in html_lower:
                bonus += value
        bonus = min(bonus, 30)  # cap bonuses at 30 pts total

    return penalty - bonus, issues

def calculate_final_ui_score(performance, accessibility, best_practices, html_penalty, detailed_metrics=None, lighthouse_failed=False):
    """Combine Lighthouse metrics and HTML penalties into a final UI Score."""

    # --- Lighthouse base ---
    if lighthouse_failed or not detailed_metrics:
        # No Lighthouse data: start from 65 but drop immediately if HTML is bad
        base_score = max(30, 65 - (html_penalty * 0.5)) if html_penalty > 50 else 65
    else:
        ui_ux_modifier = (
            detailed_metrics.get("tap_targets", 1.0) * 0.5 +
            detailed_metrics.get("font_size",   1.0) * 0.5
        )
        cat_base = (
            performance    * 0.30 +
            accessibility  * 0.50 +
            best_practices * 0.20
        )
        base_score = cat_base * (0.7 + ui_ux_modifier * 0.3)

    # --- Apply HTML audit penalties 1-for-1 (no dividing) ---
    # Cap so a catastrophically bad page can't go below 5
    final_score = max(5, min(100, int(base_score - html_penalty)))

    return final_score

def get_ui_quality(score):
    if score >= 80: return "Good"
    elif score >= 60: return "Average"
    elif score >= 40: return "Poor"
    else: return "Very Poor"

# ----------------------------
# Technology Stack
# ----------------------------

def get_technology_stack(html):
    """Identify the technology stack from HTML, including outdated platforms."""
    technologies = []
    h = html.lower()

    # Modern frameworks
    if "wp-content" in h or "wordpress" in h: technologies.append("WordPress")
    if "react" in h or "_react" in h:         technologies.append("React")
    if "vue.js" in h or "vue.min.js" in h:    technologies.append("Vue.js")
    if "angular" in h:                         technologies.append("Angular")
    if "next.js" in h or "__next" in h:        technologies.append("Next.js")

    # CSS Frameworks
    if "bootstrap" in h:    technologies.append("Bootstrap")
    if "tailwindcss" in h:  technologies.append("Tailwind")
    if "foundation" in h:   technologies.append("Foundation")

    # JS Libraries
    if "jquery" in h:       technologies.append("jQuery")

    # OLD / Legacy Platforms 🚨
    if "__viewstate" in h or "webforms" in h:      technologies.append("⚠️ ASP.NET WebForms")
    if "mootools" in h:                             technologies.append("⚠️ MooTools")
    if "prototype.js" in h:                         technologies.append("⚠️ Prototype.js")
    if ".swf" in h or "macromedia" in h:            technologies.append("⚠️ Flash")
    if "silverlight" in h:                          technologies.append("⚠️ Silverlight")
    if "dreamweaver" in h:                          technologies.append("⚠️ Dreamweaver")
    if "microsoft frontpage" in h:                  technologies.append("⚠️ FrontPage")
    if "jquery-1." in h:                            technologies.append("⚠️ jQuery 1.x (Old)")
    if "bootstrap/3" in h or "bootstrap-2" in h:   technologies.append("⚠️ Bootstrap 3/2 (Old)")

    return ", ".join(technologies) if technologies else "N/A"

# ----------------------------
# Contact Information Extraction
# ----------------------------

def extract_emails(text):
    """Extract email addresses from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text, re.IGNORECASE)
    return list(set(emails))  # Remove duplicates

def extract_phone_numbers(text):
    """Extract phone numbers from text."""
    # Pattern for various phone number formats
    phone_patterns = [
        r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # 555-555-5555, 555.555.5555, 555 555 5555
        r'\b\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{4}\b',  # (555) 555-5555
        r'\b\d{10}\b',  # 5555555555
        r'\+1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # +1 555-555-5555
    ]
    
    phones = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        phones.extend(matches)
    
    return list(set(phones))  # Remove duplicates

def extract_contact_info(url):
    """Extract contact information from a website."""
    contact_info = {
        "emails": [],
        "phones": [],
        "contact_page_links": []
    }
    
    try:
        # Get homepage content
        response = requests.get(url, timeout=10)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract from homepage
        all_text = soup.get_text()
        contact_info["emails"] = extract_emails(all_text)
        contact_info["phones"] = extract_phone_numbers(all_text)
        
        # Look for contact page links
        contact_keywords = ['contact', 'about', 'team', 'staff', 'reach us']
        for link in soup.find_all("a", href=True):
            href_text = link.get_text().lower()
            href = link["href"].lower()
            
            if any(keyword in href_text or keyword in href for keyword in contact_keywords):
                full_url = urljoin(url, link["href"])
                contact_info["contact_page_links"].append(full_url)
        
        # Limit contact page links to avoid too many requests
        contact_info["contact_page_links"] = contact_info["contact_page_links"][:3]
        
        # Extract from contact pages
        for contact_url in contact_info["contact_page_links"]:
            try:
                contact_response = requests.get(contact_url, timeout=8)
                contact_html = contact_response.text
                contact_soup = BeautifulSoup(contact_html, "html.parser")
                contact_text = contact_soup.get_text()
                
                # Add any new emails/phones found
                new_emails = extract_emails(contact_text)
                new_phones = extract_phone_numbers(contact_text)
                
                contact_info["emails"].extend([e for e in new_emails if e not in contact_info["emails"]])
                contact_info["phones"].extend([p for p in new_phones if p not in contact_info["phones"]])
                
            except:
                continue
        
        # Clean up and format
        contact_info["emails"] = contact_info["emails"][:5]  # Limit to 5 emails
        contact_info["phones"] = contact_info["phones"][:5]  # Limit to 5 phones
        
    except Exception as e:
        # If extraction fails, return empty info
        pass
    
    return contact_info

def score_lead_opportunity(ui_score, perf_score, seo_score, issues):
    """Calculate how 'good' a lead is (Higher = Better Lead / Worse Site)."""
    # 0 to 100 scale
    # Convert N/A to neutral 50
    u = 50 if ui_score == "N/A" else ui_score
    p = 50 if perf_score == "N/A" else perf_score
    s = 100 if seo_score == "N/A" else seo_score # N/A SEO isn't necessarily a bad lead
    
    # We want LOW site scores to yield HIGH lead scores
    gap_ui = 100 - u
    gap_perf = 100 - p
    gap_seo = 100 - s
    
    opportunity = (gap_ui * 0.45) + (gap_perf * 0.35) + (gap_seo * 0.2)
    
    # Reasoning construction
    reasoning = []
    if u < 40: reasoning.append("Poor UI")
    if p < 50: reasoning.append("Slow performance")
    if s < 60: reasoning.append("Low SEO visibility")
    if any("Mobile" in issue for issue in issues): reasoning.append("Not Mobile Friendly")
    
    summary = " + ".join(reasoning) if reasoning else "General improvement needed"
    
    return int(max(0, min(100, opportunity))), summary

# ----------------------------
# Integrated Analysis Helper (Parallelised)
# ----------------------------

def _fetch_page(url):
    """Thread-safe single page fetch. Returns html_text or None."""
    try:
        r = requests.get(url, timeout=(3, 10), allow_redirects=True)
        return r.text
    except Exception:
        return None


def analyze_site(site, pagespeed_key, max_pages, concurrency=3, terminal_container=None):
    """Perform full analysis with parallel HTTP fetching for speed."""

    # 1. Discover pages to scan
    pages = get_pages_to_scan(site, max_pages=max_pages)

    all_seo_scores = []
    all_ui_penalties = 0
    all_tech = set()
    all_issues = []

    # 2. Fetch homepage + subpages in parallel
    if terminal_container:
        log_to_terminal(f"🚀 Starting parallel fetch with {concurrency} threads for {len(pages)} pages", level="blue")
        render_terminal(terminal_container)
    
    page_htmls = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as ex:
        # Create mapping of future to URL
        future_to_url = {ex.submit(_fetch_page, page): page for page in pages}
        
        # Collect results as they complete
        completed = 0
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                html = future.result()
                page_htmls[url] = html
                completed += 1
                if terminal_container:
                    log_to_terminal(f"✅ Fetched {completed}/{len(pages)}: {url}", level="gray")
                    render_terminal(terminal_container)
            except Exception:
                page_htmls[url] = None
                completed += 1
                if terminal_container:
                    log_to_terminal(f"❌ Failed {completed}/{len(pages)}: {url}", level="error")
                    render_terminal(terminal_container)

    # 3. Analyze homepage HTML
    homepage_html = page_htmls.get(site) or ""
    penalty, issues = detect_ui_issues(homepage_html)
    all_ui_penalties += penalty
    all_issues.extend(issues)
    all_tech.update(get_technology_stack(homepage_html).split(", "))

    # PageSpeed for homepage (external API – single sequential call)
    perf, acc, bp, seo = None, None, None, None
    detailed_metrics = {}
    if pagespeed_key:
        perf, acc, bp, seo, detailed_metrics, failed_audits = get_lighthouse_scores(site, pagespeed_key)
        if failed_audits:
            all_issues.extend(failed_audits)
    if seo is not None:
        all_seo_scores.append(seo)

    # 4. Analyze subpages (HTML already fetched)
    for subpage in pages[1:]:
        sub_html = page_htmls.get(subpage) or ""
        if sub_html:
            sub_seo, sub_penalties = get_light_seo_check(sub_html, subpage)
            all_seo_scores.append(sub_seo)
            if sub_penalties:
                all_issues.append(f"On {subpage.replace(site, '')}: " + ", ".join(sub_penalties))

    # 5. Extract contact info from already-fetched homepage; parallel-fetch contact pages
    contact_info = {"emails": [], "phones": [], "contact_page_links": []}
    try:
        soup_home = BeautifulSoup(homepage_html, "html.parser")
        home_text = soup_home.get_text()
        contact_info["emails"] = extract_emails(home_text)
        contact_info["phones"] = extract_phone_numbers(home_text)

        contact_keywords = ['contact', 'about', 'team', 'staff', 'reach us']
        for link in soup_home.find_all("a", href=True):
            href_text = link.get_text().lower()
            href = link["href"].lower()
            if any(kw in href_text or kw in href for kw in contact_keywords):
                full_url = urljoin(site, link["href"])
                if full_url not in contact_info["contact_page_links"]:
                    contact_info["contact_page_links"].append(full_url)
        contact_info["contact_page_links"] = contact_info["contact_page_links"][:3]

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as ex:
            # Create mapping of future to URL
            future_to_url = {ex.submit(_fetch_page, page): page for page in contact_info["contact_page_links"]}
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_url):
                c_html = future.result()
                if c_html:
                    c_text = BeautifulSoup(c_html, "html.parser").get_text()
                    for e in extract_emails(c_text):
                        if e not in contact_info["emails"]:
                            contact_info["emails"].append(e)
                    for p in extract_phone_numbers(c_text):
                        if p not in contact_info["phones"]:
                            contact_info["phones"].append(p)

        contact_info["emails"] = contact_info["emails"][:5]
        contact_info["phones"] = contact_info["phones"][:5]
    except Exception:
        pass

    # 7. Visual UI Analysis with Screenshot (Non-blocking)
    visual_analysis = {"visual_score": 75, "visual_issues": ["Screenshots disabled"]}
    design_analysis = {"design_score": 75, "design_issues": ["Screenshots disabled"]}
    visual_summary = {"combined_visual_score": 75, "visual_quality": "Fair", "key_issues": ["Screenshots disabled"]}
    
    try:
        # Check if screenshots are enabled
        if not enable_screenshots:
            if terminal_container:
                log_to_terminal(f"📸 Screenshots disabled - using HTML analysis only", level="info")
                render_terminal(terminal_container)
        else:
            # Capture screenshot with improved error handling
            screenshot = capture_website_screenshot(site, timeout=10, terminal_container=terminal_container)
            
            if screenshot:
                # Analyze visual quality
                visual_analysis = analyze_visual_ui_quality(screenshot)
                
                # Analyze design patterns
                design_analysis = detect_design_patterns(homepage_html, visual_analysis)
                
                # Generate summary
                visual_summary = get_visual_ui_summary(visual_analysis, design_analysis)
                
                if terminal_container:
                    log_to_terminal(f"✅ Visual analysis complete: Score {visual_summary['combined_visual_score']}/100 - {visual_summary['visual_quality']}", level="success")
                    render_terminal(terminal_container)
            else:
                # Screenshot failed but continue with HTML-only analysis
                if terminal_container:
                    log_to_terminal(f"⚠️ Screenshot failed, using HTML analysis only", level="warn")
                    render_terminal(terminal_container)
        
        # Always do design pattern analysis with HTML (even without screenshots)
        design_analysis = detect_design_patterns(homepage_html, visual_analysis)
        visual_summary = get_visual_ui_summary(visual_analysis, design_analysis)
                
    except Exception as e:
        # Any error in visual analysis shouldn't stop the whole process
        if terminal_container:
            log_to_terminal(f"⚠️ Visual analysis skipped: {str(e)}", level="warn")
            log_to_terminal(f"🔄 Continuing with standard analysis...", level="info")
            render_terminal(terminal_container)
        
        # Set reasonable defaults so the process continues
        visual_analysis = {"visual_score": 75, "visual_issues": ["Visual analysis failed"]}
        design_analysis = {"design_score": 75, "design_issues": ["Visual analysis failed"]}
        visual_summary = {"combined_visual_score": 75, "visual_quality": "Fair", "key_issues": ["Visual analysis failed"]}

    # 8. Final scoring
    avg_seo = int(sum(all_seo_scores) / len(all_seo_scores)) if all_seo_scores else (seo if seo is not None else "N/A")
    final_ui = calculate_final_ui_score(perf or 50, acc or 50, bp or 50, all_ui_penalties,
                                        detailed_metrics=detailed_metrics, lighthouse_failed=(perf is None))
    quality = get_ui_quality(final_ui)
    lead_score, lead_reason = score_lead_opportunity(
        final_ui, perf or 50, avg_seo if isinstance(avg_seo, int) else 50, all_issues
    )

    return {
        "SEO Score": avg_seo,
        "UI Score": final_ui,
        "UI Quality": quality,
        "Performance": perf if perf is not None else "N/A",
        "Accessibility": acc if acc is not None else "N/A",
        "Best Practices": bp if bp is not None else "N/A",
        "Technology": ", ".join(filter(lambda x: x != "N/A", all_tech)) or "N/A",
        "Issues": all_issues,
        "Lead Score": lead_score,
        "Lead Reason": lead_reason,
        "Pages Scanned": len(pages),
        "Emails": ", ".join(contact_info["emails"]) if contact_info["emails"] else "N/A",
        "Phone Numbers": ", ".join(contact_info["phones"]) if contact_info["phones"] else "N/A",
        "Contact Pages": len(contact_info["contact_page_links"]),
        # Visual Analysis Results
        "Visual Score": visual_summary["combined_visual_score"],
        "Visual Quality": visual_summary["visual_quality"],
        "Visual Assessment": visual_summary["visual_assessment"],
        "Visual Issues": visual_summary["key_issues"],
        "Design Score": design_analysis["design_score"],
        "Design Issues": design_analysis["design_issues"],
        "Brightness": visual_analysis["brightness"],
        "Contrast": visual_analysis["contrast"],
        "Color Diversity": visual_analysis["color_diversity"],
        "Layout Complexity": visual_analysis["layout_complexity"]
    }


# ----------------------------
# Visual UI Analysis with Screenshots
# ----------------------------

def capture_website_screenshot(url, timeout=15, width=1920, height=1080, terminal_container=None):
    """Capture a screenshot of a website using Selenium with robust error handling."""
    driver = None
    
    def log_screenshot(message, level="info"):
        """Helper to log screenshot-related messages"""
        if terminal_container:
            log_to_terminal(f"📸 {message}", level=level)
            render_terminal(terminal_container)
    
    try:
        log_screenshot(f"Starting screenshot capture for {url}", "blue")
        
        # Enhanced Chrome options for better compatibility
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Load faster, still captures layout
        options.add_argument("--disable-javascript")  # More reliable capture
        options.add_argument(f"--window-size={width},{height}")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        
        # Modern user agent
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Performance optimizations
        options.add_argument("--max_old_space_size=4096")
        options.add_argument("--memory-pressure-off")
        
        log_screenshot("Initializing Chrome driver...", "blue")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Set timeouts
        driver.set_page_load_timeout(timeout)
        driver.set_script_timeout(10)
        
        log_screenshot(f"Navigating to {url}...", "blue")
        
        # Try to load the page
        try:
            driver.get(url)
            log_screenshot("Page loaded successfully", "info")
        except TimeoutException:
            log_screenshot("Page load timeout, trying to continue...", "warn")
            # Continue anyway - we might still get a partial screenshot
        except Exception as e:
            log_screenshot(f"Navigation error: {str(e)}", "error")
            return None
        
        # Wait for page to render
        log_screenshot("Waiting for page to render...", "gray")
        time.sleep(2)
        
        # Try to scroll to ensure content is loaded
        try:
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            log_screenshot("Scrolled to top", "gray")
        except Exception as e:
            log_screenshot(f"Scroll failed: {str(e)}", "warn")
        
        # Check if page has content
        try:
            page_title = driver.title
            page_source_length = len(driver.page_source)
            log_screenshot(f"Page title: '{page_title}', Source length: {page_source_length}", "info")
            
            if page_source_length < 1000:
                log_screenshot("Page seems too small, might be error page", "warn")
        except Exception as e:
            log_screenshot(f"Could not analyze page content: {str(e)}", "warn")
        
        # Capture screenshot
        log_screenshot("Capturing screenshot...", "blue")
        try:
            screenshot = driver.get_screenshot_as_png()
            log_screenshot(f"Screenshot captured, size: {len(screenshot)} bytes", "info")
            
            if len(screenshot) < 1000:
                log_screenshot("Screenshot seems too small, might be error", "warn")
                return None
            
            # Convert to PIL Image
            img = Image.open(BytesIO(screenshot))
            log_screenshot(f"Screenshot converted to image: {img.size}", "success")
            
            return img
            
        except Exception as e:
            log_screenshot(f"Screenshot capture failed: {str(e)}", "error")
            return None
            
    except Exception as e:
        log_screenshot(f"Screenshot initialization failed: {str(e)}", "error")
        return None
        
    finally:
        # Always clean up driver
        if driver:
            try:
                driver.quit()
                log_screenshot("Chrome driver closed", "gray")
            except Exception as e:
                log_screenshot(f"Error closing driver: {str(e)}", "warn")

def analyze_visual_ui_quality(image):
    """Analyze visual UI quality from screenshot using improved computer vision."""
    if image is None:
        return {
            "visual_score": 75,  # Better default
            "brightness": 0,
            "contrast": 0,
            "color_diversity": 0,
            "edge_density": 0,
            "layout_complexity": 0,
            "visual_issues": []
        }
    
    try:
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # 1. Brightness Analysis (more lenient range)
        brightness = np.mean(gray)
        
        # 2. Contrast Analysis (more realistic thresholds)
        contrast = np.std(gray)
        
        # 3. Color Diversity (better calculation)
        unique_colors = len(np.unique(img_array.reshape(-1, 3), axis=0))
        color_diversity = min(100, (unique_colors / 5000) * 100)  # More realistic threshold
        
        # 4. Edge Density (indicates layout complexity)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size * 100
        
        # 5. Layout Complexity (contour analysis)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        layout_complexity = min(100, len(contours) / 15)  # More lenient
        
        # 6. Detect visual issues with modern design awareness
        visual_issues = []
        
        # More lenient brightness checks (modern sites often use darker/lighter themes)
        if brightness < 60:
            visual_issues.append("Very dark theme - may affect readability")
        elif brightness > 240:
            visual_issues.append("Very bright theme - may cause eye strain")
            
        # More realistic contrast thresholds
        if contrast < 20:
            visual_issues.append("Low contrast - poor visibility")
            
        # Better color diversity assessment (modern minimalism is valid)
        if color_diversity < 10:
            visual_issues.append("Very limited color palette")
        elif color_diversity > 90:
            visual_issues.append("Excessive color variety - inconsistent design")
            
        # Better layout complexity assessment
        if edge_density < 3:
            visual_issues.append("Very simple layout - may lack structure")
        elif edge_density > 50:
            visual_issues.append("Extremely complex layout - potential clutter")
        
        # Improved scoring system (more balanced)
        brightness_score = 100 - abs(brightness - 128) / 2.0  # More lenient optimal brightness
        contrast_score = min(100, contrast * 3)  # Better contrast scoring
        color_score = 100 - abs(color_diversity - 30) / 2  # More lenient color diversity
        edge_score = 100 - abs(edge_density - 20) / 2  # More lenient edge density
        
        # Weighted average with better balance
        visual_score = (brightness_score * 0.20 + contrast_score * 0.30 + 
                       color_score * 0.25 + edge_score * 0.25)
        
        return {
            "visual_score": int(max(40, min(100, visual_score))),  # Minimum 40 for functional sites
            "brightness": int(brightness),
            "contrast": int(contrast),
            "color_diversity": int(color_diversity),
            "edge_density": int(edge_density),
            "layout_complexity": int(layout_complexity),
            "visual_issues": visual_issues
        }
        
    except Exception as e:
        return {
            "visual_score": 75,  # Better fallback score
            "brightness": 0,
            "contrast": 0,
            "color_diversity": 0,
            "edge_density": 0,
            "layout_complexity": 0,
            "visual_issues": ["Visual analysis failed"]
        }

def detect_design_patterns(html_content, visual_analysis):
    """Detect modern vs outdated design patterns from HTML and visual analysis."""
    issues = []
    modern_points = 0
    
    try:
        # HTML-based analysis
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Check for responsive design
        viewport_meta = soup.find("meta", attrs={"name": "viewport"})
        if not viewport_meta:
            issues.append("No viewport meta tag - not mobile responsive")
        else:
            modern_points += 10
            
        # Check for modern CSS frameworks (expanded list)
        modern_frameworks = [
            "bootstrap", "tailwind", "foundation", "bulma", "materialize",
            "semantic-ui", "uikit", "ant-design", "chakra-ui", "mantine",
            "next.js", "react", "vue", "angular", "svelte", "gatsby"
        ]
        html_lower = html_content.lower()
        found_framework = any(fw in html_lower for fw in modern_frameworks)
        if found_framework:
            modern_points += 15
        else:
            # Don't penalize for not having framework - many modern sites use custom CSS
            modern_points += 5
            
        # Check for outdated elements (more specific)
        if "<font" in html_lower and "face=" in html_lower:
            issues.append("Uses deprecated <font> tags with face attribute")
        if "<table" in html_lower and "layout" in html_lower:
            issues.append("Uses table-based layout")
        if "marquee" in html_lower:
            issues.append("Uses deprecated <marquee> tags")
        if "<frameset" in html_lower or "<frame" in html_lower:
            issues.append("Uses deprecated frames")
        if "<blink>" in html_lower:
            issues.append("Uses deprecated <blink> tags")
            
        # Check for modern HTML5 elements
        modern_elements = ["<header>", "<nav>", "<main>", "<article>", "<section>", "<aside>", "<footer>"]
        found_modern = any(elem in html_lower for elem in modern_elements)
        if found_modern:
            modern_points += 10
            
        # Check for CSS3/Modern CSS usage
        modern_css = ["flex", "grid", "transform", "transition", "animation", "rgba(", "hsl("]
        found_modern_css = any(css in html_lower for css in modern_css)
        if found_modern_css:
            modern_points += 10
            
        # Visual-based analysis integration (more lenient)
        if visual_analysis["brightness"] < 60:
            issues.append("Very dark theme")
        if visual_analysis["contrast"] < 20:
            issues.append("Low visual contrast")
        if visual_analysis["color_diversity"] < 10:
            issues.append("Very limited color scheme")
        if visual_analysis["edge_density"] > 60:
            issues.append("Overly complex layout")
            
        # Bonus points for good visual metrics
        if 100 <= visual_analysis["brightness"] <= 180:
            modern_points += 5
        if visual_analysis["contrast"] >= 40:
            modern_points += 5
        if 20 <= visual_analysis["color_diversity"] <= 70:
            modern_points += 5
            
        # Calculate design quality score (more balanced)
        base_score = 85  # Start with good baseline for functional sites
        base_score -= len(issues) * 8  # Smaller penalty per issue
        design_score = max(40, min(100, base_score + modern_points))
        
        return {
            "design_score": design_score,
            "design_issues": issues,
            "modern_indicators": modern_points
        }
        
    except Exception as e:
        return {
            "design_score": 75,  # Better fallback
            "design_issues": ["Design analysis failed"],
            "modern_indicators": 0
        }

def get_visual_ui_summary(visual_analysis, design_analysis):
    """Generate a summary of visual UI analysis."""
    score = visual_analysis["visual_score"]
    design_score = design_analysis["design_score"]
    
    # Combine scores (more balanced weighting)
    combined_score = (score * 0.5 + design_score * 0.5)
    
    issues = visual_analysis["visual_issues"] + design_analysis["design_issues"]
    
    # Generate quality assessment (more lenient and realistic)
    if combined_score >= 85:
        quality = "Excellent"
        assessment = "Modern, professional design with best practices"
    elif combined_score >= 75:
        quality = "Very Good"
        assessment = "Well-designed with modern elements"
    elif combined_score >= 65:
        quality = "Good"
        assessment = "Solid design with minor improvements possible"
    elif combined_score >= 50:
        quality = "Fair"
        assessment = "Functional design with some outdated elements"
    else:
        quality = "Needs Improvement"
        assessment = "Design requires significant updates"
    
    return {
        "combined_visual_score": int(combined_score),
        "visual_quality": quality,
        "visual_assessment": assessment,
        "key_issues": issues[:5]  # Top 5 issues
    }

# ----------------------------
# Run Search
# ----------------------------

if 'sites' not in st.session_state:
    st.session_state.sites = []

if 'results' not in st.session_state:
    st.session_state.results = {}

if 'live_results' not in st.session_state:
    st.session_state.live_results = []

if 'terminal_logs' not in st.session_state:
    st.session_state.terminal_logs = []

# ----------------------------
# Main Search Button
# ----------------------------

# ----------------------------
# Persistent Terminal + Live Results Panel (always visible)
# ----------------------------

st.markdown("""
<div style="background: #0d0d0d; border: 1px solid #333; border-radius: 10px;
            padding: 0.5rem 0.8rem; margin-bottom: 0.8rem;">
    <span style="color:#00bbff; font-family: monospace; font-size:0.8rem;">▶ Live Progress Terminal</span>
</div>
""", unsafe_allow_html=True)
terminal_container = st.empty()    # persistent across reruns
render_terminal(terminal_container)  # always render (shows "Ready" when idle)

# Live results table (updates in-place during search)
st.markdown("""
<div style="background: var(--bg-secondary); padding: 0.6rem 1rem; border-radius: 10px;
            border: 1px solid var(--border-color); margin: 0.4rem 0;">
    <h4 style="margin: 0; color: var(--text-primary); font-size: 0.95rem;">📋 Live Results</h4>
</div>
""", unsafe_allow_html=True)
live_table_placeholder = st.empty()
csv_placeholder = st.empty()

def _refresh_live_table():
    """Rebuild the live table and CSV download button from current live_results."""
    live_results = st.session_state.get('live_results', [])
    if not live_results:
        live_table_placeholder.info("⏳ No qualified leads yet – start a search...")
        csv_placeholder.empty()
        return
    live_df = pd.DataFrame(live_results)
    live_table_placeholder.dataframe(live_df, use_container_width=True, hide_index=True)
    csv_bytes = live_df.to_csv(index=False).encode("utf-8")
    csv_placeholder.download_button(
        label=f"📥 Download CSV ({len(live_results)} leads)",
        data=csv_bytes,
        file_name="website_leads_live.csv",
        mime="text/csv",
        use_container_width=True,
        key=f"csv_live_{len(live_results)}",
    )

_refresh_live_table()   # render persisted results immediately on page load

st.markdown('<div style="text-align: center; margin: 1.5rem 0;">', unsafe_allow_html=True)

# Dynamic button text based on mode
button_text = "🚀 Find Websites" if scan_mode == "🔍 Finder Mode" else "🚀 Scan URLs"
button_help = "Start searching for websites with poor SEO/UI" if scan_mode == "🔍 Finder Mode" else "Start scanning the provided URLs"

search_button = st.button(
    button_text, 
    use_container_width=True, 
    type="primary",
    help=button_help
)
st.markdown('</div>', unsafe_allow_html=True)

# Initialize variables to avoid undefined errors
if scan_mode == "🔍 Finder Mode":
    # Variables are already defined in sidebar for Finder Mode
    pass
else:
    # For URL Scanner Mode, set defaults for Finder Mode variables
    query = ""
    selected_template = "Custom"

# Get URLs from session state if in URL Scanner Mode
if scan_mode == "📋 URL Scanner Mode":
    urls_to_scan = st.session_state.get('urls_to_scan', [])
    # Debug info
    st.write(f"Debug: Found {len(urls_to_scan)} URLs in session state")
    if urls_to_scan:
        st.write("Debug: URLs:", urls_to_scan[:3])  # Show first 3 URLs
else:
    urls_to_scan = []

if search_button:
    if scan_mode == "🔍 Finder Mode" and not query:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%); border-left: 4px solid #f87171; text-align: center;">
            <h4 style="color: #991b1b; margin: 0;">⚠️ Please Enter a Search Query</h4>
            <p style="color: #991b1b; margin: 0.5rem 0 0 0;">Select a template or enter your custom search terms to get started</p>
        </div>
        """, unsafe_allow_html=True)
    elif scan_mode == "📋 URL Scanner Mode" and not urls_to_scan:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%); border-left: 4px solid #f87171; text-align: center;">
            <h4 style="color: #991b1b; margin: 0;">⚠️ Please Enter URLs</h4>
            <p style="color: #991b1b; margin: 0.5rem 0 0 0;">Enter one or more URLs to scan (one per line)</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.session_state.sites = []
        st.session_state.results = {}
        st.session_state.live_results = []   # reset live results
        st.session_state.terminal_logs = []  # clear previous logs

        # Refresh the persistent terminal immediately to show cleared state
        render_terminal(terminal_container)
        _refresh_live_table()

        log_to_terminal(f"🚀 Starting {'search' if scan_mode == '🔍 Finder Mode' else 'URL scan'}...", level="blue")
        render_terminal(terminal_container)
        
        # Show progress
        progress_container = st.empty()
        with progress_container.container():
            if scan_mode == "🔍 Finder Mode":
                st.markdown("""
                <div class="metric-card" style="background: linear-gradient(135deg, #e0f2fe 0%, #2196f3 100%); text-align: center;">
                    <h4 style="color: white; margin: 0;">🔍 Starting Search Process</h4>
                    <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">Finding websites that match your criteria...</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #e0f2fe 0%, #2196f3 100%); text-align: center;">
                    <h4 style="color: white; margin: 0;">📋 Starting URL Scan</h4>
                    <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">Analyzing {len(urls_to_scan)} URLs...</p>
                </div>
                """, unsafe_allow_html=True)
        
        status_container = st.empty()
        results_area = st.container()
        
        # Handle URL Scanner Mode differently - OPTIMIZED
        if scan_mode == "📋 URL Scanner Mode":
            # Optimized URL scanning with parallel processing
            log_to_terminal(f"📋 URL Scanner Mode: Processing {len(urls_to_scan)} URLs (Optimized)", level="info")
            render_terminal(terminal_container)
            
            # Step 1: Quick assessment in parallel (batch processing)
            status_container.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%); text-align: center;">
                <h4 style="color: #0369a1; margin: 0;">⚡ Quick Assessment - Processing {len(urls_to_scan)} URLs</h4>
                <p style="color: #0369a1; margin: 0.5rem 0 0 0;">Fast pre-filtering to identify promising leads...</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Progress tracking
            progress_bar = st.progress(0)
            progress_text = st.empty()
            
            # Parallel quick assessment
            promising_urls = []
            processed_count = 0
            batch_size = min(10, len(urls_to_scan))  # Process in batches of 10
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                for i in range(0, len(urls_to_scan), batch_size):
                    batch = urls_to_scan[i:i+batch_size]
                    
                    # Update progress
                    progress_text.markdown(f"""
                    <div style="text-align: center; margin: 1rem 0;">
                        <h5 style="color: #0369a1; margin: 0;">🔄 Processing Batch {i//batch_size + 1}/{(len(urls_to_scan)-1)//batch_size + 1}</h5>
                        <p style="color: #0369a1; margin: 0;">Analyzing {len(batch)} URLs in parallel...</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Normalize URLs in batch
                    normalized_batch = []
                    for url in batch:
                        if not url.startswith(('http://', 'https://')):
                            url = 'https://' + url
                        
                        # Skip if already scanned
                        if is_site_already_scanned(url):
                            log_to_terminal(f"🔄 Skipping {url} - already scanned", level="gray")
                            processed_count += 1
                            progress_bar.progress(processed_count / len(urls_to_scan))
                            continue
                        
                        normalized_batch.append(url)
                    
                    if not normalized_batch:
                        continue
                    
                    # Parallel quick assessment with real-time updates
                    futures = {executor.submit(quick_site_assessment, url): url for url in normalized_batch}
                    
                    batch_results = []
                    for future in concurrent.futures.as_completed(futures):
                        url = futures[future]
                        assessment = future.result()
                        batch_results.append((url, assessment))
                        processed_count += 1
                        
                        # Update progress bar
                        progress_bar.progress(processed_count / len(urls_to_scan))
                        
                        # Show real-time assessment in browser
                        if assessment and assessment['should_analyze_fully']:
                            promising_urls.append(assessment['url'])
                            # Show promising lead in browser
                            with results_area:
                                st.markdown(f"""
                                <div class="metric-card" style="background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); border-left: 4px solid #16a34a; margin: 0.3rem 0;">
                                    <h6 style="color: #166534; margin: 0;">✅ Promising Lead Found!</h6>
                                    <p style="color: #166534; margin: 0.2rem 0; font-size: 0.9rem;">{url}</p>
                                    <small style="color: #166534; font-size: 0.8rem;">
                                        Contact: {'✓' if assessment['has_contact'] else '✗'} | 
                                        Old Tech: {'✓' if assessment['old_technology'] else '✗'} | 
                                        Poor UI: {assessment['poor_ui_indicators']} issues
                                    </small>
                                </div>
                                """, unsafe_allow_html=True)
                            log_to_terminal(f"✅ Promising lead found: {url}", level="success")
                        else:
                            # Show rejected URL in browser
                            with results_area:
                                st.markdown(f"""
                                <div class="metric-card" style="background: var(--bg-secondary); border-left: 4px solid #6b7280; margin: 0.3rem 0;">
                                    <h6 style="color: var(--text-secondary); margin: 0;">❌ Not a Lead</h6>
                                    <p style="color: var(--text-secondary); margin: 0.2rem 0; font-size: 0.9rem;">{url if assessment else 'Unknown URL'}</p>
                                    <small style="color: var(--text-secondary); font-size: 0.8rem;">
                                        No contact info or doesn't meet criteria
                                    </small>
                                </div>
                                """, unsafe_allow_html=True)
                            log_to_terminal(f"❌ Not a lead: {url if assessment else 'Unknown'}", level="gray")
                        
                        render_terminal(terminal_container)
            
            # Complete progress
            progress_bar.progress(1.0)
            progress_text.markdown(f"""
            <div style="text-align: center; margin: 1rem 0;">
                <h5 style="color: #16a34a; margin: 0;">✅ Quick Assessment Complete!</h5>
                <p style="color: #16a34a; margin: 0.5rem 0 0 0;">Found {len(promising_urls)} promising leads from {len(urls_to_scan)} URLs</p>
            </div>
            """, unsafe_allow_html=True)
            
            log_to_terminal(f"🎯 Found {len(promising_urls)} promising leads from {len(urls_to_scan)} URLs", level="info")
            render_terminal(terminal_container)
            
            # Step 2: Full analysis only for promising leads
            if promising_urls:
                # Progress tracking for full analysis
                full_progress_bar = st.progress(0)
                full_progress_text = st.empty()
                
                status_container.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); text-align: center;">
                    <h4 style="color: #166534; margin: 0;">🔍 Full Analysis - {len(promising_urls)} Promising Leads</h4>
                    <p style="color: #166534; margin: 0.5rem 0 0 0;">Detailed analysis of qualified leads...</p>
                </div>
                """, unsafe_allow_html=True)
                
                for i, url in enumerate(promising_urls):
                    if len(st.session_state.sites) >= limit:
                        break
                    
                    # Update full analysis progress
                    full_progress_text.markdown(f"""
                    <div style="text-align: center; margin: 1rem 0;">
                        <h5 style="color: #166534; margin: 0;">🔍 Analyzing Lead ({i+1}/{len(promising_urls)})</h5>
                        <p style="color: #166534; margin: 0;">{url}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    status_container.markdown(f"""
                    <div class="metric-card" style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border-left: 4px solid #16a34a; margin: 0.5rem 0;">
                        <h5 style="color: #166534; margin: 0;">🔍 Analyzing Lead ({i+1}/{len(promising_urls)})</h5>
                        <p style="color: #166534; margin: 0;">{url}</p>
                        <small style="color: #166534;">Running full analysis...</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Save as scanned
                    save_scanned_sites([url])
                    log_to_terminal(f"📝 Full analysis: {url}", level="blue")
                    render_terminal(terminal_container)
                    
                    # Analyze the site (only promising leads)
                    res = analyze_site(url, pagespeed_key, max_pages_to_scan, concurrency=concurrency, terminal_container=terminal_container)
                    
                    # Update progress
                    full_progress_bar.progress((i + 1) / len(promising_urls))
                    
                    # Calculate lead score for poor sites (inverted logic)
                    lead_score = calculate_poor_site_lead_score(res, url)
                    
                    # Apply lead filters (for poor sites)
                    if is_poor_site_lead(res, ui_filter):
                        st.session_state.results[url] = res
                        st.session_state.sites.append(url)
                        
                        # Show finding in browser
                        with results_area:
                            st.markdown(f"""
                            <div class="metric-card" style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-left: 4px solid #f59e0b; margin: 0.5rem 0;">
                                <h5 style="color: #92400e; margin: 0;">🎯 Poor Site Lead Found!</h5>
                                <p style="color: #92400e; margin: 0.25rem 0;">{url}</p>
                                <small style="color: #92400e;">
                                    Lead Score: {lead_score}/100 | 
                                    UI: {res.get('UI Score', 'N/A')} | 
                                    Has Contact: {'✓' if res.get('Emails', 'N/A') != 'N/A' else '✗'}
                                </small>
                            </div>
                            """, unsafe_allow_html=True)
                        log_to_terminal(f"🎯 Poor Site Lead Found: {url} (Score: {lead_score}/100)", level="success")
                    else:
                        # Show rejected lead in browser
                        with results_area:
                            st.markdown(f"""
                            <div class="metric-card" style="background: var(--bg-secondary); border-left: 4px solid #6b7280; margin: 0.5rem 0;">
                                <h5 style="color: var(--text-secondary); margin: 0;">❌ Doesn't Meet Criteria</h5>
                                <p style="color: var(--text-secondary); margin: 0.25rem 0;">{url}</p>
                                <small style="color: var(--text-secondary);">
                                    Not a poor site lead
                                </small>
                            </div>
                            """, unsafe_allow_html=True)
                        log_to_terminal(f"❌ {url} doesn't meet poor site criteria", level="warn")
                    
                    render_terminal(terminal_container)
                
                # Complete full analysis progress
                full_progress_bar.progress(1.0)
                full_progress_text.markdown(f"""
                <div style="text-align: center; margin: 1rem 0;">
                    <h5 style="color: #16a34a; margin: 0;">✅ Full Analysis Complete!</h5>
                    <p style="color: #16a34a; margin: 0.5rem 0 0 0;">Found {len(st.session_state.sites)} poor site leads</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                log_to_terminal(f"❌ No promising leads found in {len(urls_to_scan)} URLs", level="warn")
                render_terminal(terminal_container)
                status_container.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%); text-align: center;">
                    <h4 style="color: #991b1b; margin: 0;">❌ No Promising Leads Found</h4>
                    <p style="color: #991b1b; margin: 0.5rem 0 0 0;">None of the {len(urls_to_scan)} URLs met the lead criteria</p>
                </div>
                """, unsafe_allow_html=True)
            
            status_container.success(
                f"🎯 URL Scan complete! Found {len(st.session_state.sites)} poor site leads from {len(urls_to_scan)} URLs."
            )
        else:
            # Finder Mode - Original search logic
            def analysis_callback(site):
                """Helper to analyze and update UI in real-time during search."""
                if site in st.session_state.results:
                    return True

                # Check if site was already scanned before
                if is_site_already_scanned(site):
                    log_to_terminal(f"🔄 Skipping {site} - already scanned", level="gray")
                    render_terminal(terminal_container)
                    return len(st.session_state.sites) < limit

                lead_n = len(st.session_state.sites) + 1
                status_container.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border-left: 4px solid #16a34a; margin: 0.5rem 0;">
                    <h5 style="color: #166534; margin: 0;">🔍 Checking site ({lead_n}/{limit})</h5>
                    <p style="color: #166534; margin: 0;">{site}</p>
                </div>
                """, unsafe_allow_html=True)

                # Save site as scanned immediately to avoid duplicate scanning
                save_scanned_sites([site])
                log_to_terminal(f"🌐 [{lead_n}/{limit}] Checking: {site}", level="blue")
                render_terminal(terminal_container)

                # Validate site is active
                if not is_website_active(site):
                    log_to_terminal(f"⚠️  Inactive/unreachable — skipped: {site}", level="warn")
                    render_terminal(terminal_container)
                    return len(st.session_state.sites) < limit

                log_to_terminal(f"✅ Site is live. Starting analysis...", level="info")
                render_terminal(terminal_container)

                res = analyze_site(site, pagespeed_key, max_pages_to_scan, concurrency=concurrency, terminal_container=terminal_container)

                # Safely convert scores for comparison
                def _to_int(v):
                    try:
                        return int(v) if v not in (None, "N/A") else 0
                    except (ValueError, TypeError):
                        return 0

                ui_num   = _to_int(res.get("UI Score"))
                seo_num  = _to_int(res.get("SEO Score"))
                perf_num = _to_int(res.get("Performance"))

                log_to_terminal(f"📊 Scores → UI:{ui_num} | Perf:{perf_num} | SEO:{seo_num}", level="info")
                log_to_terminal(f"🎯 Filters → UI≤{ui_filter} | SEO≤{seo_filter} | Perf≤{perf_filter}", level="gray")
                render_terminal(terminal_container)

                meets_ui   = ui_num   <= ui_filter
                meets_seo  = seo_num  <= seo_filter
                meets_perf = perf_num <= perf_filter

                if meets_ui and meets_seo and meets_perf:
                    st.session_state.results[site] = res
                    st.session_state.sites.append(site)

                    # Flatten result into live-results row
                    row = {"URL": site}
                    flat = res.copy()
                    flat["Issues"] = "; ".join(flat.get("Issues", []))
                    flat.pop("Contact Pages", None)
                    flat.pop("Visual Issues", None)   # list — not CSV-friendly
                    flat.pop("Design Issues", None)
                    row.update(flat)
                    st.session_state.live_results.append(row)
                    _refresh_live_table()             # update live table + download btn

                    log_to_terminal(f"🏆 Lead #{len(st.session_state.sites)} added: {site}", level="info")

                    # Show finding in real-time below the terminal
                    with results_area:
                        st.markdown(f"""
                        <div class="metric-card" style="background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); border-left: 4px solid #16a34a; margin: 0.5rem 0;">
                            <h5 style="color: #166534; margin: 0;">✅ Lead #{len(st.session_state.sites)} Found!</h5>
                            <p style="color: #166534; margin: 0.25rem 0;">{site}</p>
                            <small style="color: #166534;">UI: {ui_num} | SEO: {seo_num} | Perf: {perf_num}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    reasons = []
                    if not meets_ui:   reasons.append(f"UI {ui_num} > {ui_filter}")
                    if not meets_seo:  reasons.append(f"SEO {seo_num} > {seo_filter}")
                    if not meets_perf: reasons.append(f"Perf {perf_num} > {perf_filter}")
                    log_to_terminal(f"❌ Filtered out ({', '.join(reasons)}): {site}", level="warn")

                render_terminal(terminal_container)
                return len(st.session_state.sites) < limit

            # ── Shared search-batch dispatcher ───────────────────────────────────────
            def _search_batch(offset, batch_size=10):
                """Fetch one batch of URLs using the selected provider, engine & country."""
                kwargs = dict(
                    skip_history=avoid_history,
                    manual_avoid_list=tuple(manual_avoid_list),  # hashable for safety
                    country_code=country_code,
                    engine=search_engine
                )
                if search_provider == "Zenserp":
                    return find_sites(query, batch_size, serpapi_key, offset=offset, **kwargs)
                elif search_provider == "SerpApi":
                    return serpapi_search(query, batch_size, serpapi_key_alt, offset=offset, **kwargs)
                elif search_provider == "ScraperAPI":
                    return scraperapi_search(query, batch_size, scraperapi_key, offset=offset, **kwargs)
                elif search_provider == "Bright Data":
                    return brightdata_search(query, batch_size, brightdata_key, offset=offset, **kwargs)
                elif search_provider == "Oxylabs":
                    return oxylabs_search(query, batch_size, oxylabs_key, offset=offset, **kwargs)
                elif search_provider == "Smartproxy":
                    return smartproxy_search(query, batch_size, smartproxy_key, offset=offset, **kwargs)
                elif search_provider == "ZenRows":
                    return zenrows_search(query, batch_size, zenrows_key, offset=offset, **kwargs)
                elif search_provider == "ScraperBot":
                    return scraperbot_search(query, batch_size, scraperbot_key, offset=offset, **kwargs)
                elif search_provider == "SearchAPI":
                    return searchapi_search(query, batch_size, searchapi_key, offset=offset, **kwargs)
                else:
                    return None  # Google Search uses Selenium separately

            if auto_analyze:
                if search_provider == "Google Search":
                    # Selenium path – runs until callback returns False (limit reached) or pages run out
                    google_search(
                        query, limit=limit, callback=analysis_callback,
                        skip_pages=skip_pages, skip_history=avoid_history,
                        manual_avoid_list=manual_avoid_list,
                        terminal_container=terminal_container,
                        country_code=country_code, engine=search_engine
                    )
                else:
                    # API providers – unlimited batch loop: no scan cap, stops only when leads found or results exhausted
                    offset = skip_pages * 10
                    total_scanned = 0
                    consecutive_empty = 0  # safety: stop after 3 empty batches in a row

                    while len(st.session_state.sites) < limit:
                        status_container.markdown(f"""
                        <div class="metric-card" style="background:linear-gradient(135deg,#e0f2fe,#2196f3);text-align:center;padding:0.8rem;">
                            <h5 style="color:white;margin:0;">📡 {search_provider} — {search_engine} | Country: {country_label}</h5>
                            <p style="color:rgba(255,255,255,0.9);margin:0.3rem 0 0 0;">
                                Scanned: {total_scanned} sites &nbsp;|&nbsp; ✅ Leads found: {len(st.session_state.sites)}/{limit}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

                        log_to_terminal(
                            f"Requesting batch from {search_provider} (offset {offset}, engine={search_engine}, country={country_code or 'all'})",
                            level="blue"
                        )
                        batch = _search_batch(offset)
                        render_terminal(terminal_container)

                        if not batch:
                            consecutive_empty += 1
                            if consecutive_empty >= 3:
                                log_to_terminal("⚠️ No more results from provider — stopping.", level="warn")
                                render_terminal(terminal_container)
                                break
                            offset += 10
                            continue

                        consecutive_empty = 0
                        for site in batch:
                            total_scanned += 1
                            should_continue = analysis_callback(site)
                            if not should_continue:
                                break

                        offset += 10

                # Save results to history
                if st.session_state.sites:
                    save_history(st.session_state.sites)
                status_container.success(
                    f"🎯 Search complete! Found {len(st.session_state.sites)} qualified leads."
                )
            else:
                with st.spinner("🔍 Searching websites..."):
                    if search_provider == "Google Search":
                        sites = google_search(
                            query, limit=limit, skip_pages=skip_pages,
                            skip_history=avoid_history, manual_avoid_list=manual_avoid_list,
                            country_code=country_code, engine=search_engine
                        )
                    else:
                        sites = _search_batch(offset=skip_pages * 10, batch_size=limit) or []
                st.session_state.sites = sites
                if sites:
                    save_history(sites)
                status_container.success(f"✅ Found {len(st.session_state.sites)} websites. Click 'Analyze' to audit them.")

if st.session_state.sites:
    st.markdown(f"""
    <div class="metric-card" style="text-align: center; padding: 1.5rem; margin: 1rem 0;">
        <h3 style="color: var(--text-primary);">📊 Found {len(st.session_state.sites)} Websites</h3>
        <p style="color: var(--text-secondary);">Click 'Analyze' to audit each website for SEO/UI performance and contact information</p>
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------
    # Display Sites and Actions
    # ----------------------------

    for i, site in enumerate(st.session_state.sites):
        # Determine if site should be shown based on filters
        show_site = True
        if site in st.session_state.results:
            res = st.session_state.results[site]
            ui_val = res.get("UI Score", 100)
            seo_val = res.get("SEO Score", 100)
            
            # If the score is "N/A", we treat it as 0 for filtering purposes if the filter is set low
            ui_num = 0 if ui_val == "N/A" else ui_val
            seo_num = 0 if seo_val == "N/A" else seo_val
            perf_num = 0 if res.get("Performance") == "N/A" else res.get("Performance")
            
            if ui_num > ui_filter or seo_num > seo_filter or perf_num > perf_filter:
                show_site = False

        if show_site:
            st.markdown(f"""
            <div class="metric-card" style="margin: 1rem 0; padding: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <div style="flex: 1;">
                        <h4 style="color: var(--text-primary);">🌐 {site}</h4>
                    </div>
                    <div style="display: flex; gap: 0.5rem;">
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.write("")  # Space for URL
            with col2:
                if st.button("🔍 Analyze", key=f"analyze_{i}", use_container_width=True):
                    with st.spinner(f"🔍 Analyzing {site}..."):
                        log_to_terminal(f"🔍 Manual analyze: {site}", level="blue")
                        render_terminal(terminal_container)
                        if is_site_already_scanned(site):
                            log_to_terminal(f"ℹ️ Already scanned previously: {site}", level="gray")
                            render_terminal(terminal_container)
                        else:
                            save_scanned_sites([site])
                        if is_website_active(site):
                            log_to_terminal(f"✅ Site is live — running full analysis...", level="info")
                            render_terminal(terminal_container)
                            result = analyze_site(site, pagespeed_key, max_pages_to_scan, concurrency=concurrency, terminal_container=terminal_container)
                            st.session_state.results[site] = result
                            log_to_terminal(f"🏁 Analysis complete for {site}", level="info")
                            render_terminal(terminal_container)
                        else:
                            log_to_terminal(f"⚠️ {site} appears to be offline — skipped.", level="warn")
                            render_terminal(terminal_container)
                            st.warning(f"⚠️ {site} appears to be offline.")
                        st.rerun()
            with col3:
                if st.button("❌ Remove", key=f"remove_{i}", use_container_width=True):
                    st.session_state.sites.pop(i)
                    if site in st.session_state.results:
                        del st.session_state.results[site]
                    st.rerun()

            if site in st.session_state.results:
                res = st.session_state.results[site]
                
                # Primary Lead Opportunity Highlight
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fef3c7 0%, #fff7ed 100%); padding: 1rem; border-radius: 8px; margin: 1rem 0; border: 1px solid #fbbf24;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="color: #92400e; font-weight: 700; font-size: 1.1rem;">💎 Lead Opportunity Score: {res.get('Lead Score', 'N/A')}/100</span>
                            <p style="color: #b45309; margin: 0.2rem 0 0 0; font-weight: 500;">{res.get('Lead Reason', 'High potential lead')}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Main metrics with better styling
                st.markdown(f"""
                <div style="background: var(--bg-secondary); padding: 1rem; border-radius: 8px; margin: 1rem 0; border: 1px solid var(--border-color);">
                    <h5 style="color: var(--text-primary);">📈 Technical Scores</h5>
                </div>
                """, unsafe_allow_html=True)
                
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                with m_col1:
                    st.metric("UI Score", f"{res['UI Score']}/100", res['UI Quality'])
                with m_col2:
                    st.metric("SEO Score", res['SEO Score'])
                with m_col3:
                    st.metric("Performance", res['Performance'])
                with m_col4:
                    st.metric("Accessibility", res['Accessibility'])
                
                # Visual Analysis Section
                if 'Visual Score' in res:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%); padding: 1rem; border-radius: 8px; margin: 1rem 0; border: 1px solid #0ea5e9;">
                        <h5 style="color: #0369a1; margin: 0;">🎨 Visual UI Analysis</h5>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Visual metrics
                    v_col1, v_col2, v_col3, v_col4 = st.columns(4)
                    with v_col1:
                        st.metric("Visual Score", f"{res.get('Visual Score', 'N/A')}/100", res.get('Visual Quality', 'N/A'))
                    with v_col2:
                        st.metric("Design Score", f"{res.get('Design Score', 'N/A')}/100")
                    with v_col3:
                        st.metric("Brightness", res.get('Brightness', 'N/A'))
                    with v_col4:
                        st.metric("Contrast", res.get('Contrast', 'N/A'))
                    
                    # Visual assessment
                    st.markdown(f"""
                    <div style="background: var(--bg-secondary); padding: 1rem; border-radius: 8px; margin: 1rem 0; border: 1px solid var(--border-color);">
                        <h6 style="color: var(--text-primary);">📊 Visual Assessment</h6>
                        <p style="color: var(--text-secondary); margin: 0.5rem 0;">{res.get('Visual Assessment', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Visual issues
                    if res.get('Visual Issues') and res['Visual Issues'] != []:
                        st.markdown(f"""
                        <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: 8px; border-left: 4px solid #f59e0b;">
                            <strong style="color: var(--text-primary);">⚠️ Visual Issues Detected:</strong><br>
                            <small style="color: var(--text-secondary);">{' • '.join(res['Visual Issues'][:5])}</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Contact information section
                if res.get('Emails') != 'N/A' or res.get('Phone Numbers') != 'N/A':
                    st.markdown(f"""
                    <div style="background: var(--bg-secondary); padding: 1rem; border-radius: 8px; margin: 1rem 0; border: 1px solid var(--border-color);">
                        <h5 style="color: var(--text-primary);">📞 Contact Information</h5>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c_col1, c_col2 = st.columns(2)
                    with c_col1:
                        if res.get('Emails') != 'N/A':
                            st.markdown(f"""
                            <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: 8px; border-left: 4px solid var(--accent-color);">
                                <strong style="color: var(--text-primary);">📧 Emails:</strong><br>
                                <small style="color: var(--text-secondary);">{res['Emails']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    with c_col2:
                        if res.get('Phone Numbers') != 'N/A':
                            st.markdown(f"""
                            <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: 8px; border-left: 4px solid var(--accent-color);">
                                <strong style="color: var(--text-primary);">📱 Phone Numbers:</strong><br>
                                <small style="color: var(--text-secondary);">{res['Phone Numbers']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Secondary metrics
                st.markdown(f"""
                <div style="background: var(--bg-secondary); padding: 1rem; border-radius: 8px; margin: 1rem 0; border: 1px solid var(--border-color);">
                    <h5 style="color: var(--text-primary);">⚙️ Technical Details</h5>
                </div>
                """, unsafe_allow_html=True)
                
                s_col1, s_col2, s_col3 = st.columns([1, 1, 2])
                with s_col1:
                    st.metric("Best Practices", res['Best Practices'])
                with s_col2:
                    st.markdown(f"""
                    <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: 8px; margin-top: 0.5rem; border: 1px solid var(--border-color);">
                        <strong style="color: var(--text-primary);">🛠️ Technology:</strong><br>
                        <small style="color: var(--text-secondary);">{res['Technology']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                if res['Issues']:
                    with s_col3:
                        with st.expander("⚠️ UI Issues Detected"):
                            for issue in res['Issues']:
                                st.write(f"• {issue}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<hr class="st-hr">', unsafe_allow_html=True)

    # Only show "Analyze All" if there are unanalyzed sites
    unanalyzed_sites = [s for s in st.session_state.sites if s not in st.session_state.results]
    if unanalyzed_sites:
        if st.button("📊 Analyze All Remaining"):
            with st.spinner("Analyzing websites..."):
                log_to_terminal(f"📊 Analyze All: processing {len(unanalyzed_sites)} remaining sites", level="blue")
                render_terminal(terminal_container)
                for idx, site in enumerate(unanalyzed_sites, 1):
                    log_to_terminal(f"🌐 [{idx}/{len(unanalyzed_sites)}] {site}", level="blue")
                    render_terminal(terminal_container)
                    if is_site_already_scanned(site):
                        log_to_terminal(f"ℹ️ Already scanned — skipping: {site}", level="gray")
                        render_terminal(terminal_container)
                        continue
                    save_scanned_sites([site])
                    if is_website_active(site):
                        result = analyze_site(site, pagespeed_key, max_pages_to_scan, concurrency=concurrency, terminal_container=terminal_container)
                        st.session_state.results[site] = result
                        log_to_terminal(f"✅ Done: {site}", level="info")
                        render_terminal(terminal_container)
                    else:
                        log_to_terminal(f"⚠️ Offline — skipped: {site}", level="warn")
                        render_terminal(terminal_container)
            st.rerun()

    # ----------------------------
    # Export and Clear
    # ----------------------------

    if st.session_state.results:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center; padding: 2rem; margin: 2rem 0;">
            <h3 style="color: var(--text-primary);">📋 Filtered Leads (Ready for Export)</h3>
            <p style="color: var(--text-secondary);">Download your qualified leads with contact information and analysis data</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Prepare data for DataFrame with filters applied
        export_data = []
        for url, metrics in st.session_state.results.items():
            ui_val = metrics.get("UI Score", 100)
            seo_val = metrics.get("SEO Score", 100)
            ui_num = 0 if ui_val == "N/A" else ui_val
            seo_num = 0 if seo_val == "N/A" else seo_val

            # Only export what matches the current filter
            if ui_num <= ui_filter and seo_num <= seo_filter:
                row = {"URL": url}
                # Flatten metrics, convert issues list to string
                flat_metrics = metrics.copy()
                if "Issues" in flat_metrics:
                    flat_metrics["Issues"] = ", ".join(flat_metrics["Issues"])
                row.update(flat_metrics)
                export_data.append(row)

        if export_data:
            df = pd.DataFrame(export_data)
            
            # Styled data display
            st.markdown(f"""
            <div style="background: var(--bg-secondary); padding: 1rem; border-radius: 8px; margin: 1rem 0; border: 1px solid var(--border-color);">
                <h5 style="color: var(--text-primary);">📊 Lead Summary</h5>
            </div>
            """, unsafe_allow_html=True)
            
            st.dataframe(df, use_container_width=True)

            # Export buttons with better styling
            st.markdown(f"""
            <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: 8px; margin: 1rem 0; text-align: center; border: 1px solid var(--border-color);">
                <h5 style="color: var(--text-primary);">💾 Export Options</h5>
                <p style="color: var(--text-secondary);">Choose your preferred format for downloading the lead data</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)

            with col1:
                # Export to Excel – in-memory (no temp file)
                import io as _io
                excel_buf = _io.BytesIO()
                df.to_excel(excel_buf, index=False, engine="openpyxl")
                st.download_button(
                    "📥 Download Excel Report",
                    data=excel_buf.getvalue(),
                    file_name="website_leads_with_contacts.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            with col2:
                # Export to CSV – in-memory
                csv_buf = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Download CSV Report",
                    data=csv_buf,
                    file_name="website_leads_with_contacts.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.markdown(f"""
            <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: 8px; margin: 1rem 0; text-align: center; border-left: 4px solid var(--accent-color);">
                <h5 style="color: var(--text-primary);">⚠️ No Results Match Filters</h5>
                <p style="color: var(--text-secondary);">Try adjusting your UI/SEO filters to see more results</p>
            </div>
            """, unsafe_allow_html=True)

    # Clear button with styling
    if st.session_state.sites:
        st.markdown('<div style="text-align: center; margin: 2rem 0;">', unsafe_allow_html=True)
        if st.button("🗑️ Clear All Results", use_container_width=True):
            st.session_state.sites = []
            st.session_state.results = {}
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
