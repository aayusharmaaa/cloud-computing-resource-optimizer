"""
==========================================================
  Cloud Resource Optimizer — LSTM Training Script
==========================================================

  Train the multivariate LSTM model using Alibaba
  Cluster Trace 2018 production data.

  Usage:
    python train_model.py

  Prerequisites:
    1. Place machine_usage.csv in backend/data/ (optional)
    2. pip install -r requirements.txt
==========================================================
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from model.lstm_model import LSTMModel, DATASET_FILE


def main():
    print()
    print("=" * 60)
    print("  Cloud Resource Optimizer — Model Training")
    print("=" * 60)
    print()

    if os.path.exists(DATASET_FILE):
        size_mb = os.path.getsize(DATASET_FILE) / (1024 * 1024)
        print(f"  Dataset found: {DATASET_FILE}")
        print(f"  File size: {size_mb:.1f} MB")
        print("  Training on real Alibaba production data")
    else:
        print(f"  Dataset not found at: {DATASET_FILE}")
        print("  Will train on synthetic fallback data")
        print("  Place machine_usage.csv in backend/data/ for real training")

    print()

    model_path = os.path.join("models", "lstm_model.h5")
    if os.path.exists(model_path):
        os.remove(model_path)
        print(f"  Removed old model: {model_path}")

    print()

    start = time.time()
    model = LSTMModel()
    trained = model.train()
    elapsed = time.time() - start

    print()
    if not trained:
        print("=" * 60)
        print("  Training failed — server will use fallback predictor")
        print("=" * 60)
        sys.exit(1)

    print("=" * 60)
    print(f"  Training complete in {elapsed:.1f} seconds")
    print(f"  Model saved to: {model_path}")
    print("=" * 60)
    print()

    print("  Running test prediction...")
    test_cpu = [45, 48, 52, 55, 60, 63, 67, 70, 73, 75]
    test_mem = [60, 62, 63, 65, 68, 70, 72, 74, 76, 78]
    test_net = [30, 31, 32, 33, 35, 36, 38, 40, 42, 44]
    test_disk = [5, 5, 6, 6, 7, 7, 8, 8, 9, 10]

    predicted_cpu = model.predict(test_cpu, test_mem, test_net, test_disk)
    confidence = model.get_prediction_confidence(test_cpu)

    print(f"  Input CPU trend:  {test_cpu}")
    print(f"  Predicted next:   {predicted_cpu:.1f}%")
    print(f"  Confidence:       {confidence:.2f}")
    print()


if __name__ == "__main__":
    main()
