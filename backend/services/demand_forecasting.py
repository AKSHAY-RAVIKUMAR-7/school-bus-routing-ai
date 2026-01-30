"""
Deep Learning Model for Student Demand Forecasting

Uses LSTM/GRU neural networks to predict student ridership
based on historical data, weather, calendar events, etc.
"""
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logger.warning("TensorFlow not available, using fallback predictor")

class LSTMDemandPredictor:
    """
    LSTM-based demand forecasting model
    """
    
    def __init__(self, sequence_length: int = 30, features: int = 10):
        self.sequence_length = sequence_length
        self.features = features
        self.model = None
        self.is_trained = False
        
        if TENSORFLOW_AVAILABLE:
            self._build_model()
    
    def _build_model(self):
        """Build LSTM neural network"""
        model = keras.Sequential([
            layers.LSTM(64, return_sequences=True, 
                       input_shape=(self.sequence_length, self.features)),
            layers.Dropout(0.2),
            layers.LSTM(32, return_sequences=False),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(1, activation='linear')  # Predict student count
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae', 'mape']
        )
        
        self.model = model
        logger.info("LSTM model built successfully")
    
    def prepare_features(self, data: List[Dict]) -> np.ndarray:
        """
        Prepare features for the model
        
        Features:
        - Day of week (0-6)
        - Month (1-12)
        - Is holiday (0/1)
        - Weather condition (encoded)
        - Temperature
        - Historical average
        - Trend component
        - Day of month
        - Week of year
        - Is weekend (0/1)
        """
        features = []
        
        for record in data:
            date = datetime.fromisoformat(record['date'])
            
            feature_vector = [
                date.weekday() / 6.0,  # Normalize
                date.month / 12.0,
                float(record.get('is_holiday', 0)),
                self._encode_weather(record.get('weather', 'clear')),
                record.get('temperature', 20) / 40.0,  # Normalize temp
                record.get('historical_avg', 0) / 50.0,  # Normalize student count
                record.get('trend', 0),
                date.day / 31.0,
                date.isocalendar()[1] / 52.0,
                float(date.weekday() >= 5)  # Weekend
            ]
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def _encode_weather(self, weather: str) -> float:
        """Encode weather conditions"""
        weather_map = {
            'clear': 0.0,
            'cloudy': 0.3,
            'rain': 0.6,
            'heavy_rain': 0.8,
            'snow': 1.0
        }
        return weather_map.get(weather.lower(), 0.0)
    
    def train(self, historical_data: List[Dict], epochs: int = 50, 
             batch_size: int = 32):
        """
        Train the LSTM model
        
        Args:
            historical_data: List of historical records with features and targets
            epochs: Number of training epochs
            batch_size: Training batch size
        """
        if not TENSORFLOW_AVAILABLE:
            logger.warning("TensorFlow not available, skipping training")
            return
        
        logger.info(f"Training LSTM model with {len(historical_data)} samples")
        
        # Prepare sequences
        X, y = self._create_sequences(historical_data)
        
        # Split train/validation
        split = int(0.8 * len(X))
        X_train, X_val = X[:split], X[split:]
        y_train, y_val = y[:split], y[split:]
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            verbose=1,
            callbacks=[
                keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
                keras.callbacks.ReduceLROnPlateau(patience=5, factor=0.5)
            ]
        )
        
        self.is_trained = True
        logger.info("LSTM model training completed")
        
        return history
    
    def _create_sequences(self, data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training"""
        features = self.prepare_features(data)
        targets = np.array([d['student_count'] for d in data])
        
        X, y = [], []
        for i in range(len(features) - self.sequence_length):
            X.append(features[i:i + self.sequence_length])
            y.append(targets[i + self.sequence_length])
        
        return np.array(X), np.array(y)
    
    def predict(self, recent_data: List[Dict]) -> float:
        """
        Predict student demand
        
        Args:
            recent_data: Recent historical data (last sequence_length days)
        
        Returns:
            Predicted student count
        """
        if not TENSORFLOW_AVAILABLE or not self.is_trained:
            # Fallback: simple average
            return np.mean([d['student_count'] for d in recent_data[-7:]])
        
        # Prepare input sequence
        features = self.prepare_features(recent_data[-self.sequence_length:])
        X = np.expand_dims(features, axis=0)
        
        # Predict
        prediction = self.model.predict(X, verbose=0)[0][0]
        
        return max(0, int(prediction))

class DemandForecaster:
    """
    Main demand forecasting service
    """
    
    def __init__(self):
        self.models = {}  # One model per stop
        self.fallback_enabled = True
    
    def predict_for_stop(self, stop_id: int, days_ahead: int = 7) -> List[Dict]:
        """
        Predict demand for a specific stop
        
        Args:
            stop_id: Stop ID to predict
            days_ahead: Number of days to forecast
        
        Returns:
            List of predictions with dates
        """
        logger.info(f"Generating {days_ahead}-day forecast for stop {stop_id}")
        
        # Get or create model for this stop
        if stop_id not in self.models:
            self.models[stop_id] = LSTMDemandPredictor()
        
        model = self.models[stop_id]
        
        # Get historical data (would fetch from database in production)
        historical_data = self._get_historical_data(stop_id)
        
        # Train if not trained
        if not model.is_trained and TENSORFLOW_AVAILABLE:
            if len(historical_data) >= model.sequence_length:
                model.train(historical_data)
        
        # Generate predictions
        predictions = []
        current_date = datetime.now()
        
        for day in range(1, days_ahead + 1):
            forecast_date = current_date + timedelta(days=day)
            
            # Prepare features for prediction
            recent_data = historical_data[-model.sequence_length:]
            
            # Add synthetic future data point
            future_record = {
                'date': forecast_date.isoformat(),
                'is_holiday': self._is_holiday(forecast_date),
                'weather': 'clear',  # Would use weather API in production
                'temperature': 22,
                'historical_avg': np.mean([d['student_count'] for d in recent_data]),
                'trend': 0,
                'student_count': 0  # Placeholder
            }
            
            recent_data_with_future = recent_data + [future_record]
            
            # Predict
            prediction = model.predict(recent_data_with_future)
            
            predictions.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'predicted_count': int(prediction),
                'confidence': 0.85 if model.is_trained else 0.60,
                'day_of_week': forecast_date.strftime('%A')
            })
            
            # Add prediction to historical for next iteration
            future_record['student_count'] = prediction
            historical_data.append(future_record)
        
        return predictions
    
    def predict_all_stops(self, days_ahead: int = 7) -> Dict[int, List[Dict]]:
        """Predict demand for all stops"""
        # In production, would get all stop IDs from database
        stop_ids = [1, 2, 3, 4, 5]  # Placeholder
        
        all_predictions = {}
        for stop_id in stop_ids:
            all_predictions[stop_id] = self.predict_for_stop(stop_id, days_ahead)
        
        return all_predictions
    
    def _get_historical_data(self, stop_id: int) -> List[Dict]:
        """
        Get historical ridership data
        In production, fetch from database
        """
        # Generate synthetic historical data
        historical = []
        base_count = 25
        
        for days_ago in range(90, 0, -1):
            date = datetime.now() - timedelta(days=days_ago)
            
            # Add weekly pattern
            day_of_week = date.weekday()
            weekend_factor = 0 if day_of_week >= 5 else 1
            
            # Add some randomness
            count = int(base_count * weekend_factor + np.random.normal(0, 3))
            count = max(0, count)
            
            historical.append({
                'date': date.isoformat(),
                'student_count': count,
                'is_holiday': self._is_holiday(date),
                'weather': 'clear',
                'temperature': 20 + np.random.normal(0, 5),
                'historical_avg': base_count,
                'trend': 0
            })
        
        return historical
    
    def _is_holiday(self, date: datetime) -> bool:
        """Check if date is a holiday (simplified)"""
        # Would use a proper holiday calendar in production
        return date.weekday() >= 5  # Weekend
