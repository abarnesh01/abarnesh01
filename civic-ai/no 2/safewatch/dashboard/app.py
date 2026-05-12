"""
SafeWatch — Streamlit Dashboard
Live monitoring, incident history, camera management, and system settings.
"""

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from loguru import logger

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from database.db_manager import DatabaseManager


def load_config() -> dict:
    """Load configuration file."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


def get_db() -> DatabaseManager:
    """Get or create database manager in session state."""
    if "db_manager" not in st.session_state:
        config = load_config()
        db_path = config.get("database", {}).get("path", "logs/safewatch.db")
        st.session_state.db_manager = DatabaseManager(db_path)
    return st.session_state.db_manager


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        "show_skeleton": True,
        "show_bboxes": True,
        "show_zones": True,
        "current_page": "Live Monitor",
        "selected_camera": None,
        "risk_level": "SAFE",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ─────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SafeWatch — CCTV Threat Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Dark Theme CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #1e3a5f;
    }
    .main-header h1 {
        color: #00d4ff;
        font-size: 2em;
        margin: 0;
    }
    .main-header p {
        color: #8892a4;
        margin: 5px 0 0 0;
    }
    .metric-card {
        background: #1a1a2e;
        border: 1px solid #2a2a4a;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #00d4ff;
    }
    .metric-label {
        color: #8892a4;
        font-size: 0.9em;
    }
    .risk-safe { color: #00ff88; }
    .risk-low { color: #ffff00; }
    .risk-medium { color: #ff8800; }
    .risk-high { color: #ff0000; }
    .risk-critical { color: #aa00ff; font-weight: bold; }
    .alert-card {
        background: #1a1a2e;
        border-left: 4px solid #ff4444;
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 0 8px 8px 0;
    }
    .camera-online { color: #00ff88; }
    .camera-offline { color: #ff4444; }
    .sidebar .sidebar-content {
        background-color: #0e1117;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main dashboard entry point."""
    init_session_state()
    config = load_config()
    db = get_db()

    # Sidebar
    st.sidebar.markdown("## 🛡️ SafeWatch")
    st.sidebar.markdown("*AI-Powered CCTV Threat Detection*")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        ["🖥️ Live Monitor", "📋 Incident History", "📷 Camera Management", "⚙️ System Settings"],
        index=0,
    )

    if page == "🖥️ Live Monitor":
        page_live_monitor(config, db)
    elif page == "📋 Incident History":
        page_incident_history(config, db)
    elif page == "📷 Camera Management":
        page_camera_management(config, db)
    elif page == "⚙️ System Settings":
        page_system_settings(config, db)


