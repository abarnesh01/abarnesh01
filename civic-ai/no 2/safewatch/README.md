# SafeWatch 🛡️ — AI-Powered CCTV Threat Detection System

SafeWatch is a production-ready, modular AI surveillance system designed to detect physical threats, accidents, and unauthorized access in real-time. It leverages state-of-the-art computer vision (YOLOv8, MediaPipe) and behavioral analysis to provide instant alerts via Telegram and a live dashboard.

## 🚀 Key Features

- **Real-time Detection**: Person tracking, pose estimation, and optical flow analysis.
- **Threat Engine**: Detects fights, falls, harassment, assault, unconsciousness, trespass, and crowd panic.
- **Alert System**: Immediate Telegram notifications with annotated snapshots.
- **Live Dashboard**: Streamlit-based UI for live monitoring, incident history, and camera management.
- **Modular Architecture**: Easy to extend with custom detectors and models.
- **Robust Database**: SQLite-based logging with WAL mode for high concurrency.

## 🛠️ Tech Stack

- **Core**: Python 3.10+, OpenCV
- **AI/ML**: YOLOv8 (Ultralytics), MediaPipe, ONNX Runtime
- **Database**: SQLite (SQLAlchemy-ready logic)
- **UI**: Streamlit
- **Alerting**: Python-Telegram-Bot
- **Logging**: Loguru

## 📂 Project Structure

```
safewatch/
├── main.py              # System entry point
├── config.yaml          # Central configuration
├── requirements.txt     # Python dependencies
├── capture/             # Camera stream management
├── detection/           # YOLO & Pose detection
├── classifier/          # Behavioral feature extraction
├── threats/             # Specific threat detectors
├── alerts/              # Telegram & Snapshot logic
├── database/            # Incident logging & DB manager
├── dashboard/           # Streamlit UI
├── training/            # Model training scripts
├── models/              # Pre-trained models
└── tests/               # Unit & Integration tests
```

## 🔧 Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-repo/safewatch.git
    cd safewatch
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    Copy `.env.example` to `.env` and add your Telegram credentials:
    ```bash
    cp .env.example .env
    ```

4.  **Configure Cameras**:
    Edit `config.yaml` to add your RTSP or USB camera sources.

## 🚦 Usage

### Start the System
```bash
python main.py
```

### Run Only Dashboard
```bash
python main.py --dashboard-only
```

### Test Camera Connections
```bash
python main.py --test-cameras
```

### Test Telegram Bot
```bash
python main.py --test-telegram
```

## 🧠 Model Training

SafeWatch includes a custom Action Classifier. To train or improve the model:
1. See instructions in `training/README_COLAB.md`.
2. Use the provided scripts to extract pose sequences and train an LSTM classifier.
3. Export to ONNX and place in `models/`.

## 🛡️ License
Proprietary / Enterprise Surveillance License.

---
*Built with ❤️ for a safer world.*
