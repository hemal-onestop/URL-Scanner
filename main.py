import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from googlesearch import search
from Wappalyzer import Wappalyzer, WebPage
import time
import concurrent.futures
import plotly.express as px
import io

# PageSpeed API
PAGESPEED_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# Set page config for a more premium feel
st.set_page_config(page_title="Lead Finder Pro", page_icon="🔍", layout="wide")

# Custom CSS for glassmorphism and modern UI
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# GOOGLE SEARCH
# ---------------------------------------------------

def find_sites(query, limit):
    urls = []
    try:
        # Using a slight delay to avoid immediate rate limiting
        for url in search(query, num_results=limit):
            urls.append(url)
            time.sleep(1) # Small delay to be polite to Google
    except Exception as e:
        st.error(f"Search error: {e}")
    return urls


# ---------------------------------------------------
# TECHNOLOGY DETECTION
# ---------------------------------------------------

def detect_tech(url):
    try:
        wappalyzer = Wappalyzer.latest()
        webpage = WebPage.new_from_url(url, timeout=10)
        tech = wappalyzer.analyze(webpage)
        return list(tech)
    except:
        return []


# ---------------------------------------------------
# HTML UI DETECTION
# ---------------------------------------------------

def detect_ui_issues(url):
    score = 0
    try:
        response = requests.get(url, timeout=10)
        html = response.text.lower()
        
        # Outdated elements
        if "<table" in html and "<div" not in html: # Table based layout
            score += 25
        if "<font" in html:
            score += 20
        if "<frameset" in html or "<frame" in html:
            score += 30
        if "marquee" in html:
            score += 15
        
        # Outdated libraries
        if "jquery-1." in html or "jquery-2." in html:
            score += 15
        if "bootstrap/3" in html or "bootstrap@3" in html:
            score += 15
            
        # Lack of modern responsiveness clues
        if "viewport" not in html:
            score += 20
        if "flex" not in html and "grid" not in html: # Likely non-responsive
            score += 15

    except:
        pass
    return score


# ---------------------------------------------------
# PAGESPEED CHECK
# ---------------------------------------------------

def check_pagespeed(url):
    try:
        params = {
            "url": url,
            "strategy": "mobile"
        }
        r = requests.get(PAGESPEED_API, params=params, timeout=30)
        data = r.json()
        score = data["lighthouseResult"]["categories"]["performance"]["score"]
        return score * 100
    except:
        return 0


# ---------------------------------------------------
# LEAD SCORING
# ---------------------------------------------------

def score_lead(pagespeed, ui_score, tech):
    score = 0
    # Higher score = Better lead (meaning worse website)
    
    if pagespeed < 40:
        score += 40
    elif pagespeed < 60:
        score += 20

    if ui_score > 40:
        score += 40
    elif ui_score > 20:
        score += 20

    # Tech debt indicators
    outdated_tech = ["WordPress", "jQuery", "PHP", "Bootstrap"]
    for t in outdated_tech:
        if t in tech:
            score += 5

    return min(score, 100)


# ---------------------------------------------------
# ANALYZE WEBSITE
# ---------------------------------------------------

def analyze_site(url):
    # Performance improvement: Run tech and UI detection
    # PageSpeed can be very slow, so we do it last
    tech = detect_tech(url)
    ui_score = detect_ui_issues(url)
    pagespeed = check_pagespeed(url)
    lead_score = score_lead(pagespeed, ui_score, tech)

    return {
        "URL": url,
        "Technology": ", ".join(tech),
        "PageSpeed": round(pagespeed, 1),
        "UI Issue Score": ui_score,
        "Lead Score": lead_score
    }


# ---------------------------------------------------
# UI
# ---------------------------------------------------

def main():
    st.title("🚀 Real Estate Lead Finder Pro")
    st.subheader("Identify high-value leads with outdated web presence")

    with st.sidebar:
        st.header("Search Settings")
        query = st.text_input("Search Keyword", "real estate agencies in Florida")
        limit = st.slider("Max Websites", 10, 100, 20)
        concurrency = st.slider("Concurrency", 1, 10, 5)
        
        st.info("💡 High concurrency is faster but may trigger API blocks.")

    if st.button("Start Discovery Scan"):
        results = []
        
        st.markdown("### 🔍 1. Discovery Phase")
        with st.spinner("Searching Google for candidate sites..."):
            sites = find_sites(query, limit)
            st.success(f"Found {len(sites)} potential sites.")

        if not sites:
            st.warning("No sites found. Try a different keyword.")
            return

        st.markdown("### ⚙️ 2. Analysis Phase")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Using ThreadPoolExecutor for concurrent analysis
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_url = {executor.submit(analyze_site, url): url for url in sites}
            
            for i, future in enumerate(concurrent.futures.as_completed(future_to_url)):
                url = future_to_url[future]
                try:
                    data = future.result()
                    results.append(data)
                except Exception as exc:
                    st.error(f"{url} generated an exception: {exc}")
                
                progress = (i + 1) / len(sites)
                progress_bar.progress(progress)
                status_text.text(f"Analyzed {i+1}/{len(sites)}: {url}")

        if results:
            df = pd.DataFrame(results)
            st.markdown("---")
            st.markdown("### 📊 3. Lead Intelligence")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Scanned", len(results))
            col2.metric("High Quality Leads", len(df[df["Lead Score"] > 60]))
            col3.metric("Avg PageSpeed", f"{round(df['PageSpeed'].mean(), 1)}")

            # Visualizations
            fig = px.scatter(df, x="PageSpeed", y="UI Issue Score", 
                             size="Lead Score", color="Lead Score",
                             hover_name="URL", title="Lead Heatmap (Size = Priority)")
            st.plotly_chart(fig, use_container_width=True)

            # Results Table
            st.dataframe(df.sort_values(by="Lead Score", ascending=False), 
                         use_container_width=True)

            # Exports
            st.markdown("### 💾 4. Export Data")
            
            # Excel export
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Leads')
            excel_data = output.getvalue()

            st.download_button(
                label="📥 Download Excel Report",
                data=excel_data,
                file_name="real_estate_lead_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV Report",
                data=csv,
                file_name="real_estate_lead_report.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
