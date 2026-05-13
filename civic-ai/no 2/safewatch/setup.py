from setuptools import setup, find_packages

setup(
    name="safewatch",
    version="1.0.0",
    description="Enterprise AI CCTV Threat Detection System",
    author="SafeWatch AI",
    packages=find_packages(),
    install_requires=[
        "opencv-python",
        "ultralytics",
        "mediapipe",
        "onnxruntime",
        "numpy",
        "scipy",
        "pyyaml",
        "python-telegram-bot",
        "streamlit",
        "imutils",
        "Pillow",
        "schedule",
        "loguru",
        "torch",
        "torchvision",
        "python-dotenv"
    ],
    entry_points={
        "console_scripts": [
            "safewatch=main:main",
        ],
    },
    python_requires=">=3.10",
)
