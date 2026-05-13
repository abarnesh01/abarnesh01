from ultralytics import YOLO
from loguru import logger

def train_custom_yolo(data_yaml: str = "data.yaml", epochs: int = 100):
    logger.info(f"Starting custom YOLO training with {data_yaml} for {epochs} epochs...")
    # model = YOLO("yolov8n.pt")
    # model.train(data=data_yaml, epochs=epochs, imgsz=640)
    logger.warning("Training is commented out to prevent resource exhaustion in this environment.")

if __name__ == "__main__":
    train_custom_yolo()
