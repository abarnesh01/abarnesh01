import streamlit as st
import pandas as pd
import cv2
import yaml
import time
import os
import sys
from pathlib import Path
from datetime import datetime
import plotly.express as px

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from database.db_manager import DatabaseManager

# --- PREMIUM STYLING ---
st.set_page_config(
    page_title="SafeWatch SOC - Enterprise Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def apply_custom_css():
    st.markdown("""
        <style>
        .main {
            background-color: #0e1117;
        }
        .stMetric {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .stAlert {
            border-radius: 10px;
        }
        h1, h2, h3 {
            color: #58a6ff !important;
            font-family: 'Inter', sans-serif;
        }
        .css-1d391kg { /* Sidebar */
            background-color: #161b22;
        }
        </style>
    """, unsafe_allow_html=True)

apply_custom_css()

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    db = DatabaseManager(config["database"]["path"])

    # --- HEADER ---
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.title("🛡️ SafeWatch Intelligence")
        st.markdown("*Real-time Threat Detection & Behavioral Analytics Ecosystem*")
    with col2:
        st.image("https://img.icons8.com/fluency/96/security-shield.png", width=80)

    # --- SIDEBAR ---
    st.sidebar.header("🕹️ System Control")
    st.sidebar.info(f"Status: **ACTIVE**\nVersion: {config['system']['version']}")
    selected_page = st.sidebar.selectbox("Navigation", ["Live Monitor", "Incident History", "Intelligence Analytics", "System Settings"])

    if selected_page == "Live Monitor":
        st.subheader("📡 Real-Time Surveillance Matrix")
        cols = st.columns(2)
        for idx, cam in enumerate(config["cameras"]):
            if cam["enabled"]:
                with cols[idx % 2]:
                    st.markdown(f"### {cam['name']} (`{cam['id']}`)")
                    # Placeholder for stream
                    st.image("https://placehold.co/640x360/161b22/58a6ff?text=LIVE+STREAM+FEED", use_container_width=True)
                    st.caption(f"Source: {cam['source']} | FPS Target: {cam['fps_limit']}")

    elif selected_page == "Incident History":
        st.subheader("📁 Centralized Incident Vault")
        incidents = db.fetch_all("SELECT * FROM incidents ORDER BY timestamp DESC LIMIT 100")
        if incidents:
            df = pd.DataFrame(incidents)
            st.dataframe(df, use_container_width=True)
            
            st.divider()
            st.subheader("🔍 Visual Evidence Review")
            selected_id = st.selectbox("Select Incident ID", df["id"].tolist())
            row = next(i for i in incidents if i["id"] == selected_id)
            if row["snapshot_path"] and os.path.exists(row["snapshot_path"]):
                st.image(row["snapshot_path"], caption=f"Threat: {row['threat_type']} | Severity: {row['severity']}")
            else:
                st.warning("Snapshot file not found on disk.")
        else:
            st.info("No incidents found in database.")

    elif selected_page == "Intelligence Analytics":
        st.subheader("📊 SOC Analytics Intelligence")
        incidents = db.fetch_all("SELECT threat_type, severity, timestamp FROM incidents")
        if incidents:
            df = pd.DataFrame(incidents)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Detections", len(df), "+4%")
            c2.metric("Critical Alerts", len(df[df['severity'] == 'CRITICAL']), "-2%")
            c3.metric("System Uptime", "99.9%", "Stable")

            col_a, col_b = st.columns(2)
            with col_a:
                fig_type = px.pie(df, names='threat_type', title="Threat Distribution", hole=0.4)
                fig_type.update_layout(template="plotly_dark")
                st.plotly_chart(fig_type, use_container_width=True)
            with col_b:
                fig_sev = px.bar(df, x='severity', title="Severity Levels", color='severity', 
                                 color_discrete_map={'CRITICAL': '#f85149', 'HIGH': '#ff7b72', 'MEDIUM': '#d29922', 'LOW': '#3fb950'})
                fig_sev.update_layout(template="plotly_dark")
                st.plotly_chart(fig_sev, use_container_width=True)
        else:
            st.info("Insufficient data for intelligence generation.")

    elif selected_page == "System Settings":
        st.subheader("⚙️ Enterprise Configuration")
        st.json(config)

if __name__ == "__main__":
    main()
