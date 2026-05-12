"""
SafeWatch — LSTM Action Classifier Training (Google Colab)
Trains an LSTM-based action classifier on pose sequences.
"""

import os
from pathlib import Path
from typing import Optional

import numpy as np


def train_classifier(
    data_dir: str = "data",
    output_dir: str = "models",
    epochs: int = 50,
    batch_size: int = 32,
    lr: float = 0.001,
    seq_len: int = 30,
    hidden_size: int = 256,
    num_layers: int = 2,
    dropout: float = 0.3,
    patience: int = 10,
):
    """Train the LSTM action classifier."""
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
    from sklearn.metrics import classification_report, confusion_matrix, f1_score
    import matplotlib.pyplot as plt
    import seaborn as sns

    ACTION_CLASSES = [
        "normal", "fight", "fall", "assault", "harassment",
        "abuse", "panic", "unconscious", "other",
    ]
    num_classes = len(ACTION_CLASSES)
    input_dim = 99  # 33 landmarks * 3 coords (x, y, z)

    # ─── Dataset ─────────────────────────────────
    class PoseSequenceDataset(Dataset):
        """Dataset of pose landmark sequences with action labels."""

        def __init__(self, root_dir: str, seq_length: int = 30):
            self.seq_length = seq_length
            self.samples = []
            self.labels = []

            root = Path(root_dir)
            for cls_idx, cls_name in enumerate(ACTION_CLASSES):
                cls_dir = root / cls_name
                if not cls_dir.exists():
                    continue

                npy_files = sorted(cls_dir.glob("*.npy"))

                # Group files into sequences of seq_length
                for i in range(0, len(npy_files) - seq_length + 1, seq_length // 2):
                    seq_files = npy_files[i:i + seq_length]
                    if len(seq_files) == seq_length:
                        self.samples.append(seq_files)
                        self.labels.append(cls_idx)

                # If not enough for full sequence, pad with repetition
                if npy_files and len(npy_files) < seq_length:
                    padded = list(npy_files)
                    while len(padded) < seq_length:
                        padded.append(npy_files[-1])
                    self.samples.append(padded[:seq_length])
                    self.labels.append(cls_idx)

            print(f"Loaded {len(self.samples)} sequences from {root_dir}")

        def __len__(self):
            return len(self.samples)

        def __getitem__(self, idx):
            seq_files = self.samples[idx]
            label = self.labels[idx]

            sequence = np.zeros((self.seq_length, input_dim), dtype=np.float32)
            for i, f in enumerate(seq_files):
                try:
                    landmarks = np.load(str(f))  # Shape: (33, 3)
                    sequence[i] = landmarks.flatten()[:input_dim]
                except Exception:
                    pass  # Zeros for failed loads

            return torch.FloatTensor(sequence), torch.LongTensor([label])[0]

    # ─── Model ─────────────────────────────────
    class ActionLSTM(nn.Module):
        """LSTM-based action classifier."""

        def __init__(self):
            super().__init__()
            self.lstm = nn.LSTM(
                input_size=input_dim,
                hidden_size=hidden_size,
                num_layers=num_layers,
                dropout=dropout,
                batch_first=True,
                bidirectional=False,
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
            return output

    # ─── Training ─────────────────────────────────
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on: {device}")

    train_dataset = PoseSequenceDataset(os.path.join(data_dir, "train"), seq_len)
    val_dataset = PoseSequenceDataset(os.path.join(data_dir, "val"), seq_len)

    if len(train_dataset) == 0:
        print("❌ No training data found. Run dataset_prep.py first.")
        return

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)

    model = ActionLSTM().to(device)
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Class weights for imbalanced data
    label_counts = np.bincount(train_dataset.labels, minlength=num_classes)
    label_counts = np.maximum(label_counts, 1)  # Avoid division by zero
    weights = 1.0 / label_counts.astype(np.float32)
    weights = weights / weights.sum() * num_classes
    class_weights = torch.FloatTensor(weights).to(device)

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    # Training loop
    best_val_f1 = 0.0
    patience_counter = 0
    train_losses = []
    val_losses = []
    val_f1s = []

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for epoch in range(epochs):
        # Train
        model.train()
        total_loss = 0.0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()

        avg_train_loss = total_loss / max(len(train_loader), 1)
        train_losses.append(avg_train_loss)

        # Validate
        model.eval()
        val_loss = 0.0
        all_preds = []
        all_labels = []

        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)
                val_loss += loss.item()
                preds = torch.argmax(outputs, dim=1)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(batch_y.cpu().numpy())

        avg_val_loss = val_loss / max(len(val_loader), 1)
        val_losses.append(avg_val_loss)

        if all_labels:
            val_f1 = f1_score(all_labels, all_preds, average="weighted", zero_division=0)
        else:
            val_f1 = 0.0
        val_f1s.append(val_f1)

        scheduler.step()

        print(
            f"Epoch {epoch+1}/{epochs} — "
            f"Train Loss: {avg_train_loss:.4f} — "
            f"Val Loss: {avg_val_loss:.4f} — "
            f"Val F1: {val_f1:.4f}"
        )

        # Early stopping
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            patience_counter = 0
            torch.save(model.state_dict(), str(output_path / "action_classifier.pt"))
            print(f"  ✅ Best model saved (F1={val_f1:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"  ⏹️ Early stopping at epoch {epoch+1}")
                break

    # ─── Evaluation ─────────────────────────────────
    print("\n" + "=" * 60)
    print("FINAL EVALUATION")
    print("=" * 60)

    model.load_state_dict(torch.load(str(output_path / "action_classifier.pt")))
    model.eval()

    all_preds = []
    all_labels = []
    with torch.no_grad():
        for batch_x, batch_y in val_loader:
            batch_x = batch_x.to(device)
            outputs = model(batch_x)
            preds = torch.argmax(outputs, dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(batch_y.numpy())

    if all_labels:
        present_classes = sorted(set(all_labels) | set(all_preds))
        target_names = [ACTION_CLASSES[i] for i in present_classes]
        print("\nClassification Report:")
        print(classification_report(all_labels, all_preds,
                                    labels=present_classes,
                                    target_names=target_names,
                                    zero_division=0))

        # Confusion matrix
        cm = confusion_matrix(all_labels, all_preds, labels=present_classes)
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=target_names, yticklabels=target_names)
        plt.title("SafeWatch Action Classifier — Confusion Matrix")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.tight_layout()
        plt.savefig(str(output_path / "confusion_matrix.png"), dpi=150)
        plt.show()
        print(f"Confusion matrix saved to {output_path / 'confusion_matrix.png'}")

    # Training curves
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label="Train Loss")
    plt.plot(val_losses, label="Val Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Training & Validation Loss")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(val_f1s, label="Val F1", color="green")
    plt.xlabel("Epoch")
    plt.ylabel("F1 Score")
    plt.title("Validation F1 Score")
    plt.legend()

    plt.tight_layout()
    plt.savefig(str(output_path / "training_curves.png"), dpi=150)
    plt.show()
    print(f"Training curves saved to {output_path / 'training_curves.png'}")
    print(f"\nBest model: {output_path / 'action_classifier.pt'}")
    print(f"Best Val F1: {best_val_f1:.4f}")


if __name__ == "__main__":
    train_classifier()
