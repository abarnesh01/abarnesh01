from setuptools import setup, find_packages

setup(
    name="safewatch",
    version="1.0.0",
    description="Enterprise AI CCTV Threat Detection System",
    author="SafeWatch Team",
    packages=find_packages(),
    install_requires=[
        "ultralytics",
        "mediapipe",
        "opencv-contrib-python",
        "loguru",
        "pyyaml",
        "python-dotenv",
        "streamlit",
        "python-telegram-bot",
        "onnxruntime"
    ],
    entry_points={
        "console_scripts": [
            "safewatch=main:main",
        ],
    },
    python_requires=">=3.10",
)
