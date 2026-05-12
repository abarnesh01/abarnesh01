from setuptools import setup, find_packages

setup(
    name="safewatch",
    version="1.0.0",
    author="SafeWatch Team",
    description="AI-Powered CCTV Threat Detection System",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "opencv-python",
        "ultralytics",
        "mediapipe",
        "onnxruntime",
        "pyyaml",
        "python-dotenv",
        "loguru",
        "streamlit",
        "pandas",
        "pillow",
        "python-telegram-bot",
        "scipy",
    ],
    entry_points={
        "console_scripts": [
            "safewatch=main:main",
        ],
    },
    python_requires=">=3.10",
)
