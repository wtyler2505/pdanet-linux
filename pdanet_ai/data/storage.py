#!/usr/bin/env python3
"""
Data Storage Systems for AI-Enhanced PDanet-Linux

Provides comprehensive data storage capabilities for time-series network data,
user profiles, security events, and ML model artifacts.
"""

import asyncio
import logging
import json
import sqlite3
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..utils.config import Config

logger = logging.getLogger(__name__)

class TimeSeriesStorage:
    """Storage for time-series network data"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Database configuration
        self.db_path = Path(config.get('data_dir', 'data')) / 'timeseries.db'
        self.connection: Optional[sqlite3.Connection] = None
        
    async def initialize(self):
        """Initialize time-series storage"""
        self.logger.info("Initializing TimeSeriesStorage...")
        
        try:
            # Ensure data directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create database connection
            self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            
            # Create tables
            await self._create_tables()
            
            self.logger.info("TimeSeriesStorage initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize TimeSeriesStorage: {e}")
            raise
    
    async def _create_tables(self):
        """Create necessary database tables"""
        cursor = self.connection.cursor()
        
        # Network metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS network_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                interface_name TEXT,
                bytes_sent INTEGER,
                bytes_received INTEGER,
                packets_sent INTEGER,
                packets_received INTEGER,
                throughput_mbps REAL,
                latency_ms REAL,
                packet_loss_rate REAL,
                cpu_usage REAL,
                memory_usage REAL,
                metadata TEXT
            )
        """)
        
        # Traffic predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traffic_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                prediction_horizon INTEGER,
                predicted_bandwidth REAL,
                confidence REAL,
                model_used TEXT,
                actual_bandwidth REAL,
                prediction_error REAL
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_network_timestamp ON network_metrics(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON traffic_predictions(timestamp)")
        
        self.connection.commit()
    
    async def store_data(self, data: Dict[str, Any]):
        """Store network data point"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO network_metrics (
                    timestamp, interface_name, bytes_sent, bytes_received,
                    packets_sent, packets_received, throughput_mbps, latency_ms,
                    packet_loss_rate, cpu_usage, memory_usage, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('timestamp', datetime.utcnow()).isoformat(),
                data.get('interface_name'),
                data.get('bytes_sent', 0),
                data.get('bytes_received', 0),
                data.get('packets_sent', 0),
                data.get('packets_received', 0),
                data.get('throughput_mbps', 0.0),
                data.get('latency_ms', 0.0),
                data.get('packet_loss_rate', 0.0),
                data.get('cpu_usage', 0.0),
                data.get('memory_usage', 0.0),
                json.dumps(data.get('metadata', {}))
            ))
            
            self.connection.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to store data: {e}")
    
    async def get_data_range(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get data within time range"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT * FROM network_metrics 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp
            """, (start_time.isoformat(), end_time.isoformat()))
            
            rows = cursor.fetchall()
            
            return [{
                'timestamp': datetime.fromisoformat(row['timestamp']),
                'interface_name': row['interface_name'],
                'bytes_sent': row['bytes_sent'],
                'bytes_received': row['bytes_received'],
                'packets_sent': row['packets_sent'],
                'packets_received': row['packets_received'],
                'throughput_mbps': row['throughput_mbps'],
                'latency_ms': row['latency_ms'],
                'packet_loss_rate': row['packet_loss_rate'],
                'cpu_usage': row['cpu_usage'],
                'memory_usage': row['memory_usage'],
                'metadata': json.loads(row['metadata'] or '{}')
            } for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to get data range: {e}")
            return []

class UserDataStorage:
    """Storage for user profiles and behavior data"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.db_path = Path(config.get('data_dir', 'data')) / 'users.db'
        self.connection: Optional[sqlite3.Connection] = None
    
    async def initialize(self):
        """Initialize user data storage"""
        self.logger.info("Initializing UserDataStorage...")
        
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            await self._create_user_tables()
            
            self.logger.info("UserDataStorage initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize UserDataStorage: {e}")
            raise
    
    async def _create_user_tables(self):
        """Create user-related tables"""
        cursor = self.connection.cursor()
        
        # User profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                profile_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                confidence_score REAL DEFAULT 0.0
            )
        """)
        
        # Usage sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_minutes REAL,
                data_usage_mb REAL,
                applications_used TEXT,
                session_data TEXT,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        """)
        
        # User feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                feedback_data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        """)
        
        self.connection.commit()
    
    async def store_user_profile(self, profile: Dict[str, Any]):
        """Store or update user profile"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_profiles 
                (user_id, profile_data, created_at, last_updated, confidence_score)
                VALUES (?, ?, ?, ?, ?)
            """, (
                profile['user_id'],
                json.dumps(profile),
                profile.get('created_at', datetime.utcnow().isoformat()),
                profile.get('last_updated', datetime.utcnow().isoformat()),
                profile.get('confidence_score', 0.0)
            ))
            
            self.connection.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to store user profile: {e}")
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by ID"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute(
                "SELECT profile_data FROM user_profiles WHERE user_id = ?",
                (user_id,)
            )
            
            row = cursor.fetchone()
            if row:
                return json.loads(row['profile_data'])
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get user profile {user_id}: {e}")
            return None
    
    async def get_all_user_profiles(self) -> List[Dict[str, Any]]:
        """Get all user profiles"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT profile_data FROM user_profiles")
            rows = cursor.fetchall()
            
            return [json.loads(row['profile_data']) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to get all user profiles: {e}")
            return []

class SecurityEventStorage:
    """Storage for security events and threat data"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.db_path = Path(config.get('data_dir', 'data')) / 'security.db'
        self.connection: Optional[sqlite3.Connection] = None
    
    async def initialize(self):
        """Initialize security event storage"""
        self.logger.info("Initializing SecurityEventStorage...")
        
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            await self._create_security_tables()
            
            self.logger.info("SecurityEventStorage initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize SecurityEventStorage: {e}")
            raise
    
    async def _create_security_tables(self):
        """Create security-related tables"""
        cursor = self.connection.cursor()
        
        # Security events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                source_ip TEXT,
                destination_ip TEXT,
                protocol TEXT,
                port INTEGER,
                description TEXT,
                confidence REAL,
                raw_data TEXT,
                response_actions TEXT,
                resolved BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Threat intelligence table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threat_intelligence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                threat_type TEXT NOT NULL,
                indicators TEXT NOT NULL,
                severity TEXT NOT NULL,
                mitigation_actions TEXT,
                created_at TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                occurrence_count INTEGER DEFAULT 1
            )
        """)
        
        self.connection.commit()
    
    async def store_events(self, events: List[Dict[str, Any]]):
        """Store security events"""
        try:
            cursor = self.connection.cursor()
            
            for event in events:
                cursor.execute("""
                    INSERT OR REPLACE INTO security_events (
                        event_id, timestamp, event_type, severity, source_ip,
                        destination_ip, protocol, port, description, confidence,
                        raw_data, response_actions
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.get('event_id') or event.get('anomaly_id'),
                    event.get('timestamp', datetime.utcnow().isoformat()),
                    event.get('event_type') or event.get('anomaly_type'),
                    event.get('severity', 'medium'),
                    event.get('source_ip'),
                    event.get('destination_ip'),
                    event.get('protocol'),
                    event.get('port'),
                    event.get('description', ''),
                    event.get('confidence', 0.5),
                    json.dumps(event),
                    json.dumps(event.get('response_actions', []))
                ))
            
            self.connection.commit()
            self.logger.debug(f"Stored {len(events)} security events")
            
        except Exception as e:
            self.logger.error(f"Failed to store security events: {e}")
    
    async def get_recent_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent security events"""
        try:
            cursor = self.connection.cursor()
            
            cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
            
            cursor.execute("""
                SELECT * FROM security_events 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            """, (cutoff_time,))
            
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to get recent events: {e}")
            return []

class RewardStorage:
    """Storage for RL agent rewards and learning data"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.db_path = Path(config.get('data_dir', 'data')) / 'rewards.db'
        self.connection: Optional[sqlite3.Connection] = None
    
    async def initialize(self):
        """Initialize reward storage"""
        self.logger.info("Initializing RewardStorage...")
        
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            await self._create_reward_tables()
            
            self.logger.info("RewardStorage initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize RewardStorage: {e}")
            raise
    
    async def _create_reward_tables(self):
        """Create reward-related tables"""
        cursor = self.connection.cursor()
        
        # RL rewards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rl_rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                episode_id TEXT,
                state_vector TEXT NOT NULL,
                action_vector TEXT NOT NULL,
                reward REAL NOT NULL,
                next_state_vector TEXT,
                done BOOLEAN DEFAULT FALSE,
                metadata TEXT
            )
        """)
        
        self.connection.commit()
    
    async def store_reward(self, reward_data: Dict[str, Any]):
        """Store RL reward data"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO rl_rewards (
                    timestamp, state_vector, action_vector, reward,
                    next_state_vector, metadata
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                reward_data.get('timestamp', datetime.utcnow()).isoformat(),
                json.dumps(reward_data.get('state', {})),
                json.dumps(reward_data.get('action', {})),
                reward_data.get('reward', 0.0),
                json.dumps(reward_data.get('new_state', {})),
                json.dumps(reward_data)
            ))
            
            self.connection.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to store reward data: {e}")

