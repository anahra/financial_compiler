import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pydeck as pdk
import os
import random
from utils.styles import load_css
from utils.data_loader import COMPANIES, get_company_info, get_financials
from utils.rag_engine import RAGEngine

# Page Config
# ... imports ...

# Page Config
st.set_page_config(
    page_title="Argus",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.real_retail_data import COSTCO_LOCATIONS, WALMART_LOCATIONS, TARGET_LOCATIONS, KROGER_LOCATIONS, KROGER_SUB_LOCATIONS

# Custom CSS to maximize width and reduce padding
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    # Allow password to be set via secrets, default to "8191"
    correct_password = st.secrets.get("APP_PASSWORD", "8191")
    if st.session_state.get("password_input") == correct_password:
        st.session_state.authenticated = True
    else:
        st.error("⛔ Access Denied: Invalid Security Clearance")

if not st.session_state.authenticated:
    st.markdown("""
        <style>
        .stApp {
            background-color: #0f172a;
            color: white;
        }
        .auth-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 80vh;
            flex-direction: column;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #3b82f6;'>👁️ ARGUS</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #94a3b8;'>Restricted Access System</h3>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: #334155;'>", unsafe_allow_html=True)
        
        st.text_input("Enter Security PIN", type="password", key="password_input", on_change=check_password)
        st.caption("Enter authorized PIN to proceed.")
        
    st.stop() # Stop execution until authenticated

# ... Main App Code continues below ...

# Load Custom CSS
st.markdown(load_css(), unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "AI Analyst", "Supply Chain"])

st.sidebar.markdown("---")
st.sidebar.info("Data compiled from official sources and Yahoo Finance API.")

def format_currency(value, currency):
    if value is None:
        return "N/A"
    if value > 1e9:
        return f"{currency} {value/1e9:.2f}B"
    elif value > 1e6:
        return f"{currency} {value/1e6:.2f}M"
    return f"{currency} {value:.2f}"

def get_transcript_path(company_name):
    # Mapping company names to potential transcript files
    # KMB -> KMB_Q3_2024.txt
    mapping = {
        "Kimberly-Clark": "KMB_Q3_2024.txt",
        "Essity": "Essity_Q3_2024.txt",
        "Ontex": "Ontex_Q3_2024.txt"
    }
    filename = mapping.get(company_name)
    if filename:
        # Search recursively
        for root, dirs, files in os.walk("documents"):
            if filename in files:
                return os.path.join(root, filename)
    return None
    return None

if page == "Dashboard":
    selected_company = st.sidebar.selectbox("Select Company", ["Overview"] + list(COMPANIES.keys()))

    if selected_company == "Overview":
        st.title("ARGUS")
        st.caption("Strategic Market Observation System")
        st.markdown("### Competitive Landscape: Hygiene & Personal Care")
        
        # Summary Metrics
        cols = st.columns(len(COMPANIES))
        for idx, (name, data) in enumerate(COMPANIES.items()):
            info = get_company_info(name)
            with cols[idx]:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{name}</h4>
                    <p style="font-size: 0.9rem; color: #94a3b8;">{data['type']}</p>
                    <h3 style="color: #60a5fa;">{format_currency(info.get('market_cap'), info.get('currency', '')) if info else 'Loading...'}</h3>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Quick Access to Official Sources")
        
        for name, data in COMPANIES.items():
            with st.expander(f"{name} - Official Links"):
                st.markdown(f"**Investor Relations / Official Site:** [{data['ir_url']}]({data['ir_url']})")
                if data['type'] == 'Public':
                    st.info(f"Publicly Traded: {data['ticker']}")
                    
                    # Check for Transcript Link in Overview too
                    t_path = get_transcript_path(name)
                    if t_path:
                        with open(t_path, "r", encoding="utf-8", errors="ignore") as f:
                           st.download_button(
                               label=f"Download {name} Q3 Transcript/Summary",
                               data=f,
                               file_name=os.path.basename(t_path),
                               mime="text/plain"
                           )
                else:
                    st.warning("Private Company - Limited Public Data")

    else:
        # Company Detail Page
        info = get_company_info(selected_company)
        
        st.title(selected_company)
        st.markdown(f"**{info.get('sector', '')} | {info.get('industry', '')}**")
        
        # Top Metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Type", info['type'])
        with m2:
            st.metric("Currency", info.get('currency', 'N/A'))
        with m3:
            price = info.get('current_price')
            st.metric("Stock Price", f"{price:.2f}" if price else "N/A")
        with m4:
            st.metric("Market Cap", format_currency(info.get('market_cap'), info.get('currency', '')))
            
        st.markdown("---")
        
        # Main Content
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("Company Profile")
            st.write(info.get('long_summary'))
            
            # Transcript Section
            st.markdown("### 📄 Earnings Call Transcripts")
            
            # Simple keyword matching to find relevant files
            transcript_files = []
            # Simple keyword matching to find relevant files
            transcript_files = []
            if os.path.exists("documents"):
                for root, dirs, files in os.walk("documents"):
                    for f in files:
                        # Check if company ticker or name part is in filename
                        # Mapping: KMB -> Kimberly, Essity -> Essity, Ontex -> Ontex
                        identifiers = []
                        if selected_company == "Kimberly-Clark":
                            identifiers = ["KMB", "Kimberly"]
                        elif selected_company == "Essity":
                            identifiers = ["Essity"]
                        elif selected_company == "Ontex":
                            identifiers = ["Ontex"]
                        
                        if any(i in f for i in identifiers) and f.endswith(".txt"):
                            # Store full relative path for usage
                            transcript_files.append(os.path.join(root, f))
            
            if transcript_files:
                # Create a mapping for display {filename: full_path}
                file_map = {os.path.basename(f): f for f in transcript_files}
                sorted_filenames = sorted(list(file_map.keys()), reverse=True)
                
                selected_filename_only = st.selectbox("Select Transcript", sorted_filenames)
                t_path = file_map[selected_filename_only]
                
                with st.expander(f"Read {selected_filename_only}", expanded=False):
                    with open(t_path, "r", encoding="utf-8", errors="ignore") as f:
                        transcript_text = f.read()
                        st.text_area("Full Text", transcript_text, height=300)
                
                with open(t_path, "r", encoding="utf-8", errors="ignore") as f:
                    st.download_button(
                        label=f"Download {selected_filename_only}",
                        data=f,
                        file_name=selected_filename_only,
                        mime="text/plain"
                    )
            else:
                st.info("No transcripts found for this company.")
            
            # Additional Documents Section
            st.markdown("### 📚 Knowledge Base (Reports, Interviews, Q&A)")
            
            # recursive search for documents
            doc_structure = {}
            if os.path.exists("documents"):
                for root, dirs, files in os.walk("documents"):
                    for file in files:
                        # Check company filter
                        identifiers = []
                        if selected_company == "Kimberly-Clark":
                            identifiers = ["KMB", "Kimberly", "Clark"] # broader match
                        elif selected_company == "Essity":
                            identifiers = ["Essity"]
                        elif selected_company == "Ontex":
                            identifiers = ["Ontex"]
                        
                        # Very broad matching for KMB since we moved files
                        if selected_company == "Kimberly-Clark":
                             if any(i.lower() in file.lower() for i in identifiers) or "Earnings" in file or "Annual_Report" in file or "Presentation" in file:
                                 # organize by folder (year)
                                 folder_name = os.path.basename(root)
                                 if folder_name == "documents":
                                     folder_name = "Uncategorized"
                                 
                                 if folder_name not in doc_structure:
                                     doc_structure[folder_name] = []
                                 doc_structure[folder_name].append(os.path.join(root, file))

            if doc_structure:
                # Year selector
                years = sorted(doc_structure.keys(), reverse=True)
                selected_year = st.selectbox("Select Year/Category", years)
                
                if selected_year:
                    files_in_year = doc_structure[selected_year]
                    files_in_year.sort() # sort alphabetically
                    
                    # File selector
                    # Human readable names
                    file_map = {os.path.basename(f): f for f in files_in_year}
                    selected_file_name = st.selectbox("Select Document", list(file_map.keys()))
                    
                    if selected_file_name:
                        d_path = file_map[selected_file_name]
                        file_ext = os.path.splitext(d_path)[1].lower()
                        
                        with st.expander(f"Preview {selected_file_name}", expanded=True):
                            if file_ext == ".txt":
                                with open(d_path, "r", encoding="utf-8", errors="ignore") as f:
                                    doc_text = f.read()
                                    st.text_area("Content", doc_text, height=400)
                            elif file_ext in [".xlsx", ".xls"]:
                                try:
                                    df = pd.read_excel(d_path)
                                    st.dataframe(df.head(50)) # Show top 50 rows
                                    st.caption("Showing first 50 rows of the first sheet.")
                                except Exception as e:
                                    st.error(f"Error reading Excel file: {e}")
                            else:
                                st.info(f"Preview not available for {file_ext} files. File located at: {d_path}")
            else:
                st.info("No additional documents found.")
            
            if info['type'] == 'Public':
                st.subheader("Financials (Annual)")
                fin_data = get_financials(selected_company)
                if fin_data is not None:
                    st.dataframe(fin_data, use_container_width=True)
                else:
                    st.write("Financial data unavailable.")
            else:
                st.subheader("Financial Estimates")
                st.info("As a private company, detailed financial statements are not publicly disclosed.")
                
        with c2:
            st.subheader("Official Resources")
            st.markdown(f"""
            <div class="metric-card">
                <a href="{info['ir_url']}" target="_blank" style="text-decoration: none; color: white;">
                    <button style="width: 100%; padding: 10px; background: #2563eb; border: none; border-radius: 5px; cursor: pointer;">
                        Visit Investor Relations ➜
                    </button>
                </a>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### Recent Updates")
            st.caption("No live news feed connected yet.")

elif page == "AI Analyst":
    st.title("AI Strategic Analyst")
    st.markdown("Ask strategic questions about supply chain, innovation, and market positioning.")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        provider = st.selectbox("Select Intelligence Provider", ["OpenAI", "Perplexity"], index=1)
    with col_p2:
        # Load from secrets if available
        default_key = ""
        try:
             # Just use provider to check
            if provider == "Perplexity" and "PERPLEXITY_API_KEY" in st.secrets:
                default_key = st.secrets["PERPLEXITY_API_KEY"]
            elif provider == "OpenAI" and "OPENAI_API_KEY" in st.secrets:
                default_key = st.secrets["OPENAI_API_KEY"]
        except (FileNotFoundError, KeyError):
            pass # No secrets file or key
            
        api_key = st.text_input(f"{provider} API Key", value=default_key, type="password")
    
    if not api_key:
        st.warning(f"Please enter your {provider} API Key to proceed.")
        st.caption("Perplexity Pro users can generate API keys at settings.perplexity.ai")
    elif provider == "OpenAI" and api_key.startswith("pplx-"):
        st.error("You selected 'OpenAI' but entered a Perplexity API Key (starts with 'pplx-'). Please switch the provider to 'Perplexity'.")
    elif provider == "Perplexity" and api_key.startswith("sk-") and not api_key.startswith("sk-or-"):
        st.warning("You selected 'Perplexity' but this looks like an OpenAI Key. Please check your selection.")
    else:
        # Check if engine needs re-initialization (if provider or key changed)
        if 'rag_engine' not in st.session_state or \
           st.session_state.get('rag_provider') != provider or \
           st.session_state.get('rag_key') != api_key:
            
            with st.spinner(f"Initializing AI Engine with {provider} and Local Embeddings..."):
                transcripts_dir = os.path.join(os.getcwd(), "documents")
                rag = RAGEngine(transcripts_dir, api_key, provider=provider)
                status = rag.process_documents()
                st.session_state['rag_engine'] = rag
                st.session_state['rag_provider'] = provider
                st.session_state['rag_key'] = api_key
                if "Successfully" in status:
                    st.success(status)
                else:
                    st.error(status)
        
        # Chat Interface
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask about supply chain impacts..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing Transcripts..."):
                    response = st.session_state['rag_engine'].answer_question(prompt)
                    st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})

