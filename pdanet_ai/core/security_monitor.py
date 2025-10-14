#!/usr/bin/env python3
"""
SecurityMonitor - AI-Powered Security and Anomaly Detection System

Implements advanced machine learning-based security monitoring with real-time
threat detection, behavioral anomaly analysis, and automated response capabilities.
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
from enum import Enum

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import torch
import torch.nn as nn

from ..utils.config import Config
from ..data.storage import SecurityEventStorage
from ..utils.network_utils import NetworkUtils

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class SecurityEvent:
    """Represents a security event or anomaly"""
    event_id: str
    timestamp: datetime
    event_type: str
    severity: ThreatLevel
    source_ip: Optional[str]
    destination_ip: Optional[str]
    protocol: Optional[str]
    port: Optional[int]
    description: str
    confidence: float
    raw_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['severity'] = self.severity.name
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class TrafficAnomaly:
    """Represents detected traffic anomaly"""
    anomaly_id: str
    detected_at: datetime
    anomaly_score: float
    traffic_features: Dict[str, float]
    anomaly_type: str
    affected_flows: List[Dict[str, Any]]
    mitigation_suggested: List[str]

@dataclass
class BehaviorProfile:
    """User/system behavior profile for anomaly detection"""
    profile_id: str
    entity_id: str  # user_id, device_id, etc.
    baseline_metrics: Dict[str, float]
    pattern_features: Dict[str, Any]
    last_updated: datetime
    confidence_level: float
    
class TrafficAnomalyDetector:
    """ML-based traffic anomaly detection"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # ML models for anomaly detection
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Feature tracking
        self.traffic_features = deque(maxlen=10000)
        self.baseline_established = False
        
    async def detect_anomalies(self, traffic_data: Dict[str, Any], 
                             baseline_model: Optional[Any] = None) -> List[TrafficAnomaly]:
        """Detect traffic anomalies using ML models"""
        try:
            # Extract features from traffic data
            features = self._extract_traffic_features(traffic_data)
            self.traffic_features.append(features)
            
            # Ensure we have enough data for detection
            if len(self.traffic_features) < 100:
                return []  # Need baseline data
            
            # Train model if not yet trained
            if not self.is_trained:
                await self._train_anomaly_model()
            
            # Detect anomalies
            anomalies = []
            
            # Feature-based anomaly detection
            feature_anomalies = await self._detect_feature_anomalies(features)
            anomalies.extend(feature_anomalies)
            
            # Pattern-based anomaly detection
            pattern_anomalies = await self._detect_pattern_anomalies(traffic_data)
            anomalies.extend(pattern_anomalies)
            
            # Statistical anomaly detection
            statistical_anomalies = await self._detect_statistical_anomalies(features)
            anomalies.extend(statistical_anomalies)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            return []
    
    def _extract_traffic_features(self, traffic_data: Dict[str, Any]) -> np.ndarray:
        """Extract numerical features from traffic data"""
        features = [
            # Volume features
            traffic_data.get('bytes_per_second', 0.0),
            traffic_data.get('packets_per_second', 0.0),
            traffic_data.get('connections_per_second', 0.0),
            
            # Quality features
            traffic_data.get('average_packet_size', 0.0),
            traffic_data.get('packet_size_variance', 0.0),
            traffic_data.get('inter_arrival_time_mean', 0.0),
            traffic_data.get('inter_arrival_time_variance', 0.0),
            
            # Protocol features
            traffic_data.get('tcp_ratio', 0.0),
            traffic_data.get('udp_ratio', 0.0),
            traffic_data.get('http_ratio', 0.0),
            traffic_data.get('https_ratio', 0.0),
            
            # Behavioral features
            traffic_data.get('unique_destinations', 0),
            traffic_data.get('port_diversity', 0.0),
            traffic_data.get('payload_entropy', 0.0),
            
            # Time-based features
            datetime.now().hour / 24.0,
            datetime.now().weekday() / 7.0,
        ]
        
        return np.array(features, dtype=np.float32)
    
    async def _train_anomaly_model(self):
        """Train the anomaly detection model"""
        if len(self.traffic_features) < 100:
            return
        
        try:
            # Prepare training data
            feature_matrix = np.vstack(list(self.traffic_features))
            
            # Scale features
            scaled_features = self.scaler.fit_transform(feature_matrix)
            
            # Train isolation forest
            self.isolation_forest.fit(scaled_features)
            
            self.is_trained = True
            self.baseline_established = True
            
            self.logger.info(f"Trained anomaly detection model with {len(self.traffic_features)} samples")
            
        except Exception as e:
            self.logger.error(f"Model training failed: {e}")
    
    async def _detect_feature_anomalies(self, features: np.ndarray) -> List[TrafficAnomaly]:
        """Detect anomalies using feature-based ML model"""
        if not self.is_trained:
            return []
        
        try:
            # Scale features
            scaled_features = self.scaler.transform(features.reshape(1, -1))
            
            # Get anomaly score
            anomaly_score = self.isolation_forest.decision_function(scaled_features)[0]
            is_anomaly = self.isolation_forest.predict(scaled_features)[0] == -1
            
            if is_anomaly:
                anomaly = TrafficAnomaly(
                    anomaly_id=self._generate_anomaly_id(),
                    detected_at=datetime.utcnow(),
                    anomaly_score=float(anomaly_score),
                    traffic_features=dict(zip(
                        ['bytes_ps', 'packets_ps', 'connections_ps', 'avg_pkt_size',
                         'pkt_size_var', 'iat_mean', 'iat_var', 'tcp_ratio',
                         'udp_ratio', 'http_ratio', 'https_ratio', 'unique_dest',
                         'port_div', 'payload_entropy', 'hour', 'weekday'],
                        features
                    )),
                    anomaly_type='feature_based',
                    affected_flows=[],
                    mitigation_suggested=['monitor', 'rate_limit']
                )
                
                return [anomaly]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Feature anomaly detection failed: {e}")
            return []
    
    async def _detect_pattern_anomalies(self, traffic_data: Dict[str, Any]) -> List[TrafficAnomaly]:
        """Detect anomalies in traffic patterns"""
        anomalies = []
        
        try:
            # Check for suspicious patterns
            
            # 1. Sudden traffic spike
            current_rate = traffic_data.get('bytes_per_second', 0)
            if len(self.traffic_features) > 10:
                recent_rates = [f[0] for f in list(self.traffic_features)[-10:]]  # bytes_per_second
                avg_rate = np.mean(recent_rates)
                
                if current_rate > avg_rate * 10 and current_rate > 1000000:  # 10x increase and > 1MB/s
                    anomaly = TrafficAnomaly(
                        anomaly_id=self._generate_anomaly_id(),
                        detected_at=datetime.utcnow(),
                        anomaly_score=min(1.0, current_rate / (avg_rate * 10)),
                        traffic_features={'current_rate': current_rate, 'avg_rate': avg_rate},
                        anomaly_type='traffic_spike',
                        affected_flows=[],
                        mitigation_suggested=['rate_limit', 'investigate_source']
                    )
                    anomalies.append(anomaly)
            
            # 2. Unusual port scanning behavior
            port_diversity = traffic_data.get('port_diversity', 0)
            if port_diversity > 0.8:  # Accessing many different ports
                anomaly = TrafficAnomaly(
                    anomaly_id=self._generate_anomaly_id(),
                    detected_at=datetime.utcnow(),
                    anomaly_score=port_diversity,
                    traffic_features={'port_diversity': port_diversity},
                    anomaly_type='port_scanning',
                    affected_flows=[],
                    mitigation_suggested=['block_source', 'alert_admin']
                )
                anomalies.append(anomaly)
            
            # 3. High entropy payload (potential encrypted malware)
            payload_entropy = traffic_data.get('payload_entropy', 0)
            if payload_entropy > 7.5:  # Very high entropy
                anomaly = TrafficAnomaly(
                    anomaly_id=self._generate_anomaly_id(),
                    detected_at=datetime.utcnow(),
                    anomaly_score=payload_entropy / 8.0,
                    traffic_features={'payload_entropy': payload_entropy},
                    anomaly_type='high_entropy_payload',
                    affected_flows=[],
                    mitigation_suggested=['deep_packet_inspection', 'quarantine']
                )
                anomalies.append(anomaly)
                
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Pattern anomaly detection failed: {e}")
            return []
    
    async def _detect_statistical_anomalies(self, features: np.ndarray) -> List[TrafficAnomaly]:
        """Detect statistical anomalies using simple statistical methods"""
        if len(self.traffic_features) < 50:  # Need enough data for statistics
            return []
        
        anomalies = []
        
        try:
            # Convert recent features to matrix
            recent_features = np.vstack(list(self.traffic_features)[-50:])  # Last 50 samples
            
            # Check each feature for statistical anomalies
            for i, feature_name in enumerate(['bytes_ps', 'packets_ps', 'connections_ps']):
                if i < len(features):
                    feature_values = recent_features[:, i]
                    mean_val = np.mean(feature_values)
                    std_val = np.std(feature_values)
                    
                    # Z-score anomaly detection
                    if std_val > 0:
                        z_score = abs((features[i] - mean_val) / std_val)
                        
                        if z_score > 3.0:  # 3-sigma rule
                            anomaly = TrafficAnomaly(
                                anomaly_id=self._generate_anomaly_id(),
                                detected_at=datetime.utcnow(),
                                anomaly_score=min(1.0, z_score / 5.0),
                                traffic_features={feature_name: float(features[i]), 'z_score': z_score},
                                anomaly_type='statistical_outlier',
                                affected_flows=[],
                                mitigation_suggested=['monitor']
                            )
                            anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Statistical anomaly detection failed: {e}")
            return []
    
    def _generate_anomaly_id(self) -> str:
        """Generate unique anomaly ID"""
        timestamp = datetime.utcnow().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    async def update_model(self, new_traffic_events: List[Dict[str, Any]]):
        """Update the anomaly detection model with new data"""
        try:
            # Add new features to buffer
            for event in new_traffic_events:
                features = self._extract_traffic_features(event)
                self.traffic_features.append(features)
            
            # Retrain if we have enough new data
            if len(new_traffic_events) > 50:
                await self._train_anomaly_model()
                self.logger.info(f"Updated anomaly model with {len(new_traffic_events)} new events")
                
        except Exception as e:
            self.logger.error(f"Model update failed: {e}")