class APIRequestStorage:
    """Storage for API requests and usage analytics"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.db_path = Path(config.get('data_dir', 'data')) / 'api.db'
        self.connection: Optional[sqlite3.Connection] = None
    
    async def initialize(self):
        """Initialize API request storage"""
        self.logger.info("Initializing APIRequestStorage...")
        
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            await self._create_api_tables()
            
            self.logger.info("APIRequestStorage initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize APIRequestStorage: {e}")
            raise
    
    async def _create_api_tables(self):
        """Create API-related tables"""
        cursor = self.connection.cursor()
        
        # API requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                method TEXT NOT NULL,
                url TEXT NOT NULL,
                status_code INTEGER NOT NULL,
                duration REAL NOT NULL,
                client_ip TEXT,
                user_agent TEXT,
                user_id TEXT,
                request_data TEXT,
                response_data TEXT
            )
        """)
        
        # API metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                request_count INTEGER,
                avg_response_time REAL,
                error_count INTEGER,
                success_rate REAL
            )
        """)
        
        self.connection.commit()
    
    async def store_request(self, request_data: Dict[str, Any]):
        """Store API request data"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO api_requests (
                    timestamp, method, url, status_code, duration,
                    client_ip, user_agent, request_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request_data.get('timestamp', datetime.utcnow()).isoformat(),
                request_data.get('method', ''),
                request_data.get('url', ''),
                request_data.get('status_code', 200),
                request_data.get('duration', 0.0),
                request_data.get('client_ip', ''),
                request_data.get('user_agent', ''),
                json.dumps(request_data)
            ))
            
            self.connection.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to store API request: {e}")

