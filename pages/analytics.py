import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Add src to path so we can import processor
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.processor import load_fighters, clean_fighters

st.set_page_config(page_title="UFC Analytics", page_icon="📈", layout="wide")

st.title("📈 UFC Roster Analytics")
st.markdown("Explore statistical trends across the UFC roster.")

@st.cache_data
def get_data():
    try:
        df = load_fighters()
        df = clean_fighters(df)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = get_data()

if df.empty:
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Filters")
selected_stance = st.sidebar.multiselect("Stance", df['Stance'].unique(), default=df['Stance'].unique())
min_fights = st.sidebar.slider("Minimum Fights", 0, 50, 5)

# Filter data
filtered_df = df[
    (df['Stance'].isin(selected_stance)) & 
    ((df['Wins'] + df['Losses'] + df['Draws']) >= min_fights)
]

st.sidebar.markdown(f"**Showing {len(filtered_df)} fighters**")

st.sidebar.markdown(f"**Showing {len(filtered_df)} fighters**")

# --- Tabs ---
tab_charts, tab_data = st.tabs(["📊 Charts", "📋 Raw Data"])

with tab_charts:
    # --- Row 1 ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📏 Reach vs Height Correlation")
        fig_scatter = px.scatter(
            filtered_df, 
            x='Height_cm', 
            y='Reach_cm', 
            color='Stance', 
            hover_data=['Name'],
            trendline="ols",
            title="Reach vs Height (Ape Index)"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        st.subheader("⚖️ Weight Class Distribution")
        # Bin weights to estimate classes if Class column doesn't exist?
        # Actually, let's just use Weight_lbs distribution
        fig_hist = px.histogram(
            filtered_df, 
            x='Weight_lbs', 
            nbins=20, 
            title="Weight Distribution",
            color_discrete_sequence=['#ff4b4b']
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # --- Row 2 ---
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("🥊 Striking Volume vs Accuracy")
        fig_strike = px.scatter(
            filtered_df,
            x='SLpM',
            y='Str_Acc',
            size='Wins',
            color='Stance',
            hover_data=['Name'],
            title="Significant Strikes Landed per Minute vs Accuracy"
        )
        st.plotly_chart(fig_strike, use_container_width=True)

    with col4:
        st.subheader("🤼 Grappling Heavyweights")
        top_grapplers = filtered_df.nlargest(10, 'TD_Avg')
        fig_grapple = px.bar(
            top_grapplers,
            x='TD_Avg',
            y='Name',
            orientation='h',
            title="Top 10: Takedowns Average per 15 min",
            color='TD_Acc'
        )
        st.plotly_chart(fig_grapple, use_container_width=True)

with tab_data:
    st.subheader("📋 Raw Data Explorer")
    st.markdown("Filter and sort the dataset below.")
    st.dataframe(filtered_df, use_container_width=True)

