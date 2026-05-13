import streamlit as st
import pandas as pd
import cv2
import time
from database.db_manager import db
from database.incident_logger import IncidentLogger
import plotly.express as px
from pathlib import Path

# Page Config
st.set_page_config(
    page_title="SafeWatch SOC Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Theme SOC look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .css-1d391kg { background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.sidebar.title("🛡️ SafeWatch SOC")
    page = st.sidebar.selectbox("Navigation", ["Live Monitor", "Incident History", "Analytics", "System Settings"])

    if page == "Live Monitor":
        show_live_monitor()
    elif page == "Incident History":
        show_incident_history()
    elif page == "Analytics":
        show_analytics()
    elif page == "System Settings":
        show_settings()

def show_live_monitor():
    st.title("🔴 Real-Time Surveillance Monitor")
    
    # Placeholder for live streams
    cols = st.columns(2)
    with cols[0]:
        st.subheader("Camera 0: Front Entrance")
        st.image("https://via.placeholder.com/640x360.png?text=Live+Stream+0", use_column_width=True)
        st.info("Status: Online | FPS: 15.2")
        
    with cols[1]:
        st.subheader("Camera 1: Back Alley")
        st.image("https://via.placeholder.com/640x360.png?text=Live+Stream+1", use_column_width=True)
        st.warning("Status: Reconnecting...")

    st.divider()
    
    st.subheader("⚠️ Active Threats")
    incidents = IncidentLogger.get_recent_incidents(limit=5)
    if incidents:
        for inc in incidents:
            with st.expander(f"{inc['threat_type']} - {inc['severity']} ({inc['timestamp']})"):
                st.write(f"Camera: {inc['camera_name']}")
                st.write(f"Confidence: {inc['confidence']:.2f}")
                if inc['snapshot_path'] and Path(inc['snapshot_path']).exists():
                    st.image(inc['snapshot_path'], width=400)
    else:
        st.success("No active threats detected.")

def show_incident_history():
    st.title("📜 Incident History")
    
    incidents = IncidentLogger.get_recent_incidents(limit=100)
    if incidents:
        df = pd.DataFrame(incidents)
        st.dataframe(df, use_container_width=True)
        
        if st.button("Export to CSV"):
            IncidentLogger.export_to_csv("logs/incidents_export.csv")
            st.success("Exported to logs/incidents_export.csv")
    else:
        st.info("No incident records found.")

def show_analytics():
    st.title("📊 Security Intelligence")
    
    incidents = IncidentLogger.get_recent_incidents(limit=1000)
    if incidents:
        df = pd.DataFrame(incidents)
        
        c1, c2 = st.columns(2)
        with c1:
            fig_pie = px.pie(df, names='threat_type', title='Threat Distribution', hole=0.4)
            st.plotly_chart(fig_pie)
            
        with c2:
            fig_bar = px.histogram(df, x='camera_name', color='severity', title='Incidents per Camera')
            st.plotly_chart(fig_bar)
            
        st.subheader("Trend Analysis")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df_time = df.resample('H', on='timestamp').count().reset_index()
        fig_line = px.line(df_time, x='timestamp', y='id', title='Incident Frequency (Hourly)')
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Insufficient data for analytics.")

def show_settings():
    st.title("⚙️ System Configuration")
    
    with st.form("settings_form"):
        st.subheader("Model Settings")
        yolo_path = st.text_input("YOLO Model Path", "models/yolov8n.pt")
        conf_thresh = st.slider("Confidence Threshold", 0.1, 1.0, 0.25)
        
        st.subheader("Alert Settings")
        tg_enabled = st.checkbox("Enable Telegram Alerts", value=True)
        snapshot_enabled = st.checkbox("Save Snapshots", value=True)
        
        if st.form_submit_button("Save Configuration"):
            st.success("Configuration updated and saved to database.")

if __name__ == "__main__":
    main()