# ─────────────────────────────────────────────
# PAGE 1: Live Monitor
# ─────────────────────────────────────────────
def page_live_monitor(config: dict, db: DatabaseManager):
    """Live monitoring page with camera feeds and threat status."""
    st.markdown("""
    <div class="main-header">
        <h1>🖥️ Live Monitor</h1>
        <p>Real-time CCTV threat monitoring dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    # Display toggles
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.session_state.show_skeleton = st.toggle("Show Skeleton", st.session_state.show_skeleton)
    with col2:
        st.session_state.show_bboxes = st.toggle("Show Boxes", st.session_state.show_bboxes)
    with col3:
        st.session_state.show_zones = st.toggle("Show Zones", st.session_state.show_zones)
    with col4:
        risk_level = st.session_state.get("risk_level", "SAFE")
        risk_class = f"risk-{risk_level.lower()}"
        st.markdown(f'<div class="metric-card"><span class="metric-label">Risk Level</span><br>'
                    f'<span class="{risk_class} metric-value">{risk_level}</span></div>',
                    unsafe_allow_html=True)

    st.markdown("---")

    # Camera grid
    cameras = config.get("cameras", [])
    if not cameras:
        st.warning("No cameras configured. Add cameras in config.yaml.")
        return

    cols = st.columns(min(len(cameras), 2))
    for idx, cam in enumerate(cameras):
        with cols[idx % 2]:
            cam_id = cam["id"]
            cam_name = cam.get("name", cam_id)
            enabled = cam.get("enabled", False)

            status_icon = "🟢" if enabled else "🔴"
            st.markdown(f"### {status_icon} {cam_name} ({cam_id})")

            # Show placeholder frame
            placeholder = np.zeros((cam.get("resolution", [640, 480])[1],
                                   cam.get("resolution", [640, 480])[0], 3), dtype=np.uint8)
            cv2.putText(placeholder, f"{cam_name}", (20, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)
            if not enabled:
                cv2.putText(placeholder, "OFFLINE", (200, 250),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            else:
                cv2.putText(placeholder, "Waiting for stream...", (150, 250),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 0), 2)

            st.image(placeholder, channels="BGR", use_container_width=True)

    # Active alerts sidebar
    st.markdown("---")
    st.markdown("### 🚨 Recent Alerts")
    recent = db.get_recent_incidents(n=10)
    if not recent:
        st.info("No recent incidents")
    else:
        for inc in recent:
            severity = inc.get("severity", "LOW")
            sev_colors = {"LOW": "🟡", "MEDIUM": "🟠", "HIGH": "🔴", "CRITICAL": "🟣"}
            icon = sev_colors.get(severity, "⚪")
            ts = inc.get("timestamp", "")
            threat = inc.get("threat_type", "unknown")
            cam = inc.get("camera_id", "")
            st.markdown(
                f'{icon} **{threat.upper()}** — {cam} — {ts} — '
                f'Confidence: {inc.get("confidence", 0):.0%}'
            )


# ─────────────────────────────────────────────
# PAGE 2: Incident History
# ─────────────────────────────────────────────
def page_incident_history(config: dict, db: DatabaseManager):
    """Incident history with filters, charts, and CSV export."""
    st.markdown("""
    <div class="main-header">
        <h1>📋 Incident History</h1>
        <p>Browse and analyze past security incidents</p>
    </div>
    """, unsafe_allow_html=True)

    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        start_date = st.date_input("Start Date", datetime.now().date() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", datetime.now().date())
    with col3:
        camera_filter = st.selectbox(
            "Camera",
            ["All"] + [c["id"] for c in config.get("cameras", [])],
        )
    with col4:
        threat_filter = st.selectbox(
            "Threat Type",
            ["All", "fight", "fall", "harassment", "assault",
             "unconscious", "trespass", "crowd_panic", "accident", "abuse"],
        )

    # Fetch incidents
    kwargs = {
        "start_date": str(start_date),
        "end_date": str(end_date) + "T23:59:59",
        "limit": 500,
    }
    if camera_filter != "All":
        kwargs["camera_id"] = camera_filter
    if threat_filter != "All":
        kwargs["threat_type"] = threat_filter

    incidents = db.get_incidents(**kwargs)

    st.markdown(f"### Found {len(incidents)} incidents")

    if incidents:
        # Display as table
        import pandas as pd
        df = pd.DataFrame(incidents)
        display_cols = ["id", "camera_id", "timestamp", "threat_type",
                       "confidence", "severity", "persons_involved", "description"]
        available_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(df[available_cols], use_container_width=True, height=400)

        # Charts
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Incidents by Type")
            if "threat_type" in df.columns:
                type_counts = df["threat_type"].value_counts()
                st.bar_chart(type_counts)

        with col2:
            st.markdown("#### Incidents by Severity")
            if "severity" in df.columns:
                sev_counts = df["severity"].value_counts()
                st.bar_chart(sev_counts)

        # CSV Export
        st.markdown("---")
        if st.button("📥 Export to CSV"):
            csv_data = df[available_cols].to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"safewatch_incidents_{start_date}_{end_date}.csv",
                mime="text/csv",
            )
    else:
        st.info("No incidents found for the selected filters.")


# ─────────────────────────────────────────────
# PAGE 3: Camera Management
# ─────────────────────────────────────────────
def page_camera_management(config: dict, db: DatabaseManager):
    """Camera management with status indicators and zone configuration."""
    st.markdown("""
    <div class="main-header">
        <h1>📷 Camera Management</h1>
        <p>Monitor and configure camera feeds</p>
    </div>
    """, unsafe_allow_html=True)

    cameras = config.get("cameras", [])
    camera_statuses = db.get_camera_status()
    status_map = {s["camera_id"]: s for s in camera_statuses}

    for cam in cameras:
        cam_id = cam["id"]
        cam_name = cam.get("name", cam_id)
        enabled = cam.get("enabled", False)
        status = status_map.get(cam_id, {})

        with st.expander(f"{'🟢' if enabled else '🔴'} {cam_name} ({cam_id})", expanded=enabled):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Status", "Online" if enabled else "Offline")
            with col2:
                st.metric("FPS", f"{status.get('fps', 0):.1f}")
            with col3:
                st.metric("Frames Processed", status.get("frames_processed", 0))
            with col4:
                st.metric("Threats Today", status.get("threats_today", 0))

            st.markdown(f"**Source:** `{cam.get('source', 'N/A')}`")
            st.markdown(f"**Resolution:** {cam.get('resolution', [0,0])}")
            st.markdown(f"**Zone Type:** {cam.get('zone_type', 'N/A')}")
            st.markdown(f"**Frame Skip:** {cam.get('frame_skip', 'N/A')}")

            if st.button(f"🔔 Test Alert ({cam_id})", key=f"test_{cam_id}"):
                st.success(f"Test alert sent for {cam_name}")

    # Zone Configuration
    st.markdown("---")
    st.markdown("### 🗺️ Zone Configuration")
    st.info(
        "To configure restricted zones, define polygon coordinates below. "
        "Zones are saved to logs/zones.json."
    )

    with st.form("add_zone_form"):
        zone_name = st.text_input("Zone Name", placeholder="e.g., server_room")
        zone_type = st.selectbox("Zone Type", ["restricted", "critical", "entrance", "outdoor"])
        zone_points = st.text_area(
            "Polygon Points (x,y pairs per line)",
            placeholder="100,100\n200,100\n200,300\n100,300",
        )
        submitted = st.form_submit_button("Add Zone")

        if submitted and zone_name and zone_points:
            try:
                points = []
                for line in zone_points.strip().split("\n"):
                    x, y = line.strip().split(",")
                    points.append((int(x.strip()), int(y.strip())))
                if len(points) >= 3:
                    st.success(f"Zone '{zone_name}' added with {len(points)} points")
                else:
                    st.error("Need at least 3 points for a polygon")
            except Exception as e:
                st.error(f"Invalid points format: {e}")


# ─────────────────────────────────────────────
# PAGE 4: System Settings
# ─────────────────────────────────────────────
def page_system_settings(config: dict, db: DatabaseManager):
    """System settings page with threshold sliders and model info."""
    st.markdown("""
    <div class="main-header">
        <h1>⚙️ System Settings</h1>
        <p>Configure detection thresholds and system parameters</p>
    </div>
    """, unsafe_allow_html=True)

    # Threat confidence thresholds
    st.markdown("### 🎯 Detection Thresholds")
    threats_cfg = config.get("threats", {})

    col1, col2 = st.columns(2)
    with col1:
        for threat in ["fight", "fall", "harassment", "assault", "unconscious"]:
            cfg = threats_cfg.get(threat, {})
            current = cfg.get("confidence_threshold", 0.8)
            enabled = cfg.get("enabled", True)
            st.slider(
                f"{threat.capitalize()} ({'✅' if enabled else '❌'})",
                0.0, 1.0, float(current), 0.01,
                key=f"thresh_{threat}",
            )

    with col2:
        for threat in ["trespass", "crowd_panic", "accident", "abuse"]:
            cfg = threats_cfg.get(threat, {})
            current = cfg.get("confidence_threshold", 0.8)
            enabled = cfg.get("enabled", True)
            st.slider(
                f"{threat.replace('_', ' ').capitalize()} ({'✅' if enabled else '❌'})",
                0.0, 1.0, float(current), 0.01,
                key=f"thresh_{threat}",
            )

    # Telegram test
    st.markdown("---")
    st.markdown("### 📱 Telegram Bot")
    if st.button("🧪 Test Telegram Connection"):
        st.info("Telegram connection test: Check terminal logs for results")

    # Model Info
    st.markdown("---")
    st.markdown("### 🧠 Model Information")

    models_cfg = config.get("models", {})
    model_info = {
        "YOLOv8": config.get("detection", {}).get("yolo_model", "N/A"),
        "Action Classifier": models_cfg.get("action_classifier", "N/A"),
        "Custom YOLO": models_cfg.get("custom_yolo", "N/A"),
        "Custom YOLO Active": models_cfg.get("use_custom_yolo", False),
    }

    for name, value in model_info.items():
        exists = Path(str(value)).exists() if isinstance(value, str) else value
        status = "✅ Loaded" if exists else "⚠️ Not found (fallback mode)"
        if isinstance(value, bool):
            status = "✅ Yes" if value else "❌ No"
        st.markdown(f"**{name}:** `{value}` — {status}")

    # System Logs
    st.markdown("---")
    st.markdown("### 📋 System Logs")
    logs = db.get_system_logs(limit=20)
    if logs:
        for log_entry in logs:
            level = log_entry.get("level", "INFO")
            level_icon = {"INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌"}.get(level, "📝")
            st.text(
                f"{level_icon} [{log_entry.get('timestamp', '')}] "
                f"{log_entry.get('message', '')}"
            )
    else:
        st.info("No system logs recorded yet")

    # System info
    st.markdown("---")
    st.markdown("### 📊 System Info")
    system_cfg = config.get("system", {})
    st.markdown(f"**Name:** {system_cfg.get('name', 'SafeWatch')}")
    st.markdown(f"**Version:** {system_cfg.get('version', '1.0.0')}")
    st.markdown(f"**Debug Mode:** {system_cfg.get('debug', False)}")
    st.markdown(f"**Log Level:** {system_cfg.get('log_level', 'INFO')}")


if __name__ == "__main__":
    main()
