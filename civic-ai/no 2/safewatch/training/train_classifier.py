import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from loguru import logger

class ActionLSTM(nn.Module):
    """LSTM-based architecture for human action classification."""
    def __init__(self, input_dim, hidden_dim, num_layers, num_classes):
        super(ActionLSTM, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_dim, num_classes)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        h0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        c0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :]) # Take last time step
        return out

class SkeletonDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)
        
    def __len__(self):
        return len(self.y)
        
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

def train_model(csv_path: str, model_save_path: str):
    # Load data
    df = pd.read_csv(csv_path)
    X = np.array([eval(s) for s in df['sequence']]) # (N, seq_len * 66)
    X = X.reshape(X.shape[0], 30, 66) # (N, 30, 66)
    
    le = LabelEncoder()
    y = le.fit_transform(df['label'])
    num_classes = len(le.classes_)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    train_loader = DataLoader(SkeletonDataset(X_train, y_train), batch_size=32, shuffle=True)
    test_loader = DataLoader(SkeletonDataset(X_test, y_test), batch_size=32)
    
    # Model Setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ActionLSTM(input_dim=66, hidden_dim=128, num_layers=2, num_classes=num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training Loop
    logger.info("Starting training...")
    for epoch in range(50):
        model.train()
        total_loss = 0
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
        if (epoch+1) % 10 == 0:
            logger.info(f"Epoch {epoch+1}/50, Loss: {total_loss/len(train_loader):.4f}")
            
    # Save Model
    torch.save(model.state_dict(), model_save_path)
    logger.success(f"Model saved to {model_save_path}")

if __name__ == "__main__":
    # train_model("data/skeleton_dataset.csv", "models/action_classifier.pth")
    pass
