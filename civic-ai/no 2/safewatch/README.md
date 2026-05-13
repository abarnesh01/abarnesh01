# SafeWatch — AI-Powered CCTV Threat Detection System

SafeWatch is an enterprise-grade surveillance intelligence platform designed for real-time threat detection and behavioral analysis. It leverages state-of-the-art computer vision models (YOLOv8, MediaPipe) and custom LSTM action classifiers to identify security incidents automatically.

## Core Features

- **Threat Detection**: Fight, Fall, Harassment, Assault, Unconscious Person, Crowd Panic, Accident, Trespassing, and Abuse detection.
- **Real-Time Analytics**: Multi-threaded RTSP/USB stream processing with motion-aware sampling.
- **Behavioral Intelligence**: Skeleton landmark analysis, velocity tracking, and optical flow divergence.
- **Enterprise Alerting**: Automated Telegram notifications with annotated snapshots and severity levels.
- **SOC Dashboard**: Streamlit-powered dark-themed monitor with incident history and analytics.
- **Edge Optimized**: High-performance CPU inference via ONNX Runtime.

## Project Structure

```text
safewatch/
├── main.py              # System entry point
├── config.yaml          # Central configuration
├── capture/             # Multi-stream acquisition
├── detection/           # YOLOv8 & MediaPipe engines
├── classifier/          # LSTM Action classification
├── threats/             # Specialized threat detectors
├── alerts/              # Telegram & Snapshot logic
├── database/            # SQLite incident logging
├── dashboard/           # Streamlit SOC interface
└── training/            # AI model training pipeline
```

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   - Copy `.env.example` to `.env`
   - Add your `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`

3. **Run the System**:
   ```bash
   python main.py
   ```

4. **Launch Dashboard**:
   ```bash
   streamlit run dashboard/app.py
   ```

## Technology Stack

- **Computer Vision**: OpenCV, Ultralytics YOLOv8, MediaPipe
- **AI Inference**: ONNX Runtime, PyTorch
- **Backend**: SQLite, Loguru, PyYAML
- **Frontend**: Streamlit
- **Alerts**: python-telegram-bot

## License

Enterprise Production Build - Proprietary and Confidential.
