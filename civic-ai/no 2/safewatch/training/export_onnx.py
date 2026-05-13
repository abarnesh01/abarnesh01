import torch
import torch.onnx
from training.train_classifier import ActionLSTM
from loguru import logger

def export_to_onnx(pth_path: str, onnx_path: str, input_dim: int = 66, seq_len: int = 30, num_classes: int = 5):
    """
    Exports a trained PyTorch model to ONNX format for efficient CPU inference.
    """
    # 1. Initialize model
    model = ActionLSTM(input_dim=input_dim, hidden_dim=128, num_layers=2, num_classes=num_classes)
    
    # 2. Load state dict
    try:
        model.load_state_dict(torch.load(pth_path, map_location='cpu'))
        model.eval()
        logger.info(f"Loaded weights from {pth_path}")
    except Exception as e:
        logger.error(f"Failed to load weights: {e}")
        return

    # 3. Create dummy input
    dummy_input = torch.randn(1, seq_len, input_dim)
    
    # 4. Export
    torch.onnx.export(
        model, 
        dummy_input, 
        onnx_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    
    logger.success(f"Model successfully exported to {onnx_path}")

if __name__ == "__main__":
    # export_to_onnx("models/action_classifier.pth", "models/action_classifier.onnx")
    pass
