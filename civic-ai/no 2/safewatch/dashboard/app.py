import streamlit as st
import cv2
import pandas as pd
from pathlib import Path
import time
from datetime import datetime
import os
import yaml

# Add parent directory to path to allow relative imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    st.set_page_config(page_title="SafeWatch SOC Dashboard", layout="wide", initial_sidebar_state="expanded")
    st.title("🛡️ SafeWatch - Enterprise Surveillance Intelligence")

    config = load_config()
    db = DatabaseManager(config["database"]["path"])

    # Sidebar
    st.sidebar.header("System Status")
    st.sidebar.info(f"Version: {config['system']['version']}")
    
    page = st.sidebar.selectbox("Navigation", ["Live Monitor", "Incident History", "Analytics", "Settings"])

    if page == "Live Monitor":
        st.header("Real-Time Camera Monitoring")
        
        cols = st.columns(2)
        for i, cam in enumerate(config["cameras"]):
            if cam["enabled"]:
                with cols[i % 2]:
                    st.subheader(f"{cam['name']} ({cam['id']})")
                    # In a real production build with Streamlit, we would use a WebRTC or MJPEG stream component
                    # Here we show a placeholder for the live feed
                    st.image("https://via.placeholder.com/640x360.png?text=SafeWatch+Live+Feed", use_column_width=True)
                    st.write(f"Source: `{cam['source']}`")

    elif page == "Incident History":
        st.header("Recent Threat Incidents")
        
        incidents = db.fetch_all("SELECT * FROM incidents ORDER BY timestamp DESC LIMIT 100")
        if incidents:
            df = pd.DataFrame(incidents)
            st.dataframe(df, use_container_width=True)
            
            # View snapshots
            st.subheader("Visual Evidence")
            selected_id = st.selectbox("Select Incident ID to view snapshot", df["id"].tolist())
            row = next(i for i in incidents if i["id"] == selected_id)
            if row["snapshot_path"] and os.path.exists(row["snapshot_path"]):
                st.image(row["snapshot_path"], caption=f"Incident {selected_id}: {row['threat_type']}")
            else:
                st.info("No snapshot available for this incident.")
        else:
            st.info("No incidents recorded yet.")

    elif page == "Analytics":
        st.header("System Analytics")
        incidents = db.fetch_all("SELECT threat_type, severity, timestamp FROM incidents")
        if incidents:
            df = pd.DataFrame(incidents)
            st.subheader("Incidents by Type")
            st.bar_chart(df["threat_type"].value_counts())
            
            st.subheader("Severity Distribution")
            st.pie_chart(df["severity"].value_counts())
        else:
            st.info("Insufficient data for analytics.")

    elif page == "Settings":
        st.header("System Configuration")
        st.json(config)

if __name__ == "__main__":
    main()
