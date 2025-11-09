import numpy as np
import os
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from config import settings

class LSTMModel:
    def __init__(self):
        self.model = None
        self.model_path = os.path.join(settings.model_dir, "lstm_model.h5")
        self.sequence_length = settings.sequence_length
        os.makedirs(settings.model_dir, exist_ok=True)
        self._load_or_create_model()
    
    def _build_model(self, input_shape):
        """Build LSTM model with improved architecture"""
        model = Sequential([
            LSTM(64, activation='relu', return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(32, activation='relu', return_sequences=False),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model
    
    def _generate_training_data(self, n_samples=500):
        """Generate more realistic training data with patterns"""
        X, y = [], []
        
        for _ in range(n_samples):
            # Generate sequences with different patterns
            pattern_type = np.random.choice(['trend', 'seasonal', 'spike', 'stable'])
            
            if pattern_type == 'trend':
                seq = np.linspace(40, 85, self.sequence_length) + np.random.normal(0, 5, self.sequence_length)
                target = 90 + np.random.normal(0, 3)
            elif pattern_type == 'seasonal':
                seq = 60 + 20 * np.sin(np.linspace(0, 4*np.pi, self.sequence_length)) + np.random.normal(0, 5, self.sequence_length)
                target = 60 + 20 * np.sin(4*np.pi + 0.5) + np.random.normal(0, 3)
            elif pattern_type == 'spike':
                seq = np.full(self.sequence_length, 50) + np.random.normal(0, 5, self.sequence_length)
                seq[-3:] = seq[-3:] + 30  # Spike at the end
                target = 85 + np.random.normal(0, 3)
            else:  # stable
                base = np.random.uniform(45, 65)
                seq = np.full(self.sequence_length, base) + np.random.normal(0, 5, self.sequence_length)
                target = base + np.random.normal(0, 3)
            
            # Clamp values
            seq = np.clip(seq, 10, 95)
            target = np.clip(target, 10, 95)
            
            X.append(seq)
            y.append(target)
        
        X = np.array(X).reshape((len(X), self.sequence_length, 1))
        y = np.array(y)
        return X, y
    
    def _train(self):
        """Train the model with better data"""
        print("Training LSTM model...")
        X, y = self._generate_training_data(1000)
        
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Split data
        split_idx = int(0.8 * len(X))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=50,
            batch_size=32,
            verbose=1,
            callbacks=[early_stopping]
        )
        
        # Save model
        self.model.save(self.model_path)
        print(f"Model saved to {self.model_path}")
        
        return history
    
    def _load_or_create_model(self):
        """Load existing model or create and train new one"""
        if os.path.exists(self.model_path):
            try:
                self.model = load_model(self.model_path)
                print(f"Loaded existing model from {self.model_path}")
            except Exception as e:
                print(f"Error loading model: {e}. Creating new model...")
                self.model = self._build_model((self.sequence_length, 1))
                self._train()
        else:
            print("No existing model found. Creating new model...")
            self.model = self._build_model((self.sequence_length, 1))
            self._train()
    
    def predict(self, cpu_data):
        """Predict future CPU utilization"""
        if len(cpu_data) < self.sequence_length:
            # Pad with average if not enough data
            avg = np.mean(cpu_data)
            cpu_data = [avg] * (self.sequence_length - len(cpu_data)) + cpu_data
        
        X = np.array(cpu_data[-self.sequence_length:]).reshape((1, self.sequence_length, 1))
        prediction = self.model.predict(X, verbose=0)[0][0]
        return float(np.clip(prediction, 10, 95))
    
    def predict_multiple(self, cpu_data, n_steps=5):
        """Predict multiple future steps"""
        predictions = []
        current_seq = cpu_data[-self.sequence_length:]
        
        for _ in range(n_steps):
            pred = self.predict(current_seq)
            predictions.append(pred)
            current_seq = current_seq[1:] + [pred]
        
        return predictions
    
    def get_prediction_confidence(self, cpu_data):
        """Estimate prediction confidence based on data variance"""
        if len(cpu_data) < 2:
            return 0.5
        
        variance = np.var(cpu_data)
        # Lower variance = higher confidence
        confidence = max(0.3, min(0.95, 1.0 - (variance / 1000)))
        return confidence
