# 26.06.25 pzt 
# transfer learning

from ultralytics import YOLO

def train():
    model = YOLO("yolov8n.pt")
    model.train(data="data.yaml", epochs=10, imgsz=640, batch=8)


if __name__ == "__main__":
    train()