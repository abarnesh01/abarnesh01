# SafeWatch — AI-Powered CCTV Threat Detection System

SafeWatch is an enterprise-grade AI-powered surveillance ecosystem designed for real-time threat detection and behavioral intelligence. It leverages state-of-the-art computer vision models (YOLOv8, MediaPipe) and temporal analytics to identify security incidents autonomously.

## 🚀 Features

- **Real-Time Threat Detection**:
  - Fight & Assault detection (Aggressive proximity & limb velocity)
  - Fall detection (Horizontal posture & impact analysis)
  - Harassment detection (Sustained proximity tracking)
  - Unconscious person detection (Prolonged stillness)
  - Crowd Panic & Accident detection (Optical flow & group dynamics)
  - Trespassing (Custom zone monitoring)
- **Multi-Camera Support**: Optimized RTSP and USB webcam handling.
- **Enterprise Alerting**: Automated Telegram notifications with branded snapshots.
- **SOC Dashboard**: Dark-themed Streamlit monitoring and analytics platform.
- **CPU Optimized**: Designed for high-performance inference on standard hardware.

## 🛠️ Tech Stack

- **Inference**: YOLOv8, MediaPipe, ONNX Runtime
- **Logic**: Python 3.10+, OpenCV, NumPy, SciPy
- **Storage**: SQLite3
- **Monitoring**: Streamlit, Plotly
- **Alerts**: python-telegram-bot (Async)
- **Logging**: Loguru

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <repo_url>
   cd safewatch
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   - Rename `.env.example` to `.env`
   - Add your `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.

4. **Initialize Model**:
   - SafeWatch will automatically download `yolov8n.pt` on first run.

## 🚦 Usage

### Start the Surveillance Core:
```bash
python main.py
```

### Launch the SOC Dashboard:
```bash
streamlit run dashboard/app.py
```

## 🏗️ Project Structure

```text
safewatch/
├── capture/        # Video capture & stream management
├── detection/      # AI models & low-level vision
├── threats/        # Behavioral intelligence & threat logic
├── classifier/     # Temporal action classification
├── alerts/         # Notification & snapshot systems
├── database/       # Incident logging & analytics
├── dashboard/      # Streamlit monitor
└── training/       # Google Colab training pipeline
```

## 🛡️ Engineering Standards

- **Thread-Safe Architecture**: Non-blocking frame capture and async alerting.
- **Graceful Recovery**: Automatic stream reconnection and error handling.
- **Modular Design**: Easy to extend with custom detectors or models.

---
**SafeWatch** | Built for Enterprise Security Operations.
