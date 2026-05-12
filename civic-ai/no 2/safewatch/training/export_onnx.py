"""
SafeWatch — ONNX Export (Google Colab)
Exports trained PyTorch action classifier to ONNX for CPU inference.
"""

import time
from pathlib import Path

import numpy as np


def export_onnx(
    model_path: str = "models/action_classifier.pt",
    output_path: str = "models/action_classifier.onnx",
    seq_len: int = 30,
    input_dim: int = 99,
    hidden_size: int = 256,
    num_layers: int = 2,
    num_classes: int = 9,
    dropout: float = 0.3,
):
    """Export trained PyTorch model to ONNX format."""
    import torch
    import torch.nn as nn

    print("=" * 60)
    print("SafeWatch — ONNX Model Export")
    print("=" * 60)

    # ─── Rebuild model architecture ─────────────────
    class ActionLSTM(nn.Module):
        def __init__(self):
            super().__init__()
            self.lstm = nn.LSTM(
                input_size=input_dim,
                hidden_size=hidden_size,
                num_layers=num_layers,
                dropout=dropout,
                batch_first=True,
            )
            self.fc = nn.Sequential(
                nn.Linear(hidden_size, 128),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(128, num_classes),
            )

        def forward(self, x):
            lstm_out, _ = self.lstm(x)
            last_hidden = lstm_out[:, -1, :]
            output = self.fc(last_hidden)
            return torch.softmax(output, dim=1)

    # ─── Load weights ─────────────────
    model_file = Path(model_path)
    if not model_file.exists():
        print(f"❌ Model file not found: {model_path}")
        print("   Train the model first using train_classifier.py")
        return

    model = ActionLSTM()
    model.load_state_dict(torch.load(str(model_file), map_location="cpu"))
    model.eval()
    print(f"✅ Loaded model from {model_path}")

    # ─── Export to ONNX ─────────────────
    dummy_input = torch.randn(1, seq_len, input_dim)
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    torch.onnx.export(
        model,
        dummy_input,
        str(output_file),
        input_names=["pose_sequence"],
        output_names=["action_probs"],
        dynamic_axes={
            "pose_sequence": {0: "batch_size"},
            "action_probs": {0: "batch_size"},
        },
        opset_version=17,
        do_constant_folding=True,
    )
    print(f"✅ ONNX model exported to {output_path}")

    # ─── Validate with ONNX Runtime ─────────────────
    import onnxruntime as ort

    session = ort.InferenceSession(str(output_file), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    test_input = np.random.randn(1, seq_len, input_dim).astype(np.float32)
    result = session.run([output_name], {input_name: test_input})
    probs = result[0][0]

    print(f"\n✅ ONNX validation passed")
    print(f"   Output shape: {result[0].shape}")
    print(f"   Sum of probs: {np.sum(probs):.4f} (should be ~1.0)")
    print(f"   Top class: {np.argmax(probs)} with prob {np.max(probs):.4f}")

    # ─── Speed benchmark ─────────────────
    print("\n📊 Speed Benchmark (100 iterations):")
    times = []
    for _ in range(100):
        test_input = np.random.randn(1, seq_len, input_dim).astype(np.float32)
        start = time.perf_counter()
        session.run([output_name], {input_name: test_input})
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    avg_ms = np.mean(times) * 1000
    std_ms = np.std(times) * 1000
    min_ms = np.min(times) * 1000
    max_ms = np.max(times) * 1000

    print(f"   Average: {avg_ms:.2f} ms")
    print(f"   Std Dev: {std_ms:.2f} ms")
    print(f"   Min:     {min_ms:.2f} ms")
    print(f"   Max:     {max_ms:.2f} ms")
    print(f"   Throughput: {1000/avg_ms:.0f} inferences/sec")

    # ─── Model info ─────────────────
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    param_count = sum(p.numel() for p in model.parameters())
    ram_estimate_mb = param_count * 4 / (1024 * 1024)  # float32

    print(f"\n📦 Model Info:")
    print(f"   File size: {file_size_mb:.2f} MB")
    print(f"   Parameters: {param_count:,}")
    print(f"   Estimated RAM: {ram_estimate_mb:.2f} MB")
    print(f"   Input:  pose_sequence [{seq_len} x {input_dim}]")
    print(f"   Output: action_probs [{num_classes}]")
    print(f"\n✅ Export complete! Copy {output_path} to your SafeWatch deployment.")


if __name__ == "__main__":
    export_onnx()
