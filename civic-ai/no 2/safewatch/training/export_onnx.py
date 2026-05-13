import torch
import torch.nn as nn
import json
from pathlib import Path
from loguru import logger

# Import the model architecture (must match train_classifier.py)
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

def export_to_onnx(pth_path: str = "models/action_classifier.pth", 
                   labels_path: str = "models/labels.json",
                   output_path: str = "models/action_classifier.onnx"):
    
    if not Path(pth_path).exists():
        logger.error(f"Model file not found: {pth_path}")
        return

    with open(labels_path, "r") as f:
        labels_map = json.load(f)
    
    num_classes = len(labels_map)
    model = ActionLSTM(input_size=34, hidden_size=64, num_layers=2, num_classes=num_classes)
    model.load_state_dict(torch.load(pth_path))
    model.eval()

    # Dummy input: (batch_size, sequence_length, input_size)
    dummy_input = torch.randn(1, 30, 34)
    
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=12,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    
    logger.info(f"Model exported to ONNX: {output_path}")

if __name__ == "__main__":
    # export_to_onnx()
    pass