elif page == "Supply Chain":
    st.title("Supply Chain Network Optimization")
    st.markdown("Visualize and simulate material flow from Manufacturing to Distribution.")

    # 1. Configuration Section (Updated with KC Specifics)
    st.markdown("##### Supply Chain Configuration")
    
    # Manufacturing Sites (Mega-Hubs)
    st.sidebar.markdown("**Mega-Hubs (Mfg + Dist)**") # Smaller bold title
    factories = [
        {"name": "Beech Island, SC", "lat": 33.4757, "lon": -81.9365, "volume": 13, "role": "Southeast & East Coast Hub"},
        {"name": "Ogden, UT", "lat": 41.2230, "lon": -111.9738, "volume": 13, "role": "West Coast Hub"},
        {"name": "Paris, TX", "lat": 33.6609, "lon": -95.5555, "volume": 13, "role": "Central/South Hub"},
        {"name": "Warren, OH (Const.)", "lat": 41.2376, "lon": -80.8184, "volume": 0, "role": "Future Northeast/Midwest Hub"}
    ]
    
    factory_configs = []
    # Make Configs more compact
    for idx, f in enumerate(factories):
        active = "Const" not in f['name']
        if active:
             # Using on_change=None implies standard behavior (run on release). 
             # Streamlit reruns the whole script. 
             # To make it "smoother", we rely on efficient plotting.
             vol = st.sidebar.slider(f"{f['name']}", 0, 150, f['volume'], key=f"slider_{f['name']}")
             factory_configs.append({**f, "volume": vol})
        else:
             factory_configs.append(f)

    # Regional DCs (Mixing Centers)
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Regional Mixing Centers**") # Smaller bold title
    default_dcs = [
        {"name": "Redlands, CA", "lat": 34.0556, "lon": -117.1825, "role": "West Coast Mega DC"},
        {"name": "Wilmer, TX", "lat": 32.6065, "lon": -96.6908, "role": "South/Central Hub"},
        {"name": "McDonough, GA", "lat": 33.4473, "lon": -84.1469, "role": "Southeast Logistics Hub"},
        {"name": "New Milford, CT", "lat": 41.5770, "lon": -73.4079, "role": "Northeast Satellite"},
        {"name": "DuPont, WA", "lat": 47.0989, "lon": -122.6375, "role": "Northwest Regional DC"},
        {"name": "Mississauga, ON", "lat": 43.5890, "lon": -79.6441, "role": "Canada Primary DC"}
    ]
    
    # Define Regional Demand Centers of Gravity (Population Weighted)
    # Instead of generic state centers, we use key metro hubs that act as regional gravity centers
    regions = [
        # West Coast & Mountain
        {"name": "Los Angeles, CA", "lat": 34.0522, "lon": -118.2437},     # 0
        {"name": "San Diego, CA", "lat": 32.7157, "lon": -117.1611},       # 1
        {"name": "Seattle, WA", "lat": 47.6062, "lon": -122.3321},         # 2
        {"name": "Vancouver, BC", "lat": 49.2827, "lon": -123.1207},       # 3
        {"name": "Salt Lake City, UT", "lat": 40.7608, "lon": -111.8910},   # 4
        {"name": "Phoenix, AZ", "lat": 33.4484, "lon": -112.0740},         # 5
        {"name": "Denver, CO", "lat": 39.7392, "lon": -104.9903},          # 6
        
        # South Central
        {"name": "Dallas-Fort Worth, TX", "lat": 32.7767, "lon": -96.7970},# 7
        {"name": "Houston, TX", "lat": 29.7604, "lon": -95.3698},          # 8
        {"name": "San Antonio, TX", "lat": 29.4241, "lon": -98.4936},      # 9
        {"name": "Memphis, TN", "lat": 35.1495, "lon": -90.0490},          # 10
        
        # Midwest
        {"name": "Chicago, IL", "lat": 41.8781, "lon": -87.6298},          # 11
        {"name": "Detroit, MI", "lat": 42.3314, "lon": -83.0458},          # 12
        {"name": "Indianapolis, IN", "lat": 39.7684, "lon": -86.1581},     # 13
        {"name": "Columbus, OH", "lat": 39.9612, "lon": -82.9988},         # 14
        
        # Southeast
        {"name": "Nashville, TN", "lat": 36.1627, "lon": -86.7816},        # 15
        {"name": "Atlanta, GA", "lat": 33.7490, "lon": -84.3880},          # 16
        {"name": "Charlotte, NC", "lat": 35.2271, "lon": -80.8431},        # 17
        {"name": "Jacksonville, FL", "lat": 30.3322, "lon": -81.6557},     # 18
        {"name": "Orlando, FL", "lat": 28.5383, "lon": -81.3792},          # 19
        
        # Northeast & Canada East
        {"name": "New York, NY", "lat": 40.7128, "lon": -74.0060},         # 20
        {"name": "Philadelphia, PA", "lat": 39.9526, "lon": -75.1652},     # 21
        {"name": "Toronto, ON", "lat": 43.6532, "lon": -79.3832}           # 22
    ]

    # Assign Flows (Source -> Target with Volume)
    # Flow Structure: {'start_lat': ..., 'start_lon': ..., 'end_lat': ..., 'end_lon': ..., 'vol': ...}
    map_flows = []
    
    # Note: Using factory_configs to get dynamic volume
    # Mapping back to the lists might be tricky if order changed, but we kept order for active ones.
    # For simplicity in this demo, accessing by index for the active ones (Beech=0, Ogden=1, Paris=2)
    # But factory_configs might be shorter if inactive filtered? No, we appended all.
    
    # 1. Factory to DC Flows (Inter-Network)
    # Ogden (West Hub) -> Redlands (West DC) + DuPont (NW)
    f_ogden = factory_configs[1]
    map_flows.append({"src": f_ogden, "dst": default_dcs[0], "vol": f_ogden['volume']*0.6, "color": "#ef4444"}) # -> Redlands
    map_flows.append({"src": f_ogden, "dst": default_dcs[4], "vol": f_ogden['volume']*0.3, "color": "#ef4444"}) # -> DuPont
    
    # Paris (South Central Hub) -> Wilmer (Dallas) + McDonough (ATL)
    f_paris = factory_configs[2]
    map_flows.append({"src": f_paris, "dst": default_dcs[1], "vol": f_paris['volume']*0.6, "color": "#ef4444"}) # -> Wilmer
    map_flows.append({"src": f_paris, "dst": default_dcs[2], "vol": f_paris['volume']*0.3, "color": "#ef4444"}) # -> McDonough
    
    # Beech Island (East Hub) -> McDonough + New Milford + Mississauga (Canada)
    f_beech = factory_configs[0]
    map_flows.append({"src": f_beech, "dst": default_dcs[2], "vol": f_beech['volume']*0.3, "color": "#ef4444"}) # -> McDonough
    map_flows.append({"src": f_beech, "dst": default_dcs[3], "vol": f_beech['volume']*0.4, "color": "#ef4444"}) # -> New Milford
    map_flows.append({"src": f_beech, "dst": default_dcs[5], "vol": f_beech['volume']*0.2, "color": "#ef4444"}) # -> Mississauga
    
    # 2. DC to Region CoG Flows (Last Mile)
    
    # Redlands (West DC) -> LA, SD, Phoenix, SLC, Denver (Partial)
    map_flows.append({"src": default_dcs[0], "dst": regions[0], "vol": 25, "color": "#3b82f6"}) # -> LA
    map_flows.append({"src": default_dcs[0], "dst": regions[1], "vol": 12, "color": "#3b82f6"}) # -> SD
    map_flows.append({"src": default_dcs[0], "dst": regions[5], "vol": 15, "color": "#3b82f6"}) # -> Phoenix
    map_flows.append({"src": default_dcs[0], "dst": regions[4], "vol": 8, "color": "#3b82f6"})  # -> SLC
    
    # DuPont (NW DC) -> Seattle, Vancouver, SLC (Partial)
    map_flows.append({"src": default_dcs[4], "dst": regions[2], "vol": 18, "color": "#3b82f6"}) # -> Seattle
    map_flows.append({"src": default_dcs[4], "dst": regions[3], "vol": 10, "color": "#3b82f6"}) # -> Vancouver
    
    # Wilmer (South DC) -> DFW, Houston, San Antonio, Memphis, Denver, Chicago (Long Haul)
    map_flows.append({"src": default_dcs[1], "dst": regions[7], "vol": 25, "color": "#3b82f6"}) # -> DFW
    map_flows.append({"src": default_dcs[1], "dst": regions[8], "vol": 20, "color": "#3b82f6"}) # -> Houston
    map_flows.append({"src": default_dcs[1], "dst": regions[9], "vol": 12, "color": "#3b82f6"}) # -> San Antonio
    map_flows.append({"src": default_dcs[1], "dst": regions[6], "vol": 10, "color": "#3b82f6"}) # -> Denver
    map_flows.append({"src": default_dcs[1], "dst": regions[11], "vol": 15, "color": "#3b82f6"}) # -> Chicago
    
    # McDonough (SE DC) -> Atlanta, Charlotte, Nashville, JAX, Orlando, Memphis, Indy
    map_flows.append({"src": default_dcs[2], "dst": regions[16], "vol": 25, "color": "#3b82f6"}) # -> Atlanta
    map_flows.append({"src": default_dcs[2], "dst": regions[17], "vol": 15, "color": "#3b82f6"}) # -> Charlotte
    map_flows.append({"src": default_dcs[2], "dst": regions[15], "vol": 12, "color": "#3b82f6"}) # -> Nashville
    map_flows.append({"src": default_dcs[2], "dst": regions[18], "vol": 10, "color": "#3b82f6"}) # -> JAX
    map_flows.append({"src": default_dcs[2], "dst": regions[19], "vol": 12, "color": "#3b82f6"}) # -> Orlando
    map_flows.append({"src": default_dcs[2], "dst": regions[10], "vol": 8, "color": "#3b82f6"})  # -> Memphis
    map_flows.append({"src": default_dcs[2], "dst": regions[13], "vol": 10, "color": "#3b82f6"}) # -> Indy
    
    # New Milford (NE DC) -> NYC, Philly, Detroit, Columbus
    map_flows.append({"src": default_dcs[3], "dst": regions[20], "vol": 30, "color": "#3b82f6"}) # -> NYC
    map_flows.append({"src": default_dcs[3], "dst": regions[21], "vol": 20, "color": "#3b82f6"}) # -> Philly
    map_flows.append({"src": default_dcs[3], "dst": regions[12], "vol": 12, "color": "#3b82f6"}) # -> Detroit
    map_flows.append({"src": default_dcs[3], "dst": regions[14], "vol": 10, "color": "#3b82f6"}) # -> Columbus
    
    # Mississauga -> Toronto
    map_flows.append({"src": default_dcs[5], "dst": regions[22], "vol": 15, "color": "#3b82f6"}) # -> Toronto

    # --- Data Overlay Controls ---
    st.markdown("##### Demographic Overlays")
    overlay_driver = st.selectbox(
        "Select Map Layer", 
        ["None", "High Vol. Transport Lanes", "Population (2024 Est.)", "Median Household Income", "Births (2023)", "Avg. Mfg Labor Cost ($/hr)"],
        index=0
    )



    # US State Data (Source: US Census Bureau 2023-2024 Estimates, BLS 2023)

    # Dictionary mapping State Code to Value
    us_state_data = {
        'AL': {'pop': 5.2, 'inc': 59609, 'births': 57647, 'labor': 22.50},
        'AK': {'pop': 0.7, 'inc': 86370, 'births': 9364, 'labor': 28.10},
        'AZ': {'pop': 7.4, 'inc': 74568, 'births': 76950, 'labor': 24.80},
        'AR': {'pop': 3.1, 'inc': 53860, 'births': 35640, 'labor': 20.90},
        'CA': {'pop': 38.9, 'inc': 91551, 'births': 407073, 'labor': 32.40},
        'CO': {'pop': 5.9, 'inc': 89302, 'births': 59870, 'labor': 29.50},
        'CT': {'pop': 3.6, 'inc': 88429, 'births': 34338, 'labor': 30.10},
        'DE': {'pop': 1.0, 'inc': 77082, 'births': 10344, 'labor': 25.00},
        'FL': {'pop': 23.0, 'inc': 69303, 'births': 224250, 'labor': 23.80},
        'GA': {'pop': 11.1, 'inc': 72837, 'births': 123000, 'labor': 21.90},
        'HI': {'pop': 1.4, 'inc': 92458, 'births': 15570, 'labor': 28.50},
        'ID': {'pop': 2.0, 'inc': 70374, 'births': 22000, 'labor': 22.10},
        'IL': {'pop': 12.5, 'inc': 76708, 'births': 130000, 'labor': 26.50},
        'IN': {'pop': 6.9, 'inc': 66785, 'births': 79000, 'labor': 24.20},
        'IA': {'pop': 3.2, 'inc': 69588, 'births': 36000, 'labor': 23.50},
        'KS': {'pop': 2.9, 'inc': 68925, 'births': 34000, 'labor': 24.10},
        'KY': {'pop': 4.5, 'inc': 59341, 'births': 51000, 'labor': 23.90},
        'LA': {'pop': 4.5, 'inc': 55416, 'births': 57000, 'labor': 22.80},
        'ME': {'pop': 1.4, 'inc': 69543, 'births': 11000, 'labor': 25.20},
        'MD': {'pop': 6.2, 'inc': 94991, 'births': 68000, 'labor': 28.50},
        'MA': {'pop': 7.0, 'inc': 94488, 'births': 69000, 'labor': 31.80},
        'MI': {'pop': 10.0, 'inc': 66986, 'births': 103000, 'labor': 27.50},
        'MN': {'pop': 5.7, 'inc': 82338, 'births': 63000, 'labor': 28.20},
        'MS': {'pop': 2.9, 'inc': 52719, 'births': 34000, 'labor': 20.50},
        'MO': {'pop': 6.2, 'inc': 64811, 'births': 68000, 'labor': 23.40},
        'MT': {'pop': 1.1, 'inc': 67631, 'births': 11000, 'labor': 23.10},
        'NE': {'pop': 2.0, 'inc': 69597, 'births': 23000, 'labor': 23.60},
        'NV': {'pop': 3.2, 'inc': 70932, 'births': 34000, 'labor': 25.80},
        'NH': {'pop': 1.4, 'inc': 89992, 'births': 12000, 'labor': 29.20},
        'NJ': {'pop': 9.3, 'inc': 96346, 'births': 101000, 'labor': 30.50},
        'NM': {'pop': 2.1, 'inc': 59726, 'births': 21000, 'labor': 21.80},
        'NY': {'pop': 19.5, 'inc': 79557, 'births': 208000, 'labor': 29.80},
        'NC': {'pop': 10.8, 'inc': 67481, 'births': 120000, 'labor': 22.40},
        'ND': {'pop': 0.8, 'inc': 71913, 'births': 10000, 'labor': 26.50},
        'OH': {'pop': 11.8, 'inc': 65720, 'births': 129000, 'labor': 25.90},
        'OK': {'pop': 4.0, 'inc': 59673, 'births': 48000, 'labor': 22.30},
        'OR': {'pop': 4.2, 'inc': 75657, 'births': 40000, 'labor': 28.40},
        'PA': {'pop': 12.9, 'inc': 71719, 'births': 130000, 'labor': 26.10},
        'RI': {'pop': 1.1, 'inc': 81854, 'births': 10000, 'labor': 27.50},
        'SC': {'pop': 5.4, 'inc': 64115, 'births': 57000, 'labor': 21.60},
        'SD': {'pop': 0.9, 'inc': 69728, 'births': 11000, 'labor': 22.90},
        'TN': {'pop': 7.1, 'inc': 65254, 'births': 81000, 'labor': 22.10},
        'TX': {'pop': 30.5, 'inc': 72284, 'births': 387000, 'labor': 24.50},
        'UT': {'pop': 3.4, 'inc': 89168, 'births': 46000, 'labor': 25.20},
        'VT': {'pop': 0.6, 'inc': 73991, 'births': 5000, 'labor': 26.80},
        'VA': {'pop': 8.7, 'inc': 85873, 'births': 95000, 'labor': 25.60},
        'WA': {'pop': 7.8, 'inc': 91306, 'births': 84000, 'labor': 33.50},
        'WV': {'pop': 1.8, 'inc': 54329, 'births': 17000, 'labor': 23.20},
        'WI': {'pop': 5.9, 'inc': 70996, 'births': 60000}, # Missing WY in orig but okay
        'WY': {'pop': 0.6, 'inc': 70042, 'births': 6000, 'labor': 26.10}
    }



    # Create Map (Plotly Scattergeo with Custom Flows)
    # Create Map (Plotly Scattergeo with Custom Flows)
    
    # Layout: Map (Left) | Controls (Right)
    col_map, col_controls = st.columns([0.8, 0.2])
    
    with col_controls:
        st.markdown("##### Retail Layers")
        st.caption("Select retailers to visualize their network distribution.")
        
        retailers_overlay = []
        if st.toggle("Costco", key="tg_costco"): retailers_overlay.append("Costco")
        if st.toggle("Walmart", key="tg_walmart"): retailers_overlay.append("Walmart")
        if st.toggle("Target", key="tg_target"): retailers_overlay.append("Target")
        if st.toggle("Kroger", key="tg_kroger"): retailers_overlay.append("Kroger")
        if st.toggle("Kroger Sub.", key="tg_krogersub"): retailers_overlay.append("Kroger Subsidiaries")

    # Create Map (Plotly Scattergeo with Custom Flows)
    fig_map = go.Figure()

    # --- 0. Overlay Layers ---
    if "Transport Lanes" in overlay_driver:
        # Define Major Corridors (Approximate Paths for Overlay)
        lanes = [
            {"name": "I-5 (West Coast Artery)", "path": [(32.7157, -117.1611), (34.0522, -118.2437), (47.6062, -122.3321)]}, # SD -> LA -> Seattle
            {"name": "I-35 (NAFTA Corridor)", "path": [(27.5036, -99.5076), (29.4241, -98.4936), (32.7767, -96.7970), (41.8781, -87.6298)]}, # Laredo -> San Antonio -> DFW -> Chi
            {"name": "I-95 (East Coast Artery)", "path": [(25.7617, -80.1918), (30.3322, -81.6557), (40.7128, -74.0060)]}, # Miami -> JAX -> NY
            {"name": "I-10 (Southern Belt)", "path": [(34.0522, -118.2437), (33.4484, -112.0740), (29.7604, -95.3698), (30.3322, -81.6557)]}, # LA -> Phx -> Houston -> JAX
            {"name": "I-80 (Cross Country)", "path": [(37.7749, -122.4194), (40.7608, -111.8910), (41.8781, -87.6298), (40.7128, -74.0060)]}, # SF -> SLC -> Chi -> NY
            {"name": "I-75 (Auto Alley)", "path": [(42.3314, -83.0458), (39.9612, -82.9988), (33.7490, -84.3880), (28.5383, -81.3792)]}, # Detroit -> Cbus -> ATL -> Orlando
            {"name": "I-40 (Golden Lane)", "path": [(34.0556, -117.1825), (35.1495, -90.0490), (35.2271, -80.8431)]} # Redlands (LA) -> Memphis -> Charlotte
        ]
        
        for lane in lanes:
            lats = [p[0] for p in lane['path']]
            lons = [p[1] for p in lane['path']]
            
            fig_map.add_trace(go.Scattergeo(
                lon=lons,
                lat=lats,
                mode='lines',
                line=dict(width=3, color='#f59e0b', dash='dashdot'), # Amber Dashed
                opacity=0.8,
                name=lane['name'],
                hoverinfo='text',
                text=f"<b>{lane['name']}</b><br>High Volume Commercial Lane"
            ))



    # --- Retail Overlays (Independent Layer) ---
    if retailers_overlay:
        colors = {
            "Costco": "cyan", 
            "Walmart": "blue", 
            "Target": "red", 
            "Kroger": "purple",
            "Kroger Subsidiaries": "#d946ef" # Fuchsia/Magenta
        }
        
        # Helper to load data dynamically
        import utils.real_retail_data as rrd
        
        # Sampling Function (20%) - Cached to prevent flicker
        def get_sample(retailer_name, locations, pct=0.2):
            key = f"sample_{retailer_name}"
            # Check if cache exists and length matches (simple validation)
            if key not in st.session_state:
                k = int(len(locations) * pct)
                st.session_state[key] = random.sample(locations, k)
            return st.session_state[key]

        for retailer in retailers_overlay:
            if retailer == "Costco":
                sample_pairs = get_sample("Costco", rrd.COSTCO_LOCATIONS)
            elif retailer == "Walmart":
                sample_pairs = get_sample("Walmart", rrd.WALMART_LOCATIONS)
            elif retailer == "Target":
                sample_pairs = get_sample("Target", rrd.TARGET_LOCATIONS)
            elif retailer == "Kroger":
                sample_pairs = get_sample("Kroger", rrd.KROGER_LOCATIONS)
            elif retailer == "Kroger Subsidiaries":
                sample_pairs = get_sample("KrogerSubs", rrd.KROGER_SUB_LOCATIONS)
            else:
                sample_pairs = []

            if sample_pairs:
                fig_map.add_trace(go.Scattergeo(
                    lat=[p[0] for p in sample_pairs],
                    lon=[p[1] for p in sample_pairs],
                    mode='markers',
                    marker=dict(size=3, color=colors[retailer], opacity=0.7),
                    name=f"{retailer} (20% Sample)",
                    hoverinfo='text',
                    text=[f"{retailer} Store" for _ in sample_pairs]
                ))

    if overlay_driver != "None":
        
        # A. State Level Choropleth
        # Prepare Data
        z_vals = []
        locations = []
        color_scale = "Blues"
        label = ""
        
        if "Population" in overlay_driver:
            label = "Population (M)"
            color_scale = "Greys" # User requested Grays
            for state, data in us_state_data.items():
                if 'pop' in data: # Safe check
                    locations.append(state)
                    z_vals.append(data['pop'])
                
        elif "Income" in overlay_driver:
            label = "Avg Income ($)"
            color_scale = "Greens"
            for state, data in us_state_data.items():
                if 'inc' in data:
                    locations.append(state)
                    z_vals.append(data['inc'])
        
        elif "Births" in overlay_driver:
            label = "Annual Births"
            color_scale = "Reds" # Relevant for Baby Care
            for state, data in us_state_data.items():
                if 'births' in data:
                    locations.append(state)
                    z_vals.append(data['births'])
                    
        elif "Labor" in overlay_driver:
            label = "Mfg Wage ($/hr)"
            color_scale = "Purples" # Distinct from others
            for state, data in us_state_data.items():
                if 'labor' in data:
                    locations.append(state)
                    z_vals.append(data['labor'])

        fig_map.add_trace(go.Choropleth(
            locations=locations,
            z=z_vals,
            locationmode='USA-states',
            colorscale=color_scale,
            marker_line_color='rgba(255,255,255,0.1)', # Faint borders
            marker_line_width=1,
            zmin=min(z_vals) if z_vals else 0, # Prevent error if empty
            zmax=max(z_vals) if z_vals else 1,
            colorbar_title=label,
            colorbar=dict(
                x=0.01, # Left aligned
                y=0.5,
                len=0.4,
                thickness=10,
                title_side='right',
                bgcolor='rgba(0,0,0,0.5)',
                tickfont=dict(color='white'),
                title=dict(font=dict(color='white'))
            ),
            # Make it subtle so it doesn't overpower the network
            marker_opacity=0.6 
        ))

    # --- 1. Nodes Customization ---
    
    # Active Mfg (Solid Circles, Size Proportional to Volume)
    active_mfg = [f for f in factory_configs if "Const" not in f['name']]
    
    # Calculate sizes: Base 10 + Scale factor
    mfg_sizes = [15 + (f['volume'] / 5) for f in active_mfg]
    
    fig_map.add_trace(go.Scattergeo(
        lon=[f['lon'] for f in active_mfg],
        lat=[f['lat'] for f in active_mfg],
        text=[f"<b>{f['name']}</b><br>{f['role']}<br>Vol: {f['volume']}M" for f in active_mfg],
        mode='markers+text',
        textposition="top center",
        marker=dict(
            size=mfg_sizes, 
            color='#ef4444', 
            symbol='circle', 
            line=dict(width=2, color='white')
        ),
        name='Active Manufacturing'
    ))
    
    # Future Mfg (Hollow Circles)
    future_mfg = [f for f in factory_configs if "Const" in f['name']]
    fig_map.add_trace(go.Scattergeo(
        lon=[f['lon'] for f in future_mfg],
        lat=[f['lat'] for f in future_mfg],
        text=[f"<b>{f['name']}</b><br>{f['role']}" for f in future_mfg],
        mode='markers+text',
        textposition="top center",
        marker=dict(size=14, color='rgba(0,0,0,0)', symbol='circle', 
                   line=dict(width=2, color='#f59e0b')), # Amber Outline
        name='Future Capacity'
    ))

    # DCs (Blue Diamonds - approximations for "Arc" or distinct shape)
    fig_map.add_trace(go.Scattergeo(
        lon=[d['lon'] for d in default_dcs],
        lat=[d['lat'] for d in default_dcs],
        text=[f"<b>{d['name']}</b><br>{d['role']}" for d in default_dcs],
        mode='markers',
        marker=dict(size=12, color='#3b82f6', symbol='diamond', line=dict(width=1, color='white')),
        name='Distribution Centers'
    ))
    
    # Regional Demand CoG (Strategic Centers)
    fig_map.add_trace(go.Scattergeo(
        lon=[r['lon'] for r in regions],
        lat=[r['lat'] for r in regions],
        text=[r['name'] for r in regions],
        mode='markers',
        marker=dict(size=8, color='#10b981', symbol='x', line=dict(width=1, color='white')), # Emerald 'X'
        name='Regional Demand CoG'
    ))

    # --- 2. Curved Flow Generation ---
    import numpy as np

    def get_curve_points(start_lat, start_lon, end_lat, end_lon, n_points=20, curvature=0.2):
        # Linear interpolation
        lats = np.linspace(start_lat, end_lat, n_points)
        lons = np.linspace(start_lon, end_lon, n_points)
        
        # Add curvature (parabolic offset perpendicular to the path)
        # Simply adding offset to latitude for visual curve
        dist = np.sqrt((end_lat - start_lat)**2 + (end_lon - start_lon)**2)
        
        # Parabola: 4 * h * x * (1-x) where x is 0..1
        t = np.linspace(0, 1, n_points)
        offset = 4 * (curvature * dist) * t * (1 - t)
        
        return lats + offset, lons

    # Plot Flows (Curved Lines)
    added_legend_groups = set()
    
    for flow in map_flows:
        src_lat, src_lon = flow['src']['lat'], flow['src']['lon']
        dst_lat, dst_lon = flow['dst']['lat'], flow['dst']['lon']
        
        # Determine Flow Type for Legend
        flow_name = "Other Flows"
        if flow['color'] == "#ef4444":  # Red
            flow_name = "Plant → DC Volume"
        elif flow['color'] == "#3b82f6": # Blue
            flow_name = "DC → Customer Volume"
            
        show_legend = False
        if flow_name not in added_legend_groups:
            show_legend = True
            added_legend_groups.add(flow_name)
        
        # Generate curve points
        curve_lat, curve_lon = get_curve_points(src_lat, src_lon, dst_lat, dst_lon)
        
        # Scale width (Thicker)
        width = max(3, (flow['vol'] / 100) * 15)
        
        fig_map.add_trace(go.Scattergeo(
            lon=curve_lon,
            lat=curve_lat,
            mode='lines',
            line=dict(width=width, color=flow['color']),
            opacity=0.6, # Slightly increased opacity for visibility
            hoverinfo='text',
            text=f"Flow: {flow['vol']:.1f}M",
            name=flow_name,
            legendgroup=flow_name,
            showlegend=show_legend
        ))

    fig_map.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        height=750, # Slightly reduced height to enhance "wide" feel
        showlegend=True,
        legend=dict(x=0.01, y=0.95, bgcolor="rgba(0,0,0,0)"),
        geo=dict(
            scope='north america',
            showland=True,
            landcolor='#1e293b', 
            subunitcolor="#334155",
            countrycolor="#475569", 
            showlakes=False,
            bgcolor='rgba(0,0,0,0)',
            resolution=50,
            # Ultra-Cinematic "Widescreen" Crop
            lataxis=dict(range=[24, 52]),  # Tight crop: South TX to Northern US/Border Canada
            lonaxis=dict(range=[-135, -55]), # Extended East/West
            projection=dict(type="mercator"), 
            fitbounds=False
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        uirevision='constant' # Preserves zoom/pan and legend state across updates
    )


    # Render Map in Left Column
    col_map.plotly_chart(fig_map, use_container_width=True)


    st.markdown("##### Material Flow Analysis")
    # st.caption("Visualizing flow from Factory -> DC -> Region (Simulated based on capacity)")

    # Construct Sankey Data
    # Levels: Factories (0,1,2) -> DCs (3,4,5,6,7) -> Regions (8,9,10,11)
    
    # 1. Define Nodes
    labels = [f['name'] for f in factory_configs] + [d['name'] for d in default_dcs] + ["West Region", "Midwest Region", "South Region", "Northeast Region"]
    
    # Indices
    # Factories: 0-2
    # DCs: 3-7
    # Regions: 8-11
    
    # 2. Define Links (Simulated Logic)
    # Logic: 
    # Ogden feeds DC West (3) and DC Midwest (4)
    # Paris feeds DC Texas (7) and DC Midwest (4) and DC South (5)
    # Beech Island feeds DC South (5) and DC Northeast (6)
    
    sources = []
    targets = []
    values = []

    # Ogden (Index 0) -> DC West (3), DC Midwest (4)
    sources.extend([0, 0])
    targets.extend([3, 4])
    values.extend([factory_configs[0]['volume']*0.7, factory_configs[0]['volume']*0.3]) # 70% West, 30% Midwest

    # Paris (Index 1) -> DC Texas (7), DC Midwest (4), DC South (5)
    sources.extend([1, 1, 1])
    targets.extend([7, 4, 5])
    values.extend([factory_configs[1]['volume']*0.5, factory_configs[1]['volume']*0.3, factory_configs[1]['volume']*0.2])

    # Beech Island (Index 2) -> DC South (5), DC Northeast (6)
    sources.extend([2, 2])
    targets.extend([5, 6])
    values.extend([factory_configs[2]['volume']*0.4, factory_configs[2]['volume']*0.6])

    # DCs to Regions (Pass through)
    # DC West (3) -> West Region (8)
    sources.append(3)
    targets.append(8)
    values.append(factory_configs[0]['volume']*0.7) # Just passing through for simplicity

    # DC Midwest (4) -> Midwest Region (9)
    # Volume = Ogden flow + Paris flow
    midwest_vol = (factory_configs[0]['volume']*0.3) + (factory_configs[1]['volume']*0.3)
    sources.append(4)
    targets.append(9)
    values.append(midwest_vol)

    # DC South (5) + DC Texas (7) -> South (10)
    south_vol = (factory_configs[1]['volume']*0.2) + (factory_configs[2]['volume']*0.4) + (factory_configs[1]['volume']*0.5)
    # Split flows from both DCs
    sources.extend([5, 7])
    targets.extend([10, 10])
    values.extend([(factory_configs[1]['volume']*0.2) + (factory_configs[2]['volume']*0.4), factory_configs[1]['volume']*0.5])

    # DC Northeast (6) -> Northeast (11)
    sources.append(6)
    targets.append(11)
    values.append(factory_configs[2]['volume']*0.6)

    fig_sankey = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = labels,
          color = "blue"
        ),
        link = dict(
          source = sources,
          target = targets,
          value = values
      ))])

    fig_sankey.update_layout(title_text="Estimated Production Flow (Millions of Units)", font_size=10, height=600)
    st.plotly_chart(fig_sankey, use_container_width=True)

    # --- Sources Footer ---
    st.markdown("---")
    st.caption("**Data Sources:**")
    st.caption("1. **Population (2024 Est.):** U.S. Census Bureau, Population Division. Annual Estimates of the Resident Population.")
    st.caption("2. **Median Household Income:** U.S. Census Bureau, American Community Survey (ACS).")
    st.caption("3. **Births:** Centers for Disease Control and Prevention (CDC), National Center for Health Statistics.")
    st.caption("4. **Cost of Labor:** Bureau of Labor Statistics (BLS), Average Hourly Earnings of Production Employees (State Estimates).")