class BehaviorAnomalyDetector:
    """Detects anomalies in user/system behavior patterns"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Behavior profiles storage
        self.behavior_profiles: Dict[str, BehaviorProfile] = {}
        self.behavior_history = defaultdict(lambda: deque(maxlen=1000))
        
        # Clustering for behavior analysis
        self.behavior_clusterer = DBSCAN(eps=0.5, min_samples=5)
        
    async def detect_anomalies(self, user_behavior: Dict[str, Any],
                             user_profile: Optional[BehaviorProfile] = None) -> List[SecurityEvent]:
        """Detect behavioral anomalies"""
        try:
            entity_id = user_behavior.get('entity_id', 'unknown')
            
            # Get or create behavior profile
            if entity_id not in self.behavior_profiles:
                await self._create_behavior_profile(entity_id, user_behavior)
                return []  # No anomalies for new profiles
            
            profile = self.behavior_profiles[entity_id]
            anomalies = []
            
            # Check various behavioral patterns
            
            # 1. Connection time anomalies
            connection_anomaly = await self._detect_connection_time_anomaly(user_behavior, profile)
            if connection_anomaly:
                anomalies.append(connection_anomaly)
            
            # 2. Data usage anomalies
            usage_anomaly = await self._detect_usage_anomaly(user_behavior, profile)
            if usage_anomaly:
                anomalies.append(usage_anomaly)
            
            # 3. Location/device anomalies
            location_anomaly = await self._detect_location_anomaly(user_behavior, profile)
            if location_anomaly:
                anomalies.append(location_anomaly)
            
            # 4. Application usage anomalies
            app_anomaly = await self._detect_application_anomaly(user_behavior, profile)
            if app_anomaly:
                anomalies.append(app_anomaly)
            
            # Update behavior profile
            await self._update_behavior_profile(entity_id, user_behavior)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Behavior anomaly detection failed: {e}")
            return []
    
    async def _create_behavior_profile(self, entity_id: str, initial_behavior: Dict[str, Any]):
        """Create new behavior profile for entity"""
        profile = BehaviorProfile(
            profile_id=f"profile_{entity_id}_{datetime.now().strftime('%Y%m%d')}",
            entity_id=entity_id,
            baseline_metrics={
                'avg_connection_duration': initial_behavior.get('connection_duration', 0),
                'avg_data_usage': initial_behavior.get('data_usage', 0),
                'typical_connection_time': initial_behavior.get('connection_time', 12),  # hour of day
                'primary_applications': initial_behavior.get('applications', []),
            },
            pattern_features={
                'connection_frequency': 1.0,
                'usage_variance': 0.0,
                'time_regularity': 1.0,
            },
            last_updated=datetime.utcnow(),
            confidence_level=0.1  # Low confidence for new profiles
        )
        
        self.behavior_profiles[entity_id] = profile
        self.logger.info(f"Created behavior profile for {entity_id}")
    
    async def _detect_connection_time_anomaly(self, behavior: Dict[str, Any], 
                                            profile: BehaviorProfile) -> Optional[SecurityEvent]:
        """Detect anomalies in connection timing patterns"""
        current_hour = datetime.now().hour
        typical_hour = profile.baseline_metrics.get('typical_connection_time', 12)
        
        # Check if connection time is significantly different from typical
        time_diff = abs(current_hour - typical_hour)
        if time_diff > 6:  # More than 6 hours difference
            return SecurityEvent(
                event_id=self._generate_event_id(),
                timestamp=datetime.utcnow(),
                event_type='unusual_connection_time',
                severity=ThreatLevel.MEDIUM,
                source_ip=behavior.get('source_ip'),
                destination_ip=None,
                protocol=None,
                port=None,
                description=f"Connection at unusual time: {current_hour}:00 (typical: {typical_hour}:00)",
                confidence=min(0.9, time_diff / 12.0),
                raw_data=behavior
            )
        
        return None
    
    async def _detect_usage_anomaly(self, behavior: Dict[str, Any], 
                                  profile: BehaviorProfile) -> Optional[SecurityEvent]:
        """Detect anomalies in data usage patterns"""
        current_usage = behavior.get('data_usage', 0)
        typical_usage = profile.baseline_metrics.get('avg_data_usage', 0)
        
        if typical_usage > 0:
            usage_ratio = current_usage / typical_usage
            
            if usage_ratio > 5.0:  # 5x normal usage
                return SecurityEvent(
                    event_id=self._generate_event_id(),
                    timestamp=datetime.utcnow(),
                    event_type='excessive_data_usage',
                    severity=ThreatLevel.HIGH if usage_ratio > 10 else ThreatLevel.MEDIUM,
                    source_ip=behavior.get('source_ip'),
                    destination_ip=None,
                    protocol=None,
                    port=None,
                    description=f"Data usage {usage_ratio:.1f}x higher than typical",
                    confidence=min(0.95, usage_ratio / 10.0),
                    raw_data=behavior
                )
        
        return None
    
    async def _detect_location_anomaly(self, behavior: Dict[str, Any], 
                                     profile: BehaviorProfile) -> Optional[SecurityEvent]:
        """Detect anomalies in connection location/device"""
        # Simplified location/device checking
        current_ip = behavior.get('source_ip', '')
        device_info = behavior.get('device_info', {})
        
        # Check for unusual IP patterns (very basic)
        if current_ip and len(current_ip.split('.')) == 4:
            ip_parts = current_ip.split('.')
            
            # Flag connections from unusual IP ranges
            if ip_parts[0] in ['10', '172', '192']:  # Private IPs are normal
                return None
            
            # Very basic geolocation anomaly (would need proper geolocation service)
            if ip_parts[0] in ['1', '2', '5']:  # Some suspicious ranges (simplified)
                return SecurityEvent(
                    event_id=self._generate_event_id(),
                    timestamp=datetime.utcnow(),
                    event_type='unusual_location',
                    severity=ThreatLevel.MEDIUM,
                    source_ip=current_ip,
                    destination_ip=None,
                    protocol=None,
                    port=None,
                    description=f"Connection from unusual IP range: {current_ip}",
                    confidence=0.6,
                    raw_data=behavior
                )
        
        return None
    
    async def _detect_application_anomaly(self, behavior: Dict[str, Any], 
                                        profile: BehaviorProfile) -> Optional[SecurityEvent]:
        """Detect anomalies in application usage patterns"""
        current_apps = set(behavior.get('applications', []))
        typical_apps = set(profile.baseline_metrics.get('primary_applications', []))
        
        # Check for completely new applications
        new_apps = current_apps - typical_apps
        
        if new_apps and len(new_apps) > 3:  # Many new applications
            return SecurityEvent(
                event_id=self._generate_event_id(),
                timestamp=datetime.utcnow(),
                event_type='unusual_applications',
                severity=ThreatLevel.MEDIUM,
                source_ip=behavior.get('source_ip'),
                destination_ip=None,
                protocol=None,
                port=None,
                description=f"Using {len(new_apps)} new applications: {list(new_apps)[:3]}",
                confidence=min(0.8, len(new_apps) / 5.0),
                raw_data=behavior
            )
        
        return None
    
    async def _update_behavior_profile(self, entity_id: str, behavior: Dict[str, Any]):
        """Update behavior profile with new data"""
        if entity_id not in self.behavior_profiles:
            return
        
        profile = self.behavior_profiles[entity_id]
        
        # Update baseline metrics (exponential moving average)
        alpha = 0.1  # Learning rate
        
        current_duration = behavior.get('connection_duration', 0)
        current_usage = behavior.get('data_usage', 0)
        current_hour = datetime.now().hour
        
        profile.baseline_metrics['avg_connection_duration'] = (
            alpha * current_duration + 
            (1 - alpha) * profile.baseline_metrics['avg_connection_duration']
        )
        
        profile.baseline_metrics['avg_data_usage'] = (
            alpha * current_usage + 
            (1 - alpha) * profile.baseline_metrics['avg_data_usage']
        )
        
        profile.baseline_metrics['typical_connection_time'] = (
            alpha * current_hour + 
            (1 - alpha) * profile.baseline_metrics['typical_connection_time']
        )
        
        # Update applications list
        current_apps = behavior.get('applications', [])
        if current_apps:
            existing_apps = set(profile.baseline_metrics.get('primary_applications', []))
            new_apps = set(current_apps)
            profile.baseline_metrics['primary_applications'] = list(existing_apps.union(new_apps))
        
        # Update confidence level
        profile.confidence_level = min(1.0, profile.confidence_level + 0.01)
        profile.last_updated = datetime.utcnow()
        
        # Store behavior history
        self.behavior_history[entity_id].append(behavior)
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = datetime.utcnow().isoformat()
        return hashlib.md5(f"behavior_{timestamp}".encode()).hexdigest()[:12]
    
    async def update_model(self, new_behavior_events: List[Dict[str, Any]]):
        """Update behavior models with new data"""
        try:
            for event in new_behavior_events:
                entity_id = event.get('entity_id', 'unknown')
                if entity_id != 'unknown':
                    if entity_id not in self.behavior_profiles:
                        await self._create_behavior_profile(entity_id, event)
                    else:
                        await self._update_behavior_profile(entity_id, event)
            
            self.logger.info(f"Updated behavior models with {len(new_behavior_events)} events")
            
        except Exception as e:
            self.logger.error(f"Behavior model update failed: {e}")

class ThreatClassifier:
    """Classifies and prioritizes security threats"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Threat classification rules
        self.threat_rules = {
            'port_scanning': {'base_severity': ThreatLevel.HIGH, 'urgency': 0.8},
            'traffic_spike': {'base_severity': ThreatLevel.MEDIUM, 'urgency': 0.6},
            'unusual_location': {'base_severity': ThreatLevel.MEDIUM, 'urgency': 0.5},
            'excessive_data_usage': {'base_severity': ThreatLevel.HIGH, 'urgency': 0.7},
            'high_entropy_payload': {'base_severity': ThreatLevel.CRITICAL, 'urgency': 0.9},
            'unusual_applications': {'base_severity': ThreatLevel.MEDIUM, 'urgency': 0.4},
        }
    
    async def classify(self, anomalies: List[Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Classify threats and determine response priority"""
        if not anomalies:
            return {
                'risk_level': 0.0,
                'threat_count': 0,
                'classifications': [],
                'recommended_actions': []
            }
        
        try:
            classifications = []
            max_risk = 0.0
            total_urgency = 0.0
            
            for anomaly in anomalies:
                classification = await self._classify_single_threat(anomaly, context)
                classifications.append(classification)
                
                max_risk = max(max_risk, classification['risk_score'])
                total_urgency += classification['urgency']
            
            # Overall assessment
            avg_urgency = total_urgency / len(anomalies) if anomalies else 0.0
            
            # Determine recommended actions
            recommended_actions = self._determine_actions(max_risk, avg_urgency, classifications)
            
            return {
                'risk_level': max_risk,
                'threat_count': len(anomalies),
                'classifications': classifications,
                'recommended_actions': recommended_actions,
                'urgency_score': avg_urgency,
                'assessment_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Threat classification failed: {e}")
            return {
                'risk_level': 0.5,  # Default moderate risk
                'threat_count': len(anomalies),
                'classifications': [],
                'recommended_actions': ['monitor'],
                'error': str(e)
            }
    
    async def _classify_single_threat(self, anomaly: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Classify a single threat"""
        # Determine threat type
        if hasattr(anomaly, 'anomaly_type'):
            threat_type = anomaly.anomaly_type
        elif hasattr(anomaly, 'event_type'):
            threat_type = anomaly.event_type
        else:
            threat_type = 'unknown'
        
        # Get base classification
        rule = self.threat_rules.get(threat_type, {
            'base_severity': ThreatLevel.MEDIUM,
            'urgency': 0.5
        })
        
        # Calculate risk score based on various factors
        base_risk = rule['base_severity'].value / 4.0  # Normalize to 0-1
        
        # Confidence multiplier
        confidence = getattr(anomaly, 'confidence', 0.5)
        if hasattr(anomaly, 'anomaly_score'):
            confidence = max(confidence, abs(anomaly.anomaly_score))
        
        # Context multipliers
        time_multiplier = self._get_time_risk_multiplier()
        network_multiplier = self._get_network_risk_multiplier(context)
        
        # Final risk score
        risk_score = min(1.0, base_risk * confidence * time_multiplier * network_multiplier)
        
        return {
            'threat_type': threat_type,
            'base_severity': rule['base_severity'].name,
            'risk_score': risk_score,
            'urgency': rule['urgency'],
            'confidence': confidence,
            'context_factors': {
                'time_multiplier': time_multiplier,
                'network_multiplier': network_multiplier
            },
            'anomaly_details': asdict(anomaly) if hasattr(anomaly, '__dict__') else str(anomaly)
        }
    
    def _get_time_risk_multiplier(self) -> float:
        """Get risk multiplier based on time of day"""
        current_hour = datetime.now().hour
        
        # Higher risk during off-hours (night/early morning)
        if 0 <= current_hour <= 6 or 22 <= current_hour <= 23:
            return 1.3
        # Normal risk during business hours
        elif 9 <= current_hour <= 17:
            return 1.0
        # Moderate risk during evening
        else:
            return 1.1
    
    def _get_network_risk_multiplier(self, context: Dict[str, Any]) -> float:
        """Get risk multiplier based on network context"""
        multiplier = 1.0
        
        # Higher risk for external connections
        if context.get('connection_type') == 'external':
            multiplier *= 1.2
        
        # Higher risk during high traffic periods
        traffic_load = context.get('current_traffic_load', 0.5)
        if traffic_load > 0.8:
            multiplier *= 1.1
        
        return multiplier
    
    def _determine_actions(self, max_risk: float, avg_urgency: float, 
                          classifications: List[Dict]) -> List[str]:
        """Determine recommended actions based on threat assessment"""
        actions = []
        
        # Based on maximum risk level
        if max_risk >= 0.9:
            actions.extend(['immediate_block', 'alert_admin', 'forensic_capture'])
        elif max_risk >= 0.7:
            actions.extend(['rate_limit', 'enhanced_monitoring', 'alert_admin'])
        elif max_risk >= 0.5:
            actions.extend(['monitor', 'log_detailed'])
        else:
            actions.extend(['monitor'])
        
        # Based on urgency
        if avg_urgency >= 0.8:
            actions.append('escalate_immediately')
        elif avg_urgency >= 0.6:
            actions.append('schedule_review')
        
        # Based on threat types
        threat_types = [c['threat_type'] for c in classifications]
        if 'port_scanning' in threat_types:
            actions.append('block_source_ip')
        if 'high_entropy_payload' in threat_types:
            actions.append('deep_packet_inspection')
        
        return list(set(actions))  # Remove duplicates
    
    async def retrain(self, new_threats: List[Dict[str, Any]], 
                     false_positives: List[Dict[str, Any]]):
        """Update threat classification based on feedback"""
        try:
            # Update threat rules based on confirmed threats
            for threat in new_threats:
                threat_type = threat.get('type')
                if threat_type in self.threat_rules:
                    # Increase severity/urgency for confirmed threats
                    current_urgency = self.threat_rules[threat_type]['urgency']
                    self.threat_rules[threat_type]['urgency'] = min(1.0, current_urgency + 0.1)
            
            # Decrease sensitivity for false positives
            for fp in false_positives:
                threat_type = fp.get('type')
                if threat_type in self.threat_rules:
                    current_urgency = self.threat_rules[threat_type]['urgency']
                    self.threat_rules[threat_type]['urgency'] = max(0.1, current_urgency - 0.05)
            
            self.logger.info(
                f"Updated threat classification: {len(new_threats)} confirmed, "
                f"{len(false_positives)} false positives"
            )
            
        except Exception as e:
            self.logger.error(f"Threat classifier retraining failed: {e}")

class SecurityResponseEngine:
    """Automated security response and mitigation engine"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.network_utils = NetworkUtils()
        
        # Response action mappings
        self.action_handlers = {
            'monitor': self._action_monitor,
            'rate_limit': self._action_rate_limit,
            'block_source_ip': self._action_block_ip,
            'alert_admin': self._action_alert_admin,
            'enhanced_monitoring': self._action_enhanced_monitoring,
            'forensic_capture': self._action_forensic_capture,
        }
    
    async def respond(self, threat_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Execute automated response to threats"""
        try:
            response_results = []
            
            recommended_actions = threat_assessment.get('recommended_actions', [])
            
            for action in recommended_actions:
                if action in self.action_handlers:
                    try:
                        result = await self.action_handlers[action](threat_assessment)
                        response_results.append({
                            'action': action,
                            'success': result.get('success', True),
                            'details': result
                        })
                    except Exception as e:
                        response_results.append({
                            'action': action,
                            'success': False,
                            'error': str(e)
                        })
                else:
                    response_results.append({
                        'action': action,
                        'success': False,
                        'error': 'Unknown action'
                    })
            
            return {
                'response_executed': True,
                'actions_taken': len([r for r in response_results if r['success']]),
                'actions_failed': len([r for r in response_results if not r['success']]),
                'results': response_results,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Security response failed: {e}")
            return {
                'response_executed': False,
                'error': str(e)
            }
    
    async def _action_monitor(self, threat_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced monitoring action"""
        self.logger.info(f"Enhanced monitoring activated for threat level {threat_assessment.get('risk_level')}")
        return {'success': True, 'action': 'monitoring_enhanced'}
    
    async def _action_rate_limit(self, threat_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Rate limiting action"""
        try:
            # Apply rate limiting based on threat level
            risk_level = threat_assessment.get('risk_level', 0.5)
            limit_factor = 1.0 - (risk_level * 0.5)  # Reduce limits based on risk
            
            result = await self.network_utils.apply_rate_limiting(limit_factor)
            
            self.logger.info(f"Applied rate limiting: factor={limit_factor}")
            return {'success': True, 'limit_factor': limit_factor, 'result': result}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _action_block_ip(self, threat_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Block source IP action"""
        try:
            # Extract source IPs from threat classifications
            source_ips = set()
            for classification in threat_assessment.get('classifications', []):
                anomaly_details = classification.get('anomaly_details', {})
                if isinstance(anomaly_details, dict):
                    source_ip = anomaly_details.get('source_ip')
                    if source_ip:
                        source_ips.add(source_ip)
            
            blocked_ips = []
            for ip in source_ips:
                try:
                    result = await self.network_utils.block_ip_address(ip)
                    blocked_ips.append(ip)
                    self.logger.info(f"Blocked IP address: {ip}")
                except Exception as e:
                    self.logger.error(f"Failed to block IP {ip}: {e}")
            
            return {
                'success': len(blocked_ips) > 0,
                'blocked_ips': blocked_ips,
                'total_attempted': len(source_ips)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _action_alert_admin(self, threat_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Send alert to administrators"""
        try:
            alert_message = {
                'type': 'security_alert',
                'timestamp': datetime.utcnow().isoformat(),
                'risk_level': threat_assessment.get('risk_level'),
                'threat_count': threat_assessment.get('threat_count'),
                'summary': f"Security threat detected with risk level {threat_assessment.get('risk_level', 0):.2f}",
                'details': threat_assessment
            }
            
            # In a real implementation, this would send email/SMS/Slack notification
            self.logger.warning(f"SECURITY ALERT: {alert_message['summary']}")
            
            return {
                'success': True,
                'alert_sent': True,
                'message': alert_message['summary']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _action_enhanced_monitoring(self, threat_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Enable enhanced monitoring"""
        try:
            # Increase monitoring frequency and detail level
            monitoring_config = {
                'packet_capture': True,
                'detailed_logging': True,
                'real_time_analysis': True,
                'duration': '1h'  # Enhanced monitoring for 1 hour
            }
            
            # Apply enhanced monitoring configuration
            result = await self.network_utils.configure_enhanced_monitoring(monitoring_config)
            
            self.logger.info("Enhanced monitoring activated")
            return {
                'success': True,
                'monitoring_config': monitoring_config,
                'result': result
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _action_forensic_capture(self, threat_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Start forensic data capture"""
        try:
            capture_config = {
                'full_packet_capture': True,
                'metadata_collection': True,
                'duration': '30m',  # 30 minutes of capture
                'storage_path': '/var/log/forensics/',
                'threat_context': threat_assessment
            }
            
            # Start forensic capture
            result = await self.network_utils.start_forensic_capture(capture_config)
            
            self.logger.warning("Forensic data capture started")
            return {
                'success': True,
                'capture_config': capture_config,
                'result': result
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

class SecurityMonitor:
    """Main AI-powered security monitoring system"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Security components
        self.traffic_analyzer = TrafficAnomalyDetector(config)
        self.behavior_monitor = BehaviorAnomalyDetector(config)
        self.threat_classifier = ThreatClassifier(config)
        self.response_engine = SecurityResponseEngine(config)
        
        # Storage and utilities
        self.event_storage = SecurityEventStorage(config)
        self.network_utils = NetworkUtils()
        
        # State tracking
        self.active_threats = {}
        self.security_metrics = deque(maxlen=1000)
        
    async def initialize(self):
        """Initialize security monitoring system"""
        self.logger.info("Initializing SecurityMonitor...")
        
        try:
            await self.event_storage.initialize()
            self.logger.info("SecurityMonitor initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize SecurityMonitor: {e}")
            raise
    
    async def analyze(self, network_state: Any) -> Dict[str, Any]:
        """Main security analysis function"""
        try:
            # Convert network state to analysis format
            analysis_data = self._prepare_analysis_data(network_state)
            
            # Traffic anomaly detection
            traffic_anomalies = await self.traffic_analyzer.detect_anomalies(
                analysis_data['traffic_data']
            )
            
            # Behavior anomaly detection
            behavior_anomalies = await self.behavior_monitor.detect_anomalies(
                analysis_data['behavior_data']
            )
            
            # Combine all anomalies
            all_anomalies = traffic_anomalies + behavior_anomalies
            
            # Classify threats
            threat_assessment = await self.threat_classifier.classify(
                all_anomalies,
                analysis_data['context']
            )
            
            # Store security events
            await self._store_security_events(all_anomalies, threat_assessment)
            
            # Update metrics
            self.security_metrics.append({
                'timestamp': datetime.utcnow(),
                'anomaly_count': len(all_anomalies),
                'risk_level': threat_assessment.get('risk_level', 0.0),
                'threat_types': [a.anomaly_type if hasattr(a, 'anomaly_type') else 'unknown' for a in all_anomalies]
            })
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'anomalies_detected': len(all_anomalies),
                'traffic_anomalies': len(traffic_anomalies),
                'behavior_anomalies': len(behavior_anomalies),
                'threat_assessment': threat_assessment,
                'security_status': self._calculate_security_status(threat_assessment),
            }
            
        except Exception as e:
            self.logger.error(f"Security analysis failed: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'security_status': 'unknown'
            }
    
    def _prepare_analysis_data(self, network_state: Any) -> Dict[str, Any]:
        """Prepare data for security analysis"""
        state_dict = network_state.__dict__ if hasattr(network_state, '__dict__') else {}
        
        return {
            'traffic_data': {
                'bytes_per_second': state_dict.get('bandwidth_usage', {}).get('total', 0) * 8,  # Convert to bits
                'packets_per_second': len(state_dict.get('connections', [])) * 10,  # Rough estimate
                'connections_per_second': len(state_dict.get('connections', [])) / 60,  # Per minute to per second
                'average_packet_size': 1024,  # Default
                'packet_size_variance': 200,  # Default
                'inter_arrival_time_mean': 0.1,  # Default
                'inter_arrival_time_variance': 0.05,  # Default
                'tcp_ratio': 0.8,  # Default
                'udp_ratio': 0.2,  # Default
                'http_ratio': 0.4,  # Default
                'https_ratio': 0.6,  # Default
                'unique_destinations': len(set([str(c) for c in state_dict.get('connections', [])])),
                'port_diversity': min(1.0, len(state_dict.get('connections', [])) / 100),
                'payload_entropy': 6.0,  # Default entropy
            },
            'behavior_data': {
                'entity_id': 'system',
                'connection_duration': 300,  # 5 minutes default
                'data_usage': state_dict.get('bandwidth_usage', {}).get('total', 0),
                'connection_time': datetime.now().hour,
                'applications': state_dict.get('active_applications', []),
                'source_ip': '192.168.1.100',  # Default
                'device_info': {}
            },
            'context': {
                'connection_type': 'internal',
                'current_traffic_load': min(1.0, state_dict.get('cpu_usage', 0.5)),
                'network_interfaces': len(state_dict.get('interfaces', {})),
            }
        }
    
    async def _store_security_events(self, anomalies: List[Any], threat_assessment: Dict[str, Any]):
        """Store security events for analysis"""
        try:
            events = []
            
            for anomaly in anomalies:
                if hasattr(anomaly, '__dict__'):
                    event_data = asdict(anomaly)
                    event_data['threat_assessment'] = threat_assessment
                    events.append(event_data)
            
            if events:
                await self.event_storage.store_events(events)
                
        except Exception as e:
            self.logger.error(f"Failed to store security events: {e}")
    
    def _calculate_security_status(self, threat_assessment: Dict[str, Any]) -> str:
        """Calculate overall security status"""
        risk_level = threat_assessment.get('risk_level', 0.0)
        
        if risk_level >= 0.8:
            return 'critical'
        elif risk_level >= 0.6:
            return 'high_risk'
        elif risk_level >= 0.4:
            return 'medium_risk'
        elif risk_level >= 0.2:
            return 'low_risk'
        else:
            return 'secure'
    
    async def apply_security_config(self, security_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply security configuration changes"""
        try:
            results = {}
            
            # Apply threat response level changes
            if 'threat_response_level' in security_config:
                level = security_config['threat_response_level']
                # Configure response sensitivity
                results['threat_response'] = f"Set to level {level}"
            
            # Apply monitoring intensity changes
            if 'monitoring_intensity' in security_config:
                intensity = security_config['monitoring_intensity']
                # Configure monitoring frequency
                results['monitoring_intensity'] = f"Set to {intensity}"
            
            return {
                'security_config_applied': True,
                'results': results,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Security configuration failed: {e}")
            return {
                'security_config_applied': False,
                'error': str(e)
            }
    
    async def get_security_insights(self) -> Dict[str, Any]:
        """Get security insights and statistics"""
        if not self.security_metrics:
            return {'status': 'no_data'}
        
        recent_metrics = list(self.security_metrics)[-100:]  # Last 100 measurements
        
        avg_risk = np.mean([m['risk_level'] for m in recent_metrics])
        avg_anomalies = np.mean([m['anomaly_count'] for m in recent_metrics])
        
        # Threat type frequency
        all_threat_types = []
        for m in recent_metrics:
            all_threat_types.extend(m.get('threat_types', []))
        
        threat_frequency = {}
        for threat_type in all_threat_types:
            threat_frequency[threat_type] = threat_frequency.get(threat_type, 0) + 1
        
        return {
            'avg_risk_level': avg_risk,
            'avg_anomalies_per_analysis': avg_anomalies,
            'threat_type_frequency': threat_frequency,
            'total_analyses': len(recent_metrics),
            'security_trend': 'improving' if len(recent_metrics) > 1 and recent_metrics[-1]['risk_level'] < recent_metrics[0]['risk_level'] else 'stable',
            'last_analysis': recent_metrics[-1]['timestamp'].isoformat() if recent_metrics else None
        }