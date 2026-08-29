import numpy as np
import pandas as pd
import os
import warnings
from config import settings

# Try to import TensorFlow, fallback to simple prediction if not available
try:
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping
    TENSORFLOW_AVAILABLE = True
except ImportError as e:
    TENSORFLOW_AVAILABLE = False
    warnings.warn(f"TensorFlow not available: {e}. Using simple prediction fallback.")


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATASET_FILE = os.path.join(DATA_DIR, "machine_usage.csv")

# Alibaba machine_usage.csv column names (no header in raw file)
COLUMN_NAMES = [
    "machine_id", "time_stamp", "cpu_util_percent", "mem_util_percent",
    "mem_gps", "mkpi", "net_in", "net_out", "disk_io_percent"
]

# The 4 key features we train on
FEATURE_COLS = ["cpu_util_percent", "mem_util_percent", "net_in", "disk_io_percent"]


class LSTMModel:
    def __init__(self):
        self.model = None
        self.model_path = os.path.join(settings.model_dir, "lstm_model.h5")
        self.sequence_length = settings.sequence_length
        os.makedirs(settings.model_dir, exist_ok=True)
        if TENSORFLOW_AVAILABLE:
            self._load_or_create_model()
        else:
            print("TensorFlow not available. Using simple prediction fallback.")
    
    # ----------------------------------------------------------------
    #  REAL DATA LOADING (Alibaba Cluster Trace 2018)
    # ----------------------------------------------------------------
    def _load_real_data(self, max_machines=200, max_rows=500000):
        """
        Load real production data from the Alibaba machine_usage.csv.
        Samples a subset of machines to keep memory manageable.
        Returns X (sequences) and y (next-step CPU target) arrays.
        """
        if not os.path.exists(DATASET_FILE):
            print(f"[WARNING] Dataset not found at {DATASET_FILE}")
            print("          Falling back to synthetic training data.")
            print("          Place machine_usage.csv in backend/data/ for real training.")
            return self._generate_synthetic_fallback()

        print(f"[INFO] Loading real Alibaba dataset from {DATASET_FILE}...")
        
        # Read CSV in chunks to handle large files
        # The raw file has no header
        chunks = []
        rows_read = 0
        for chunk in pd.read_csv(
            DATASET_FILE,
            header=None,
            names=COLUMN_NAMES,
            chunksize=100000,
            on_bad_lines='skip'
        ):
            chunks.append(chunk)
            rows_read += len(chunk)
            if rows_read >= max_rows:
                break
        
        df = pd.concat(chunks, ignore_index=True)
        print(f"[INFO] Loaded {len(df):,} rows from dataset.")

        # Sample a subset of machines
        unique_machines = df["machine_id"].unique()
        if len(unique_machines) > max_machines:
            sampled_machines = np.random.choice(unique_machines, max_machines, replace=False)
            df = df[df["machine_id"].isin(sampled_machines)]
            print(f"[INFO] Sampled {max_machines} machines ({len(df):,} rows).")

        # Clean data: replace empty/invalid values with NaN, then drop
        for col in FEATURE_COLS:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.dropna(subset=FEATURE_COLS)
        
        # Clamp values to valid ranges
        df["cpu_util_percent"] = df["cpu_util_percent"].clip(0, 100)
        df["mem_util_percent"] = df["mem_util_percent"].clip(0, 100)
        df["disk_io_percent"] = df["disk_io_percent"].clip(0, 100)
        df["net_in"] = df["net_in"].clip(0, None)  # Network can't be negative

        print(f"[INFO] After cleaning: {len(df):,} valid rows.")

        # Build training sequences per machine
        X, y = [], []
        
        for machine_id, group in df.groupby("machine_id"):
            group = group.sort_values("time_stamp")
            
            # Extract the 4 feature columns as numpy array
            values = group[FEATURE_COLS].values  # shape: (timesteps, 4)
            
            if len(values) < self.sequence_length + 1:
                continue  # Skip machines without enough data
            
            # Create sliding window sequences
            for i in range(len(values) - self.sequence_length):
                seq = values[i:i + self.sequence_length]      # (seq_len, 4)
                target = values[i + self.sequence_length, 0]  # Predict next CPU%
                X.append(seq)
                y.append(target)

        X = np.array(X, dtype=np.float32)
        y = np.array(y, dtype=np.float32)
        
        print(f"[INFO] Built {len(X):,} training sequences (shape: {X.shape}).")
        return X, y

    # ----------------------------------------------------------------
    #  SYNTHETIC FALLBACK (used only when dataset is missing)
    # ----------------------------------------------------------------
    def _generate_synthetic_fallback(self, n_samples=1000):
        """Fallback to synthetic data if real dataset is not available."""
        print("[INFO] Generating synthetic training data as fallback...")
        X, y = [], []
        
        for _ in range(n_samples):
            pattern_type = np.random.choice(['trend', 'seasonal', 'spike', 'stable'])
            
            if pattern_type == 'trend':
                cpu = np.linspace(40, 85, self.sequence_length) + np.random.normal(0, 5, self.sequence_length)
                target = 90 + np.random.normal(0, 3)
            elif pattern_type == 'seasonal':
                cpu = 60 + 20 * np.sin(np.linspace(0, 4*np.pi, self.sequence_length)) + np.random.normal(0, 5, self.sequence_length)
                target = 60 + 20 * np.sin(4*np.pi + 0.5) + np.random.normal(0, 3)
            elif pattern_type == 'spike':
                cpu = np.full(self.sequence_length, 50) + np.random.normal(0, 5, self.sequence_length)
                cpu[-3:] = cpu[-3:] + 30
                target = 85 + np.random.normal(0, 3)
            else:
                base = np.random.uniform(45, 65)
                cpu = np.full(self.sequence_length, base) + np.random.normal(0, 5, self.sequence_length)
                target = base + np.random.normal(0, 3)
            
            cpu = np.clip(cpu, 10, 95)
            target = np.clip(target, 10, 95)
            
            # Build 4-feature vectors (simulate mem/net/disk alongside CPU)
            mem = cpu * 0.8 + np.random.normal(0, 3, self.sequence_length)
            net = cpu * 0.5 + np.random.normal(0, 2, self.sequence_length)
            disk = np.random.uniform(2, 15, self.sequence_length)
            
            seq = np.stack([cpu, mem, net, disk], axis=-1)  # (seq_len, 4)
            X.append(seq)
            y.append(target)
        
        X = np.array(X, dtype=np.float32)
        y = np.array(y, dtype=np.float32)
        return X, y

    # ----------------------------------------------------------------
    #  MODEL ARCHITECTURE
    # ----------------------------------------------------------------
    def _build_model(self, input_shape):
        """Build multivariate LSTM model — now accepts 4 input features."""
        if not TENSORFLOW_AVAILABLE:
            return None
        model = Sequential([
            LSTM(64, activation='relu', return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(32, activation='relu', return_sequences=False),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)  # Predict next CPU utilization
        ])
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model
    
    # ----------------------------------------------------------------
    #  TRAINING
    # ----------------------------------------------------------------
    def train(self):
        """Train a new LSTM model from data and save it to disk."""
        if not TENSORFLOW_AVAILABLE:
            print("[ERROR] TensorFlow is not available. Install dependencies with:")
            print("          pip install -r requirements.txt")
            return False

        print("=" * 60)
        print("  LSTM MODEL TRAINING")
        print("=" * 60)

        X, y = self._load_real_data()

        if len(X) == 0:
            print("[ERROR] No training data available. Skipping training.")
            return False

        self.model = self._build_model((self.sequence_length, len(FEATURE_COLS)))
        if self.model is None:
            print("[ERROR] Failed to build LSTM model.")
            return False

        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )

        split_idx = int(0.8 * len(X))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]

        print(f"[INFO] Training set: {len(X_train):,} | Validation set: {len(X_val):,}")

        self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=50,
            batch_size=32,
            verbose=1,
            callbacks=[early_stopping]
        )

        self.model.save(self.model_path)
        print(f"[INFO] Model saved to {self.model_path}")
        print("=" * 60)
        return True
    
    # ----------------------------------------------------------------
    #  LOAD OR CREATE
    # ----------------------------------------------------------------
    def _load_or_create_model(self):
        """Load existing model or fall back to simple predictions."""
        if not TENSORFLOW_AVAILABLE:
            return
        if os.path.exists(self.model_path):
            try:
                self.model = load_model(self.model_path)
                print(f"[INFO] Loaded existing model from {self.model_path}")
            except Exception as e:
                print(f"[WARNING] Error loading model: {e}. Using fallback predictor.")
                self.model = None
        else:
            print("[INFO] No trained model found. Using fallback predictor.")
            print("[INFO] Run 'python train_model.py' to train the LSTM model.")
    
    # ----------------------------------------------------------------
    #  PREDICTION (accepts single-metric list for backward compat)
    # ----------------------------------------------------------------
    def predict(self, cpu_data, mem_data=None, net_data=None, disk_data=None):
        """
        Predict future CPU utilization.
        Accepts just CPU data (backward compatible) or all 4 features.
        """
        if not TENSORFLOW_AVAILABLE or self.model is None:
            # Fallback: simple moving average with trend
            if len(cpu_data) < 2:
                return 60.0
            recent = cpu_data[-5:] if len(cpu_data) >= 5 else cpu_data
            avg = np.mean(recent)
            trend = (cpu_data[-1] - cpu_data[0]) / len(cpu_data) if len(cpu_data) > 1 else 0
            prediction = avg + trend * 2
            return float(np.clip(prediction, 10, 95))
        
        # Build multivariate input
        n = len(cpu_data)
        if mem_data is None:
            mem_data = [50.0] * n  # Default placeholder
        if net_data is None:
            net_data = [30.0] * n
        if disk_data is None:
            disk_data = [5.0] * n
        
        # Ensure all lists are same length
        min_len = min(len(cpu_data), len(mem_data), len(net_data), len(disk_data))
        
        features = np.column_stack([
            cpu_data[-min_len:],
            mem_data[-min_len:],
            net_data[-min_len:],
            disk_data[-min_len:]
        ])
        
        if len(features) < self.sequence_length:
            # Pad with mean values
            pad_len = self.sequence_length - len(features)
            pad = np.tile(features.mean(axis=0), (pad_len, 1))
            features = np.vstack([pad, features])
        
        X = features[-self.sequence_length:].reshape(1, self.sequence_length, len(FEATURE_COLS))
        X = X.astype(np.float32)
        prediction = self.model.predict(X, verbose=0)[0][0]
        return float(np.clip(prediction, 10, 95))
    
    def predict_multiple(self, cpu_data, n_steps=5):
        """Predict multiple future steps."""
        predictions = []
        current_cpu = list(cpu_data[-self.sequence_length:])
        
        for _ in range(n_steps):
            pred = self.predict(current_cpu)
            predictions.append(pred)
            current_cpu = current_cpu[1:] + [pred]
        
        return predictions
    
    def get_prediction_confidence(self, cpu_data):
        """Estimate prediction confidence based on data variance."""
        if not TENSORFLOW_AVAILABLE:
            return 0.6
        
        if len(cpu_data) < 2:
            return 0.5
        
        variance = np.var(cpu_data)
        confidence = max(0.3, min(0.95, 1.0 - (variance / 1000)))
        return confidence