class ModelArtifactStorage:
    """Storage for ML model artifacts and checkpoints"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.models_dir = Path(config.get('ml.models_dir', 'ml_models'))
        
    async def initialize(self):
        """Initialize model artifact storage"""
        self.logger.info("Initializing ModelArtifactStorage...")
        
        try:
            self.models_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories for different model types
            for model_type in ['traffic_prediction', 'anomaly_detection', 'user_modeling', 'optimization_rl']:
                (self.models_dir / model_type).mkdir(exist_ok=True)
            
            self.logger.info("ModelArtifactStorage initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize ModelArtifactStorage: {e}")
            raise
    
    async def save_model(self, model_name: str, model_type: str, 
                        model_data: Any, metadata: Optional[Dict[str, Any]] = None):
        """Save ML model artifact"""
        try:
            model_dir = self.models_dir / model_type
            model_path = model_dir / f"{model_name}.pkl"
            metadata_path = model_dir / f"{model_name}_metadata.json"
            
            # Save model
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            # Save metadata
            model_metadata = {
                'model_name': model_name,
                'model_type': model_type,
                'saved_at': datetime.utcnow().isoformat(),
                'file_path': str(model_path),
                **(metadata or {})
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(model_metadata, f, indent=2)
            
            self.logger.info(f"Saved model {model_name} of type {model_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to save model {model_name}: {e}")
    
    async def load_model(self, model_name: str, model_type: str) -> Optional[Tuple[Any, Dict[str, Any]]]:
        """Load ML model artifact"""
        try:
            model_dir = self.models_dir / model_type
            model_path = model_dir / f"{model_name}.pkl"
            metadata_path = model_dir / f"{model_name}_metadata.json"
            
            if not model_path.exists():
                return None
            
            # Load model
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            # Load metadata
            metadata = {}
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
            
            self.logger.info(f"Loaded model {model_name} of type {model_type}")
            return model_data, metadata
            
        except Exception as e:
            self.logger.error(f"Failed to load model {model_name}: {e}")
            return None
    
    async def list_models(self, model_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available models"""
        try:
            models = []
            
            search_dirs = [self.models_dir / model_type] if model_type else self.models_dir.iterdir()
            
            for model_dir in search_dirs:
                if model_dir.is_dir():
                    for metadata_file in model_dir.glob("*_metadata.json"):
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                            models.append(metadata)
                        except Exception as e:
                            self.logger.debug(f"Could not read metadata {metadata_file}: {e}")
            
            return models
            
        except Exception as e:
            self.logger.error(f"Failed to list models: {e}")
            return []

class DataStorageManager:
    """Manages all data storage components"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize storage components
        self.timeseries = TimeSeriesStorage(config)
        self.user_data = UserDataStorage(config)
        self.security_events = SecurityEventStorage(config)
        self.api_requests = APIRequestStorage(config)
        self.model_artifacts = ModelArtifactStorage(config)
        
        self.storage_components = [
            self.timeseries,
            self.user_data,
            self.security_events,
            self.api_requests,
            self.model_artifacts
        ]
    
    async def initialize_all(self):
        """Initialize all storage components"""
        self.logger.info("Initializing all storage components...")
        
        try:
            for component in self.storage_components:
                await component.initialize()
            
            self.logger.info("All storage components initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize storage components: {e}")
            raise
    
    async def get_storage_status(self) -> Dict[str, Any]:
        """Get status of all storage components"""
        status = {
            'timestamp': datetime.utcnow().isoformat(),
            'components': {}
        }
        
        for component in self.storage_components:
            component_name = component.__class__.__name__
            try:
                # Basic status check - connection exists and is functional
                if hasattr(component, 'connection') and component.connection:
                    status['components'][component_name] = {
                        'status': 'healthy',
                        'initialized': True
                    }
                else:
                    status['components'][component_name] = {
                        'status': 'not_initialized',
                        'initialized': False
                    }
            except Exception as e:
                status['components'][component_name] = {
                    'status': 'error',
                    'error': str(e),
                    'initialized': False
                }
        
        return status
    
    async def cleanup(self):
        """Clean up storage resources"""
        try:
            for component in self.storage_components:
                if hasattr(component, 'connection') and component.connection:
                    component.connection.close()
            
            self.logger.info("Storage cleanup completed")
        except Exception as e:
            self.logger.error(f"Storage cleanup failed: {e}")