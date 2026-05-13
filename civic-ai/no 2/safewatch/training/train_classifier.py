import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from loguru import logger
from pathlib import Path

class ActionDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class ActionLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(ActionLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

def train_model(data_path: str = "training/data/processed_landmarks.json"):
    # 1. Load Data
    with open(data_path, "r") as f:
        dataset = json.load(f)
    
    labels_map = {label: i for i, label in enumerate(set([d["label"] for d in dataset]))}
    
    X, y = [], []
    for d in dataset:
        landmarks = d["landmarks"]
        # Ensure sequence length is exactly 30
        if len(landmarks) >= 30:
            X.append(landmarks[:30])
            y.append(labels_map[d["label"]])
            
    X = np.array(X)
    y = np.array(y)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    train_loader = DataLoader(ActionDataset(X_train, y_train), batch_size=32, shuffle=True)
    test_loader = DataLoader(ActionDataset(X_test, y_test), batch_size=32)
    
    # 2. Setup Model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ActionLSTM(input_size=34, hidden_size=64, num_layers=2, num_classes=len(labels_map)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # 3. Training Loop
    num_epochs = 50
    for epoch in range(num_epochs):
        model.train()
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        
        if (epoch+1) % 10 == 0:
            logger.info(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')
            
    # 4. Save Model
    torch.save(model.state_dict(), "models/action_classifier.pth")
    with open("models/labels.json", "w") as f:
        json.dump(labels_map, f)
    logger.info("Training complete. Model saved.")

if __name__ == "__main__":
    # train_model()
    pass
