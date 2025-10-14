#!/usr/bin/env python3
"""
TrafficPredictor - LSTM/GRU-based Network Traffic Prediction System

Implements advanced time-series forecasting for network traffic patterns using
deep learning models with multi-timeframe analysis and adaptive learning.
"""

import asyncio
import logging
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import deque

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error

from ..utils.config import Config
from ..data.storage import TimeSeriesStorage

logger = logging.getLogger(__name__)

@dataclass
class TrafficFeatures:
    """Network traffic features for ML processing"""
    timestamp: datetime
    bandwidth_usage: float
    connection_count: int
    packet_rate: float
    bytes_per_second: float
    latency: float
    jitter: float
    packet_loss: float
    application_mix: Dict[str, float]
    time_features: Dict[str, float]
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array for ML processing"""
        features = [
            self.bandwidth_usage,
            self.connection_count,
            self.packet_rate,
            self.bytes_per_second,
            self.latency,
            self.jitter,
            self.packet_loss,
        ]
        
        # Add application mix features (top 5 applications)
        app_features = list(self.application_mix.values())[:5]
        features.extend(app_features + [0.0] * (5 - len(app_features)))
        
        # Add time features
        features.extend([
            self.time_features.get('hour_sin', 0.0),
            self.time_features.get('hour_cos', 0.0),
            self.time_features.get('day_sin', 0.0),
            self.time_features.get('day_cos', 0.0),
            self.time_features.get('weekday', 0.0),
        ])
        
        return np.array(features, dtype=np.float32)

class TrafficFeatureEngineer:
    """Feature engineering for network traffic data"""
    
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.is_fitted = False
        
    async def process(self, raw_metrics: Dict[str, Any]) -> TrafficFeatures:
        """Process raw network metrics into ML features"""
        timestamp = raw_metrics.get('timestamp', datetime.utcnow())
        
        # Extract basic traffic metrics
        bandwidth_usage = raw_metrics.get('bandwidth_usage', {}).get('total', 0.0)
        connection_count = len(raw_metrics.get('connections', []))
        packet_rate = raw_metrics.get('packet_rate', 0.0)
        bytes_per_second = raw_metrics.get('bytes_per_second', 0.0)
        
        # Quality metrics
        latency = raw_metrics.get('latency_metrics', {}).get('avg', 0.0)
        jitter = raw_metrics.get('jitter', 0.0)
        packet_loss = raw_metrics.get('packet_loss', 0.0)
        
        # Application mix analysis
        applications = raw_metrics.get('active_applications', [])
        app_mix = self._analyze_application_mix(applications)
        
        # Time-based features
        time_features = self._extract_time_features(timestamp)
        
        return TrafficFeatures(
            timestamp=timestamp,
            bandwidth_usage=bandwidth_usage,
            connection_count=connection_count,
            packet_rate=packet_rate,
            bytes_per_second=bytes_per_second,
            latency=latency,
            jitter=jitter,
            packet_loss=packet_loss,
            application_mix=app_mix,
            time_features=time_features
        )
    
    def _analyze_application_mix(self, applications: List[str]) -> Dict[str, float]:
        """Analyze application distribution"""
        if not applications:
            return {}
        
        # Count application occurrences
        app_counts = {}
        for app in applications:
            app_counts[app] = app_counts.get(app, 0) + 1
        
        # Convert to proportions
        total = len(applications)
        app_mix = {app: count / total for app, count in app_counts.items()}
        
        # Sort by usage and take top 5
        sorted_apps = sorted(app_mix.items(), key=lambda x: x[1], reverse=True)[:5]
        return dict(sorted_apps)
    
    def _extract_time_features(self, timestamp: datetime) -> Dict[str, float]:
        """Extract cyclical time features"""
        hour = timestamp.hour
        day_of_year = timestamp.timetuple().tm_yday
        weekday = timestamp.weekday()
        
        return {
            'hour_sin': np.sin(2 * np.pi * hour / 24),
            'hour_cos': np.cos(2 * np.pi * hour / 24),
            'day_sin': np.sin(2 * np.pi * day_of_year / 365),
            'day_cos': np.cos(2 * np.pi * day_of_year / 365),
            'weekday': weekday / 7.0,
        }
    
    def fit_scaler(self, features: List[TrafficFeatures]):
        """Fit the feature scaler"""
        feature_arrays = [f.to_array() for f in features]
        if feature_arrays:
            self.scaler.fit(np.vstack(feature_arrays))
            self.is_fitted = True
    
    def transform_features(self, features: TrafficFeatures) -> np.ndarray:
        """Transform features using fitted scaler"""
        if not self.is_fitted:
            return features.to_array()
        
        return self.scaler.transform(features.to_array().reshape(1, -1)).flatten()

class TrafficDataset(Dataset):
    """PyTorch dataset for traffic prediction"""
    
    def __init__(self, sequences: np.ndarray, targets: np.ndarray):
        self.sequences = torch.FloatTensor(sequences)
        self.targets = torch.FloatTensor(targets)
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        return self.sequences[idx], self.targets[idx]

class LSTMTrafficPredictor(nn.Module):
    """LSTM model for traffic prediction"""
    
    def __init__(self, input_dim: int, hidden_dim: int = 128, num_layers: int = 2, 
                 output_dim: int = 1, dropout: float = 0.2):
        super().__init__()
        
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_dim, hidden_dim, num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        # Output layers
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc2 = nn.Linear(hidden_dim // 2, output_dim)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        # LSTM forward pass
        lstm_out, _ = self.lstm(x)
        
        # Take the last output for prediction
        last_output = lstm_out[:, -1, :]
        
        # Dense layers
        out = self.dropout(last_output)
        out = self.relu(self.fc1(out))
        out = self.dropout(out)
        out = self.fc2(out)
        
        return out

class GRUTrafficPredictor(nn.Module):
    """GRU model for traffic prediction"""
    
    def __init__(self, input_dim: int, hidden_dim: int = 128, num_layers: int = 2,
                 output_dim: int = 1, dropout: float = 0.2):
        super().__init__()
        
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # GRU layers
        self.gru = nn.GRU(
            input_dim, hidden_dim, num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        # Output layers
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc2 = nn.Linear(hidden_dim // 2, output_dim)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        # GRU forward pass
        gru_out, _ = self.gru(x)
        
        # Take the last output for prediction
        last_output = gru_out[:, -1, :]
        
        # Dense layers
        out = self.dropout(last_output)
        out = self.relu(self.fc1(out))
        out = self.dropout(out)
        out = self.fc2(out)
        
        return out

class TrafficPredictor:
    """Main traffic prediction system with multi-timeframe analysis"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Model configurations
        self.models = {}
        self.model_configs = {
            'lstm_1min': {'sequence_length': 60, 'model_type': 'lstm'},
            'gru_15min': {'sequence_length': 96, 'model_type': 'gru'},  # 24 hours of 15-min data
            'lstm_1hour': {'sequence_length': 168, 'model_type': 'lstm'},  # 1 week of hourly data
        }
        
        # Feature engineering
        self.feature_engineer = TrafficFeatureEngineer()
        
        # Data storage
        self.storage = TimeSeriesStorage(config)
        self.feature_buffer = deque(maxlen=10000)  # Keep recent features in memory
        
        # Training parameters
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.retrain_threshold = 0.1  # Retrain if error exceeds 10%
        self.min_samples_for_training = 1000
        
    async def initialize(self):
        """Initialize the traffic predictor"""
        self.logger.info("Initializing TrafficPredictor...")
        
        try:
            # Initialize storage
            await self.storage.initialize()
            
            # Load existing models or create new ones
            await self._load_or_create_models()
            
            # Load recent training data for feature scaling
            await self._initialize_feature_scaling()
            
            self.logger.info("TrafficPredictor initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize TrafficPredictor: {e}")
            raise
    
    async def _load_or_create_models(self):
        """Load existing models or create new ones"""
        models_dir = Path(self.config.get('models_dir', 'ml_models/traffic_prediction'))
        models_dir.mkdir(parents=True, exist_ok=True)
        
        for model_name, model_config in self.model_configs.items():
            model_path = models_dir / f"{model_name}.pth"
            
            if model_path.exists():
                try:
                    # Load existing model
                    self.models[model_name] = torch.load(model_path, map_location=self.device)
                    self.logger.info(f"Loaded model: {model_name}")
                except Exception as e:
                    self.logger.error(f"Failed to load model {model_name}: {e}")
                    self.models[model_name] = self._create_model(model_config)
            else:
                # Create new model
                self.models[model_name] = self._create_model(model_config)
                self.logger.info(f"Created new model: {model_name}")
    
    def _create_model(self, model_config: Dict) -> nn.Module:
        """Create a new prediction model"""
        input_dim = 17  # Based on TrafficFeatures.to_array() output
        
        if model_config['model_type'] == 'lstm':
            model = LSTMTrafficPredictor(input_dim)
        elif model_config['model_type'] == 'gru':
            model = GRUTrafficPredictor(input_dim)
        else:
            raise ValueError(f"Unknown model type: {model_config['model_type']}")
        
        return model.to(self.device)
    
    async def _initialize_feature_scaling(self):
        """Initialize feature scaling from historical data"""
        try:
            # Load recent data for feature scaling
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)  # Last week
            
            historical_data = await self.storage.get_data_range(start_time, end_time)
            
            if len(historical_data) > 100:
                # Convert to features and fit scaler
                features = []
                for data_point in historical_data:
                    feature = await self.feature_engineer.process(data_point)
                    features.append(feature)
                
                self.feature_engineer.fit_scaler(features)
                self.logger.info(f"Fitted feature scaler with {len(features)} samples")
            else:
                self.logger.warning("Not enough historical data for feature scaling")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize feature scaling: {e}")
    
    async def predict(self, current_metrics: Any, horizons: List[int] = None) -> Dict[str, Any]:
        """Multi-horizon traffic prediction"""
        if horizons is None:
            horizons = [1, 15, 60]  # 1 minute, 15 minutes, 1 hour
        
        try:
            # Process current metrics into features
            features = await self.feature_engineer.process(current_metrics.__dict__ if hasattr(current_metrics, '__dict__') else current_metrics)
            
            # Add to feature buffer
            self.feature_buffer.append(features)
            
            predictions = {}
            
            for horizon in horizons:
                model_name = self._select_model_for_horizon(horizon)
                if model_name in self.models:
                    prediction = await self._predict_with_model(model_name, features, horizon)
                    predictions[f'{horizon}min'] = prediction
                else:
                    # Fallback to simple prediction
                    predictions[f'{horizon}min'] = self._simple_prediction(features, horizon)
            
            return {
                'predictions': predictions,
                'timestamp': datetime.utcnow().isoformat(),
                'confidence': self._calculate_confidence(predictions),
                'features_used': len(self.feature_buffer)
            }
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            return {
                'predictions': {},
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _select_model_for_horizon(self, horizon: int) -> str:
        """Select appropriate model based on prediction horizon"""
        if horizon <= 5:
            return 'lstm_1min'
        elif horizon <= 30:
            return 'gru_15min'
        else:
            return 'lstm_1hour'
    
    async def _predict_with_model(self, model_name: str, features: TrafficFeatures, horizon: int) -> Dict[str, float]:
        """Make prediction using specified model"""
        try:
            model = self.models[model_name]
            model.eval()
            
            # Prepare sequence data
            sequence = self._prepare_sequence(model_name, features)
            if sequence is None:
                return self._simple_prediction(features, horizon)
            
            with torch.no_grad():
                sequence_tensor = torch.FloatTensor(sequence).unsqueeze(0).to(self.device)
                prediction = model(sequence_tensor)
                predicted_value = prediction.cpu().numpy().flatten()[0]
            
            return {
                'predicted_bandwidth': max(0.0, float(predicted_value)),
                'confidence': 0.8,  # Model-based confidence
                'model_used': model_name
            }
            
        except Exception as e:
            self.logger.error(f"Model prediction failed: {e}")
            return self._simple_prediction(features, horizon)
    
    def _prepare_sequence(self, model_name: str, current_features: TrafficFeatures) -> Optional[np.ndarray]:
        """Prepare sequence data for model input"""
        config = self.model_configs[model_name]
        sequence_length = config['sequence_length']
        
        if len(self.feature_buffer) < sequence_length:
            return None
        
        # Get recent features and transform them
        recent_features = list(self.feature_buffer)[-sequence_length:]
        
        # Convert to arrays and normalize
        sequence = []
        for features in recent_features:
            transformed = self.feature_engineer.transform_features(features)
            sequence.append(transformed)
        
        return np.array(sequence)
    
    def _simple_prediction(self, features: TrafficFeatures, horizon: int) -> Dict[str, float]:
        """Simple fallback prediction when models aren't available"""
        # Use current bandwidth with time-based adjustments
        current_bw = features.bandwidth_usage
        
        # Simple time-based scaling
        time_factor = 1.0
        hour = features.timestamp.hour
        
        # Peak hours (typically 8-10 AM and 7-11 PM)
        if 8 <= hour <= 10 or 19 <= hour <= 23:
            time_factor = 1.2
        elif 0 <= hour <= 6:
            time_factor = 0.6
        
        predicted_bw = current_bw * time_factor * (1.0 + np.random.normal(0, 0.1))
        
        return {
            'predicted_bandwidth': max(0.0, predicted_bw),
            'confidence': 0.3,  # Low confidence for simple prediction
            'model_used': 'simple_fallback'
        }
    
    def _calculate_confidence(self, predictions: Dict[str, Any]) -> float:
        """Calculate overall confidence in predictions"""
        if not predictions:
            return 0.0
        
        confidences = [p.get('confidence', 0.0) for p in predictions.values()]
        return np.mean(confidences)
    
    async def adaptive_learning(self, actual_traffic: Dict[str, Any]):
        """Continuous learning from actual vs predicted traffic"""
        try:
            # Store actual traffic data
            await self.storage.store_data(actual_traffic)
            
            # Check if retraining is needed
            if await self._should_retrain():
                await self._retrain_models()
            
        except Exception as e:
            self.logger.error(f"Adaptive learning failed: {e}")
    
    async def _should_retrain(self) -> bool:
        """Determine if models need retraining"""
        # Simple heuristic: retrain every 24 hours or if error is high
        # In production, this would be more sophisticated
        return len(self.feature_buffer) % 1440 == 0  # Every 24 hours (if 1-min intervals)
    
    async def _retrain_models(self):
        """Retrain models with recent data"""
        self.logger.info("Starting model retraining...")
        
        try:
            # Get training data
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=30)  # Last 30 days
            
            training_data = await self.storage.get_data_range(start_time, end_time)
            
            if len(training_data) < self.min_samples_for_training:
                self.logger.warning(f"Not enough training data: {len(training_data)}")
                return
            
            # Process data into features
            features = []
            for data_point in training_data:
                feature = await self.feature_engineer.process(data_point)
                features.append(feature)
            
            # Retrain each model
            for model_name in self.models.keys():
                await self._retrain_single_model(model_name, features)
            
            # Save updated models
            await self._save_models()
            
            self.logger.info("Model retraining completed")
            
        except Exception as e:
            self.logger.error(f"Model retraining failed: {e}")
    
    async def _retrain_single_model(self, model_name: str, features: List[TrafficFeatures]):
        """Retrain a single model"""
        try:
            config = self.model_configs[model_name]
            sequence_length = config['sequence_length']
            
            # Prepare training sequences
            sequences, targets = self._prepare_training_data(features, sequence_length)
            
            if len(sequences) < 100:  # Need minimum samples
                self.logger.warning(f"Not enough sequences for {model_name}: {len(sequences)}")
                return
            
            # Create data loader
            dataset = TrafficDataset(sequences, targets)
            dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
            
            # Training setup
            model = self.models[model_name]
            model.train()
            
            optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
            criterion = nn.MSELoss()
            
            # Training loop (simplified)
            for epoch in range(10):  # Quick retraining
                total_loss = 0
                for batch_sequences, batch_targets in dataloader:
                    batch_sequences = batch_sequences.to(self.device)
                    batch_targets = batch_targets.to(self.device)
                    
                    optimizer.zero_grad()
                    outputs = model(batch_sequences)
                    loss = criterion(outputs, batch_targets)
                    loss.backward()
                    optimizer.step()
                    
                    total_loss += loss.item()
                
                if epoch % 2 == 0:
                    avg_loss = total_loss / len(dataloader)
                    self.logger.debug(f"{model_name} epoch {epoch}, loss: {avg_loss:.4f}")
            
            model.eval()
            self.logger.info(f"Retrained model: {model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to retrain {model_name}: {e}")
    
    def _prepare_training_data(self, features: List[TrafficFeatures], 
                             sequence_length: int) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training sequences and targets"""
        sequences = []
        targets = []
        
        # Transform all features
        transformed_features = [self.feature_engineer.transform_features(f) for f in features]
        
        # Create sequences
        for i in range(sequence_length, len(transformed_features)):
            sequence = transformed_features[i-sequence_length:i]
            target = transformed_features[i][0]  # Predict bandwidth (first feature)
            
            sequences.append(sequence)
            targets.append([target])
        
        return np.array(sequences), np.array(targets)
    
    async def _save_models(self):
        """Save all models to disk"""
        models_dir = Path(self.config.get('models_dir', 'ml_models/traffic_prediction'))
        
        for model_name, model in self.models.items():
            model_path = models_dir / f"{model_name}.pth"
            torch.save(model, model_path)
            self.logger.debug(f"Saved model: {model_name}")
    
    async def get_current_patterns(self) -> Dict[str, Any]:
        """Get current traffic patterns analysis"""
        if len(self.feature_buffer) < 60:  # Need at least 1 hour of data
            return {'error': 'Insufficient data for pattern analysis'}
        
        recent_features = list(self.feature_buffer)[-60:]  # Last hour
        
        patterns = {
            'avg_bandwidth': np.mean([f.bandwidth_usage for f in recent_features]),
            'bandwidth_trend': self._calculate_trend([f.bandwidth_usage for f in recent_features]),
            'peak_connections': max([f.connection_count for f in recent_features]),
            'avg_latency': np.mean([f.latency for f in recent_features]),
            'quality_score': self._calculate_quality_score(recent_features),
            'dominant_applications': self._get_dominant_applications(recent_features),
        }
        
        return patterns
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'stable'
        
        # Simple linear trend
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_quality_score(self, features: List[TrafficFeatures]) -> float:
        """Calculate overall network quality score (0-1)"""
        if not features:
            return 0.5
        
        # Combine latency, jitter, and packet loss
        avg_latency = np.mean([f.latency for f in features])
        avg_jitter = np.mean([f.jitter for f in features])
        avg_loss = np.mean([f.packet_loss for f in features])
        
        # Normalize and invert (lower is better for these metrics)
        latency_score = max(0, 1 - avg_latency / 1000)  # Assume 1000ms is very bad
        jitter_score = max(0, 1 - avg_jitter / 100)     # Assume 100ms jitter is very bad
        loss_score = max(0, 1 - avg_loss * 10)          # Packet loss is 0-1, scale by 10
        
        return (latency_score + jitter_score + loss_score) / 3
    
    def _get_dominant_applications(self, features: List[TrafficFeatures]) -> List[str]:
        """Get most commonly used applications"""
        app_counts = {}
        
        for feature in features:
            for app, usage in feature.application_mix.items():
                app_counts[app] = app_counts.get(app, 0) + usage
        
        # Sort by usage and return top 3
        sorted_apps = sorted(app_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        return [app for app, _ in sorted_apps]