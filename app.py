"""
UFC Fight Predictor - Interactive Dashboard
Built with Streamlit
"""
import streamlit as st
import pandas as pd
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from src.processor import load_fighters, clean_fighters, predict_matchup

# --- Page Config ---
st.set_page_config(
    page_title="UFC Fight Predictor",
    page_icon="🥊",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
    }
    .fighter-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        margin: 10px 0;
    }
    .red-corner {
        border-left: 4px solid #e74c3c;
    }
    .blue-corner {
        border-left: 4px solid #3498db;
    }
    .stat-label {
        color: #aaa;
        font-size: 0.85em;
    }
    .stat-value {
        font-size: 1.2em;
        font-weight: bold;
    }
    .prediction-box {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        color: white;
        margin: 20px 0;
    }
    .winner-name {
        font-size: 2em;
        font-weight: bold;
        color: #f1c40f;
    }
    .vs-text {
        font-size: 2.5em;
        font-weight: bold;
        color: #e74c3c;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def get_data():
    try:
        df = load_fighters()
    except Exception:
        return None
        
    # Check if required columns exist before cleaning
    required = ['Stance', 'Height_cm', 'Reach_cm', 'Wins', 'Losses']
    missing = [c for c in required if c not in df.columns]
    
    if missing:
        # Invalid data file (probably from old scraper run)
        st.cache_data.clear()
        return None
        
    df = clean_fighters(df)
    return df

fighters_df = get_data()

if fighters_df is None or fighters_df.empty:
    st.warning("⏳ Scraping data... Please wait a moment and refresh the page.")
    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    st.stop()

# --- Sidebar ---
with st.sidebar:
    st.header("Settings")
    if st.button("🔄 Refresh / Reload Data"):
        st.cache_data.clear()
        st.rerun()

# --- Header ---
st.markdown("<h1 style='text-align:center;'>🥊 UFC Fight Predictor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color: #888;'>Compare fighters by weight class and predict fight outcomes using statistical analysis</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Weight Class Filter ---
weight_classes = sorted(fighters_df['WeightClass'].unique())
selected_class = st.selectbox("🏋️ Filter by Weight Class", ['All Classes'] + weight_classes)

if selected_class != 'All Classes':
    available_fighters = fighters_df[fighters_df['WeightClass'] == selected_class].sort_values('Name')
else:
    available_fighters = fighters_df.sort_values('Name')

fighter_names = available_fighters['Name'].tolist()

if len(fighter_names) < 2:
    st.warning("Not enough fighters in this weight class. Try another one.")
    st.stop()

# --- Fighter Selection ---
col1, col_vs, col2 = st.columns([5, 1, 5])

with col1:
    st.markdown("### 🔴 Red Corner")
    fighter_a_name = st.selectbox("Select Fighter A", fighter_names, index=0, key="fighter_a")

with col_vs:
    st.markdown("<div class='vs-text'><br>VS</div>", unsafe_allow_html=True)

with col2:
    st.markdown("### 🔵 Blue Corner")
    fighter_b_options = [n for n in fighter_names if n != fighter_a_name]
    fighter_b_name = st.selectbox("Select Fighter B", fighter_b_options, index=0, key="fighter_b")

    # --- Tale of the Tape (Visual) ---
    st.markdown("---")

    # Define fighters
    fighter_a = available_fighters[available_fighters['Name'] == fighter_a_name].iloc[0]
    fighter_b = available_fighters[available_fighters['Name'] == fighter_b_name].iloc[0]

    # Helper for image fetching
    try:
        from src.image_fetcher import get_fighter_image_url
    except ImportError:
        def get_fighter_image_url(name): return None

    @st.cache_data(show_spinner="Running photo reconnaissance...", ttl=3600*24)
    def fetch_photo(name):
        return get_fighter_image_url(name)

    # Placeholder Image SVG
    PLACEHOLDER_SVG = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#555" width="100%" height="100%">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
    </svg>
    """

    
    # Function to display fighter stats in a card
    def fighter_card(fighter, corner="red"):
        name = fighter['Name']
        nickname = fighter.get('Nickname', '')
        if pd.isna(nickname): nickname = ""
        
        color = "#e74c3c" if corner == "red" else "#3498db"
        
        with st.container(border=True):
            st.markdown(f"<h2 style='text-align: center; color: {color}; margin:0;'>{name}</h2>", unsafe_allow_html=True)
            if nickname:
                st.markdown(f"<p style='text-align: center; color: #aaa; margin:0; font-style:italic;'>'{nickname}'</p>", unsafe_allow_html=True)
            
            st.write("") # Spacer
            
            # Image
            img_url = fetch_photo(name)
            if img_url:
                st.image(img_url, use_container_width=True)
            else:
                st.markdown(f"<div style='text-align:center;'>{PLACEHOLDER_SVG}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Stats Grid (HTML for better control)
            stats_html = f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center;">
                <div>
                    <span style="color:#888; font-size:0.8em;">Height</span><br>
                    <span style="font-size:1.1em; font-weight:bold;">{fighter['Height_cm']:.0f} cm</span>
                </div>
                <div>
                    <span style="color:#888; font-size:0.8em;">Reach</span><br>
                    <span style="font-size:1.1em; font-weight:bold;">{fighter['Reach_cm']:.0f} cm</span>
                </div>
                <div>
                    <span style="color:#888; font-size:0.8em;">Record</span><br>
                    <span style="font-size:1.1em; font-weight:bold;">{int(fighter['Wins'])}-{int(fighter['Losses'])}</span>
                </div>
                <div>
                    <span style="color:#888; font-size:0.8em;">Win Rate</span><br>
                    <span style="font-size:1.1em; font-weight:bold;">{fighter['WinRate']:.0%}</span>
                </div>
            </div>
            <div style="margin-top: 15px; text-align: center;">
                <span style="color:{color}; font-weight:bold; border-bottom: 2px solid {color};">STRIKING</span>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin-top:5px;">
                    <div><span style="color:#aaa; font-size:0.8em;">SLpM</span> <span style="font-weight:bold;">{fighter['SLpM']:.2f}</span></div>
                    <div><span style="color:#aaa; font-size:0.8em;">Def</span> <span style="font-weight:bold;">{fighter['Str_Def']:.0%}</span></div>
                </div>
            </div>
            <div style="margin-top: 10px; text-align: center;">
                <span style="color:{color}; font-weight:bold; border-bottom: 2px solid {color};">GRAPPLING</span>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin-top:5px;">
                    <div><span style="color:#aaa; font-size:0.8em;">TD Avg</span> <span style="font-weight:bold;">{fighter['TD_Avg']:.2f}</span></div>
                    <div><span style="color:#aaa; font-size:0.8em;">Sub Avg</span> <span style="font-weight:bold;">{fighter['Sub_Avg']:.2f}</span></div>
                </div>
            </div>
            """
            st.markdown(stats_html, unsafe_allow_html=True)

    col1, col_center, col2 = st.columns([1, 0.15, 1], gap="small")
    
    with col1:
        fighter_card(fighter_a, "red")
        
    with col_center:
        # Centering 'VS' vertically is tricky in Streamlit.
        # We'll use formatting to push it down roughly to the middle of the images.
        st.markdown("<div style='text-align: center; font-size: 2.5em; font-weight: 900; color: #e74c3c; padding-top: 250px;'>VS</div>", unsafe_allow_html=True)
        
    with col2:
        fighter_card(fighter_b, "blue")

    # Metrics comparison (optional expandable detail)
    with st.expander("📊 View Detailed Comparison Table"):
         st.dataframe(available_fighters.set_index('Name'), use_container_width=True)

    st.header("ℹ️ How it Works")
    st.markdown("""
    **Prediction Logic:**
    The model calculates a weighted score based on 4 key factors:
    
    *   **🥊 Striking (40%)**: Compares significant strikes landed, accuracy, and defense.
    *   **🤼 Grappling (30%)**: Compares takedown average, accuracy, and submission threat.
    *   **📐 Physical (15%)**: Reach and height advantage.
    *   **🏅 Experience (15%)**: Win rate weighted by total number of fights.
    
    *Data sourced from [ufcstats.com](http://www.ufcstats.com) & [ufc.com](http://www.ufc.com) (photos).*
    """)

# --- Prediction ---
st.markdown("---")

if st.button("🥊 PREDICT FIGHT OUTCOME", use_container_width=True, type="primary"):
    result = predict_matchup(fighter_a, fighter_b)
    
    # Winner display
    winner = result['predicted_winner']
    is_a_winner = winner == fighter_a_name
    
    st.markdown(f"""
    <div class='prediction-box'>
        <p style='font-size: 1.2em; color: #aaa;'>PREDICTED WINNER</p>
        <p class='winner-name'>🏆 {winner}</p>
        <p style='font-size: 1.1em;'>Confidence: {result['confidence']:.1f}%</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Probability bars
    prob_col1, prob_col2 = st.columns(2)
    
    with prob_col1:
        st.metric(f"🔴 {fighter_a_name}", f"{result['prob_a']:.1%}")
        st.progress(result['prob_a'])
    
    with prob_col2:
        st.metric(f"🔵 {fighter_b_name}", f"{result['prob_b']:.1%}")
        st.progress(result['prob_b'])
    
    # Breakdown
    st.markdown("### 📈 Advantage Breakdown")
    
    bd = result['breakdown']
    
    adv_col1, adv_col2, adv_col3, adv_col4 = st.columns(4)
    
    categories = [
        ("🥋 Striking", bd['Striking'], 'Striking', adv_col1),
        ("🤼 Grappling", bd['Grappling'], 'Grappling', adv_col2),
        ("📐 Physical", bd['Physical'], 'Physical', adv_col3),
        ("🏅 Experience", bd['Experience'], 'Experience', adv_col4),
    ]
    
    for label, data, key, col in categories:
        with col:
            adv = data.get('Advantage', 'Even')
            if adv == 'A':
                adv_icon = f"🔴 {fighter_a_name}"
                adv_color = "#e74c3c"
            elif adv == 'B':
                adv_icon = f"🔵 {fighter_b_name}"
                adv_color = "#3498db"
            else:
                adv_icon = "⚖️ Even"
                adv_color = "#95a5a6"
            
            st.markdown(f"**{label}**")
            st.markdown(f"<span style='color:{adv_color};font-weight:bold;'>{adv_icon}</span>", unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color: #666;'>"
    "Data sourced from ufcstats.com | Model uses weighted statistical analysis across "
    "Striking (40%), Grappling (30%), Physical (15%), Experience (15%)"
    "</p>",
    unsafe_allow_html=True
)
