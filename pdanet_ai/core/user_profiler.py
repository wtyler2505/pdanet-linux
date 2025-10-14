#!/usr/bin/env python3
"""
UserProfiler - Advanced User Behavior Analysis and Personalization

Implements sophisticated user behavior modeling, preference learning,
and personalized network optimization using machine learning techniques.
"""

import asyncio
import logging
import json
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict, deque
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier

from ..utils.config import Config
from ..data.storage import UserDataStorage

logger = logging.getLogger(__name__)

@dataclass
class UsageSession:
    """Represents a user's network usage session"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: float
    total_data_mb: float
    avg_bandwidth_mbps: float
    peak_bandwidth_mbps: float
    applications_used: List[str]
    connection_type: str
    location_context: Optional[str]
    quality_metrics: Dict[str, float]
    user_satisfaction: Optional[float]  # 0-1 scale
    
    def to_feature_vector(self) -> np.ndarray:
        """Convert session to ML feature vector"""
        # Time-based features
        hour_of_day = self.start_time.hour / 24.0
        day_of_week = self.start_time.weekday() / 7.0
        
        # Usage features
        features = [
            self.duration_minutes / 480.0,  # Normalize to 8-hour max
            self.total_data_mb / 10000.0,   # Normalize to 10GB max
            self.avg_bandwidth_mbps / 100.0, # Normalize to 100 Mbps max
            self.peak_bandwidth_mbps / 100.0,
            len(self.applications_used) / 20.0,  # Max 20 apps
            hour_of_day,
            day_of_week,
            self.quality_metrics.get('avg_latency', 100) / 1000.0,  # Normalize latency
            self.quality_metrics.get('packet_loss', 0.01) * 100,    # Scale packet loss
            self.user_satisfaction or 0.5,  # Default neutral satisfaction
        ]
        
        # Connection type encoding
        conn_encoding = {'wifi': 0.0, 'cellular': 1.0, 'ethernet': 0.5}
        features.append(conn_encoding.get(self.connection_type, 0.5))
        
        return np.array(features, dtype=np.float32)

@dataclass
class UserProfile:
    """Comprehensive user profile with learned preferences and patterns"""
    user_id: str
    created_at: datetime
    last_updated: datetime
    total_sessions: int
    
    # Usage patterns
    typical_usage_hours: List[int]
    avg_session_duration: float
    avg_daily_data_gb: float
    preferred_applications: List[str]
    connection_preferences: Dict[str, float]
    
    # Quality preferences
    latency_sensitivity: float    # 0-1 (0=tolerant, 1=very sensitive)
    bandwidth_priority: float     # 0-1 (0=low, 1=high)
    reliability_importance: float # 0-1 (0=not important, 1=critical)
    cost_consciousness: float     # 0-1 (0=cost no object, 1=very cost conscious)
    
    # Learned behaviors
    optimization_acceptance: float  # How often user accepts AI suggestions
    manual_override_frequency: float # How often user manually overrides AI
    feedback_responsiveness: float  # How responsive to feedback
    
    # Personalization settings
    automation_level: float        # 0-1 (0=manual, 1=fully automated)
    notification_preferences: Dict[str, bool]
    customization_preferences: Dict[str, Any]
    
    # Clustering and modeling
    user_cluster: Optional[int] = None
    behavior_model: Optional[str] = None
    confidence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_updated'] = self.last_updated.isoformat()
        return data

class BehaviorAnalyzer:
    """Analyzes user behavior patterns using machine learning"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # ML models for behavior analysis
        self.usage_clusterer = KMeans(n_clusters=5, random_state=42)
        self.pattern_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
        # Model state
        self.models_trained = False
        self.cluster_labels = {
            0: 'light_user',
            1: 'heavy_user', 
            2: 'business_user',
            3: 'entertainment_user',
            4: 'mixed_user'
        }
        
    async def analyze(self, data: List[UsageSession], 
                     features: List[str]) -> Dict[str, Any]:
        """Analyze user behavior patterns from session data"""
        try:
            if not data:
                return {'error': 'No data provided for analysis'}
            
            # Convert sessions to feature vectors
            feature_vectors = np.array([session.to_feature_vector() for session in data])
            
            if len(feature_vectors) < 5:  # Need minimum data for analysis
                return await self._simple_analysis(data)
            
            # Perform clustering analysis
            cluster_analysis = await self._perform_clustering(feature_vectors)
            
            # Temporal pattern analysis
            temporal_patterns = await self._analyze_temporal_patterns(data)
            
            # Application usage analysis
            app_analysis = await self._analyze_application_usage(data)
            
            # Quality preference analysis
            quality_analysis = await self._analyze_quality_preferences(data)
            
            return {
                'cluster_analysis': cluster_analysis,
                'temporal_patterns': temporal_patterns,
                'application_analysis': app_analysis,
                'quality_preferences': quality_analysis,
                'total_sessions_analyzed': len(data),
                'analysis_confidence': self._calculate_analysis_confidence(len(data))
            }
            
        except Exception as e:
            self.logger.error(f"Behavior analysis failed: {e}")
            return {'error': str(e)}
    
    async def _perform_clustering(self, feature_vectors: np.ndarray) -> Dict[str, Any]:
        """Perform clustering analysis on user behavior"""
        try:
            # Scale features
            if not self.models_trained:
                scaled_features = self.scaler.fit_transform(feature_vectors)
                self.models_trained = True
            else:
                scaled_features = self.scaler.transform(feature_vectors)
            
            # Perform clustering
            cluster_labels = self.usage_clusterer.fit_predict(scaled_features)
            
            # Analyze clusters
            unique_clusters, cluster_counts = np.unique(cluster_labels, return_counts=True)
            
            # Determine primary cluster
            primary_cluster = unique_clusters[np.argmax(cluster_counts)]
            primary_cluster_name = self.cluster_labels.get(primary_cluster, f'cluster_{primary_cluster}')
            
            return {
                'primary_cluster': primary_cluster_name,
                'cluster_distribution': dict(zip(unique_clusters.tolist(), cluster_counts.tolist())),
                'behavior_consistency': float(np.max(cluster_counts) / len(cluster_labels)),
                'total_clusters_used': len(unique_clusters)
            }
            
        except Exception as e:
            self.logger.error(f"Clustering analysis failed: {e}")
            return {'error': str(e)}
    
    async def _analyze_temporal_patterns(self, sessions: List[UsageSession]) -> Dict[str, Any]:
        """Analyze temporal usage patterns"""
        try:
            # Extract usage hours
            usage_hours = [session.start_time.hour for session in sessions]
            weekdays = [session.start_time.weekday() for session in sessions]
            
            # Find peak usage hours
            hour_counts = {}
            for hour in usage_hours:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
            peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Weekday vs weekend analysis
            weekday_sessions = [s for s in sessions if s.start_time.weekday() < 5]
            weekend_sessions = [s for s in sessions if s.start_time.weekday() >= 5]
            
            patterns = {
                'peak_usage_hours': [f"{hour:02d}:00" for hour, _ in peak_hours],
                'avg_session_duration': float(np.mean([s.duration_minutes for s in sessions])),
                'weekday_usage_ratio': len(weekday_sessions) / len(sessions),
                'most_active_day': self._get_most_active_day(weekdays),
                'usage_regularity': self._calculate_usage_regularity(usage_hours)
            }
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Temporal pattern analysis failed: {e}")
            return {'error': str(e)}
    
    def _get_most_active_day(self, weekdays: List[int]) -> str:
        """Find most active day of week"""
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        if not weekdays:
            return 'Unknown'
        
        day_counts = {}
        for day in weekdays:
            day_counts[day] = day_counts.get(day, 0) + 1
        
        most_active_day_num = max(day_counts.items(), key=lambda x: x[1])[0]
        return day_names[most_active_day_num]
    
    def _calculate_usage_regularity(self, usage_hours: List[int]) -> float:
        """Calculate how regular usage patterns are (0-1 scale)"""
        if len(usage_hours) < 2:
            return 0.5
        
        # Calculate standard deviation of usage hours
        std_dev = np.std(usage_hours)
        
        # Convert to regularity score (lower std dev = higher regularity)
        regularity = max(0, 1 - (std_dev / 12))  # 12 hours max deviation
        return float(regularity)
    
    async def _analyze_application_usage(self, sessions: List[UsageSession]) -> Dict[str, Any]:
        """Analyze application usage patterns"""
        try:
            all_apps = []
            for session in sessions:
                all_apps.extend(session.applications_used)
            
            if not all_apps:
                return {'error': 'No application data found'}
            
            # Count application usage
            app_counts = {}
            for app in all_apps:
                app_counts[app] = app_counts.get(app, 0) + 1
            
            # Sort by usage frequency
            sorted_apps = sorted(app_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Calculate usage diversity
            total_app_instances = len(all_apps)
            unique_apps = len(set(all_apps))
            diversity_score = unique_apps / max(total_app_instances, 1)
            
            return {
                'top_applications': sorted_apps[:5],
                'application_diversity': diversity_score,
                'total_unique_applications': unique_apps,
                'primary_application_category': self._categorize_primary_usage(sorted_apps)
            }
            
        except Exception as e:
            self.logger.error(f"Application analysis failed: {e}")
            return {'error': str(e)}
    
    def _categorize_primary_usage(self, sorted_apps: List[Tuple[str, int]]) -> str:
        """Categorize primary usage type based on top applications"""
        if not sorted_apps:
            return 'unknown'
        
        top_app = sorted_apps[0][0].lower()
        
        categories = {
            'productivity': ['teams', 'zoom', 'slack', 'office', 'outlook'],
            'entertainment': ['netflix', 'youtube', 'spotify', 'twitch', 'gaming'],
            'social': ['discord', 'telegram', 'whatsapp', 'facebook'],
            'development': ['vscode', 'github', 'docker', 'terminal'],
            'browsing': ['chrome', 'firefox', 'safari', 'edge']
        }
        
        for category, apps in categories.items():
            if any(app in top_app for app in apps):
                return category
        
        return 'general'
    
    async def _analyze_quality_preferences(self, sessions: List[UsageSession]) -> Dict[str, Any]:
        """Analyze user's quality of service preferences"""
        try:
            # Extract quality metrics and satisfaction scores
            latencies = [s.quality_metrics.get('avg_latency', 100) for s in sessions]
            packet_losses = [s.quality_metrics.get('packet_loss', 0.01) for s in sessions]
            satisfactions = [s.user_satisfaction for s in sessions if s.user_satisfaction is not None]
            
            # Analyze satisfaction correlation with quality metrics
            if len(satisfactions) >= 5:
                # Simple correlation analysis
                latency_tolerance = await self._calculate_quality_tolerance(latencies, satisfactions)
                reliability_importance = await self._calculate_reliability_importance(packet_losses, satisfactions)
            else:
                # Default values
                latency_tolerance = 0.5
                reliability_importance = 0.7
            
            return {
                'latency_sensitivity': 1.0 - latency_tolerance,  # Invert for sensitivity
                'reliability_importance': reliability_importance,
                'avg_latency_experienced': float(np.mean(latencies)),
                'avg_packet_loss_experienced': float(np.mean(packet_losses)),
                'satisfaction_trend': self._calculate_satisfaction_trend(satisfactions)
            }
            
        except Exception as e:
            self.logger.error(f"Quality preference analysis failed: {e}")
            return {'error': str(e)}
    
    async def _calculate_quality_tolerance(self, latencies: List[float], 
                                         satisfactions: List[float]) -> float:
        """Calculate user's tolerance for latency"""
        if len(latencies) != len(satisfactions) or len(latencies) < 3:
            return 0.5  # Default moderate tolerance
        
        # Find correlation between latency and satisfaction
        correlation = np.corrcoef(latencies, satisfactions)[0, 1]
        
        # Convert correlation to tolerance (negative correlation means less tolerant)
        tolerance = 0.5 + (correlation * 0.5) if not np.isnan(correlation) else 0.5
        return max(0, min(1, tolerance))
    
    async def _calculate_reliability_importance(self, packet_losses: List[float], 
                                              satisfactions: List[float]) -> float:
        """Calculate importance of reliability to user"""
        if len(packet_losses) != len(satisfactions) or len(packet_losses) < 3:
            return 0.7  # Default high importance
        
        # Find correlation between packet loss and satisfaction
        correlation = np.corrcoef(packet_losses, satisfactions)[0, 1]
        
        # Convert to importance (negative correlation means high importance)
        importance = 0.5 - (correlation * 0.5) if not np.isnan(correlation) else 0.7
        return max(0, min(1, importance))
    
    def _calculate_satisfaction_trend(self, satisfactions: List[float]) -> str:
        """Calculate trend in user satisfaction"""
        if len(satisfactions) < 3:
            return 'stable'
        
        # Simple linear trend
        x = np.arange(len(satisfactions))
        slope = np.polyfit(x, satisfactions, 1)[0]
        
        if slope > 0.05:
            return 'improving'
        elif slope < -0.05:
            return 'declining'
        else:
            return 'stable'
    
    async def _simple_analysis(self, sessions: List[UsageSession]) -> Dict[str, Any]:
        """Simple analysis for insufficient data"""
        if not sessions:
            return {'error': 'No sessions to analyze'}
        
        return {
            'simple_analysis': True,
            'total_sessions': len(sessions),
            'avg_duration': float(np.mean([s.duration_minutes for s in sessions])),
            'total_data': float(sum([s.total_data_mb for s in sessions])),
            'most_used_apps': list(set([app for s in sessions for app in s.applications_used]))[:5]
        }

class UsagePredictor:
    """Predicts user's future usage patterns and needs"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Prediction models
        self.usage_predictor = None  # Would be a trained time-series model
        self.need_predictor = None   # Would be a trained classification model
        
    async def predict(self, profile: UserProfile, context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict user's usage needs based on profile and context"""
        try:
            # Extract context features
            current_time = datetime.now()
            time_context = context.get('time', {})
            location_context = context.get('location', {})
            device_context = context.get('device', {})
            
            # Predict bandwidth needs
            predicted_bandwidth = await self._predict_bandwidth_needs(
                profile, current_time, time_context
            )
            
            # Predict session duration
            predicted_duration = await self._predict_session_duration(
                profile, current_time
            )
            
            # Predict quality requirements
            quality_needs = await self._predict_quality_needs(
                profile, context
            )
            
            # Predict application usage
            likely_applications = await self._predict_application_usage(
                profile, current_time
            )
            
            return {
                'predicted_bandwidth_mbps': predicted_bandwidth,
                'predicted_duration_minutes': predicted_duration,
                'quality_requirements': quality_needs,
                'likely_applications': likely_applications,
                'prediction_confidence': 0.75,  # Would be calculated from model uncertainty
                'context_factors': {
                    'time_of_day': current_time.hour,
                    'day_of_week': current_time.weekday(),
                    'is_peak_hour': current_time.hour in profile.typical_usage_hours
                }
            }
            
        except Exception as e:
            self.logger.error(f"Usage prediction failed: {e}")
            return {'error': str(e)}
    
    async def _predict_bandwidth_needs(self, profile: UserProfile, 
                                      current_time: datetime,
                                      time_context: Dict[str, Any]) -> float:
        """Predict bandwidth needs for current context"""
        base_bandwidth = profile.avg_daily_data_gb * 8 * 1024 / (24 * 60)  # Convert GB/day to Mbps
        
        # Time-based adjustments
        hour = current_time.hour
        if hour in profile.typical_usage_hours:
            time_multiplier = 1.5  # Higher usage during typical hours
        else:
            time_multiplier = 0.7  # Lower usage outside typical hours
        
        # Application-based adjustments
        if 'video' in profile.preferred_applications or 'streaming' in profile.preferred_applications:
            app_multiplier = 1.3
        elif 'gaming' in profile.preferred_applications:
            app_multiplier = 1.2
        else:
            app_multiplier = 1.0
        
        predicted_bandwidth = base_bandwidth * time_multiplier * app_multiplier
        
        # Apply bounds
        return max(1.0, min(100.0, predicted_bandwidth))
    
    async def _predict_session_duration(self, profile: UserProfile, 
                                       current_time: datetime) -> float:
        """Predict likely session duration"""
        base_duration = profile.avg_session_duration
        
        # Time-based adjustments
        hour = current_time.hour
        if hour in profile.typical_usage_hours:
            duration_multiplier = 1.2
        elif 22 <= hour or hour <= 6:  # Late night/early morning
            duration_multiplier = 0.8
        else:
            duration_multiplier = 1.0
        
        # Weekday vs weekend
        if current_time.weekday() >= 5:  # Weekend
            duration_multiplier *= 1.3
        
        return base_duration * duration_multiplier
    
    async def _predict_quality_needs(self, profile: UserProfile, 
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict quality of service needs"""
        return {
            'latency_requirement': 'low' if profile.latency_sensitivity > 0.7 else 'medium',
            'bandwidth_priority': 'high' if profile.bandwidth_priority > 0.7 else 'medium',
            'reliability_need': 'high' if profile.reliability_importance > 0.8 else 'medium'
        }
    
    async def _predict_application_usage(self, profile: UserProfile, 
                                        current_time: datetime) -> List[str]:
        """Predict likely application usage"""
        # Return top applications with time-based weighting
        hour = current_time.hour
        
        # Time-based application preferences
        time_apps = {
            'morning': ['email', 'news', 'weather'],
            'work_hours': ['teams', 'zoom', 'slack', 'browser'],
            'evening': ['netflix', 'youtube', 'gaming', 'spotify'],
            'night': ['entertainment', 'social', 'browsing']
        }
        
        if 6 <= hour <= 9:
            time_category = 'morning'
        elif 9 <= hour <= 17:
            time_category = 'work_hours'
        elif 17 <= hour <= 22:
            time_category = 'evening'
        else:
            time_category = 'night'
        
        # Combine user preferences with time-based predictions
        predicted_apps = profile.preferred_applications[:3]  # Top 3 user apps
        predicted_apps.extend(time_apps.get(time_category, [])[:2])  # Add 2 time-based apps
        
        return list(set(predicted_apps))  # Remove duplicates

class PreferenceLearner:
    """Learns user preferences through implicit and explicit feedback"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Learning parameters
        self.learning_rate = 0.1
        self.feedback_weight = 0.3
        self.implicit_weight = 0.7
        
    async def learn(self, user_actions: List[Dict[str, Any]], 
                   network_states: List[Dict[str, Any]], 
                   satisfaction_indicators: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Learn preferences from user actions and feedback"""
        try:
            preferences = {
                'optimization_preferences': {},
                'quality_preferences': {},
                'automation_preferences': {},
                'application_preferences': {}
            }
            
            # Learn from user actions
            action_preferences = await self._learn_from_actions(user_actions)
            preferences['optimization_preferences'].update(action_preferences)
            
            # Learn from satisfaction indicators
            satisfaction_preferences = await self._learn_from_satisfaction(
                satisfaction_indicators, network_states
            )
            preferences['quality_preferences'].update(satisfaction_preferences)
            
            # Learn automation preferences
            automation_preferences = await self._learn_automation_preferences(
                user_actions
            )
            preferences['automation_preferences'].update(automation_preferences)
            
            return preferences
            
        except Exception as e:
            self.logger.error(f"Preference learning failed: {e}")
            return {'error': str(e)}
    
    async def _learn_from_actions(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Learn preferences from user actions"""
        action_patterns = defaultdict(int)
        
        for action in actions:
            action_type = action.get('type', 'unknown')
            action_patterns[action_type] += 1
        
        # Find most common action types
        total_actions = sum(action_patterns.values())
        if total_actions == 0:
            return {}
        
        preferences = {}
        for action_type, count in action_patterns.items():
            preference_strength = count / total_actions
            if preference_strength > 0.2:  # Significant preference
                preferences[f'prefers_{action_type}'] = preference_strength
        
        return preferences
    
    async def _learn_from_satisfaction(self, satisfaction_indicators: List[Dict[str, Any]], 
                                      network_states: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Learn quality preferences from satisfaction feedback"""
        if not satisfaction_indicators or not network_states:
            return {}
        
        # Analyze when user is most/least satisfied
        high_satisfaction_states = []
        low_satisfaction_states = []
        
        for i, indicator in enumerate(satisfaction_indicators):
            satisfaction = indicator.get('satisfaction_score', 0.5)
            if i < len(network_states):
                if satisfaction > 0.7:
                    high_satisfaction_states.append(network_states[i])
                elif satisfaction < 0.3:
                    low_satisfaction_states.append(network_states[i])
        
        preferences = {}
        
        # Learn latency preference
        if high_satisfaction_states:
            avg_good_latency = np.mean([s.get('latency', 100) for s in high_satisfaction_states])
            preferences['preferred_max_latency'] = avg_good_latency * 1.2  # Allow 20% buffer
        
        # Learn bandwidth preference
        if high_satisfaction_states:
            avg_good_bandwidth = np.mean([s.get('bandwidth', 10) for s in high_satisfaction_states])
            preferences['preferred_min_bandwidth'] = avg_good_bandwidth * 0.8  # 80% of good bandwidth
        
        return preferences
    
    async def _learn_automation_preferences(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Learn user's automation preferences"""
        manual_actions = len([a for a in actions if a.get('type') == 'manual_override'])
        auto_accepts = len([a for a in actions if a.get('type') == 'accept_ai_suggestion'])
        total_decisions = manual_actions + auto_accepts
        
        if total_decisions == 0:
            return {'automation_acceptance': 0.7}  # Default moderate acceptance
        
        automation_acceptance = auto_accepts / total_decisions
        
        return {
            'automation_acceptance': automation_acceptance,
            'prefers_manual_control': automation_acceptance < 0.3,
            'trusts_ai_decisions': automation_acceptance > 0.8
        }

class UserProfiler:
    """Main user profiling and personalization system"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core components
        self.behavior_analyzer = BehaviorAnalyzer(config)
        self.usage_predictor = UsagePredictor(config)
        self.preference_learner = PreferenceLearner(config)
        
        # Data storage
        self.user_storage = UserDataStorage(config)
        
        # In-memory user profiles
        self.user_profiles: Dict[str, UserProfile] = {}
        self.session_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
    async def initialize(self):
        """Initialize the user profiler"""
        self.logger.info("Initializing UserProfiler...")
        
        try:
            await self.user_storage.initialize()
            await self._load_existing_profiles()
            
            self.logger.info(f"UserProfiler initialized with {len(self.user_profiles)} existing profiles")
        except Exception as e:
            self.logger.error(f"Failed to initialize UserProfiler: {e}")
            raise
    
    async def _load_existing_profiles(self):
        """Load existing user profiles from storage"""
        try:
            existing_profiles = await self.user_storage.get_all_user_profiles()
            
            for profile_data in existing_profiles:
                user_id = profile_data.get('user_id')
                if user_id:
                    # Convert stored data back to UserProfile object
                    profile = self._dict_to_profile(profile_data)
                    self.user_profiles[user_id] = profile
            
            self.logger.info(f"Loaded {len(existing_profiles)} user profiles")
            
        except Exception as e:
            self.logger.error(f"Failed to load existing profiles: {e}")
    
    def _dict_to_profile(self, data: Dict[str, Any]) -> UserProfile:
        """Convert dictionary to UserProfile object"""
        # Handle datetime conversion
        created_at = datetime.fromisoformat(data.get('created_at', datetime.utcnow().isoformat()))
        last_updated = datetime.fromisoformat(data.get('last_updated', datetime.utcnow().isoformat()))
        
        return UserProfile(
            user_id=data.get('user_id', ''),
            created_at=created_at,
            last_updated=last_updated,
            total_sessions=data.get('total_sessions', 0),
            typical_usage_hours=data.get('typical_usage_hours', []),
            avg_session_duration=data.get('avg_session_duration', 60.0),
            avg_daily_data_gb=data.get('avg_daily_data_gb', 1.0),
            preferred_applications=data.get('preferred_applications', []),
            connection_preferences=data.get('connection_preferences', {}),
            latency_sensitivity=data.get('latency_sensitivity', 0.5),
            bandwidth_priority=data.get('bandwidth_priority', 0.5),
            reliability_importance=data.get('reliability_importance', 0.7),
            cost_consciousness=data.get('cost_consciousness', 0.5),
            optimization_acceptance=data.get('optimization_acceptance', 0.7),
            manual_override_frequency=data.get('manual_override_frequency', 0.3),
            feedback_responsiveness=data.get('feedback_responsiveness', 0.8),
            automation_level=data.get('automation_level', 0.7),
            notification_preferences=data.get('notification_preferences', {}),
            customization_preferences=data.get('customization_preferences', {}),
            user_cluster=data.get('user_cluster'),
            behavior_model=data.get('behavior_model'),
            confidence_score=data.get('confidence_score', 0.0)
        )
    
    async def build_user_profile(self, user_id: str, 
                                historical_data: List[Dict[str, Any]]) -> UserProfile:
        """Build comprehensive user behavior profile"""
        try:
            # Convert historical data to usage sessions
            sessions = [self._dict_to_session(data) for data in historical_data]
            
            # Analyze usage patterns
            usage_patterns = await self.behavior_analyzer.analyze(
                data=sessions,
                features=[
                    'duration_minutes', 'total_data_mb', 'applications_used',
                    'connection_type', 'quality_metrics', 'user_satisfaction'
                ]
            )
            
            # Learn preferences through implicit feedback
            user_actions = historical_data  # Simplified - would extract actual actions
            network_states = [data.get('network_state', {}) for data in historical_data]
            satisfaction_indicators = [data.get('satisfaction', {}) for data in historical_data]
            
            preferences = await self.preference_learner.learn(
                user_actions=user_actions,
                network_states=network_states,
                satisfaction_indicators=satisfaction_indicators
            )
            
            # Create user profile
            profile = UserProfile(
                user_id=user_id,
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                total_sessions=len(sessions),
                typical_usage_hours=self._extract_typical_hours(sessions),
                avg_session_duration=float(np.mean([s.duration_minutes for s in sessions])) if sessions else 60.0,
                avg_daily_data_gb=self._calculate_daily_data_usage(sessions),
                preferred_applications=self._extract_preferred_apps(sessions),
                connection_preferences=self._extract_connection_preferences(sessions),
                latency_sensitivity=preferences.get('quality_preferences', {}).get('latency_sensitivity', 0.5),
                bandwidth_priority=preferences.get('quality_preferences', {}).get('bandwidth_priority', 0.5),
                reliability_importance=preferences.get('quality_preferences', {}).get('reliability_importance', 0.7),
                cost_consciousness=0.5,  # Would be learned from user behavior
                optimization_acceptance=preferences.get('automation_preferences', {}).get('automation_acceptance', 0.7),
                manual_override_frequency=preferences.get('automation_preferences', {}).get('manual_override_frequency', 0.3),
                feedback_responsiveness=0.8,  # Default
                automation_level=preferences.get('automation_preferences', {}).get('automation_acceptance', 0.7),
                notification_preferences={'optimization_complete': True, 'security_alerts': True},
                customization_preferences={},
                user_cluster=usage_patterns.get('cluster_analysis', {}).get('primary_cluster'),
                confidence_score=usage_patterns.get('analysis_confidence', 0.5)
            )
            
            # Store profile
            self.user_profiles[user_id] = profile
            await self.user_storage.store_user_profile(profile.to_dict())
            
            self.logger.info(f"Built user profile for {user_id} with {len(sessions)} sessions")
            
            return profile
            
        except Exception as e:
            self.logger.error(f"User profile building failed for {user_id}: {e}")
            raise
    
    def _dict_to_session(self, data: Dict[str, Any]) -> UsageSession:
        """Convert dictionary to UsageSession object"""
        return UsageSession(
            session_id=data.get('session_id', str(datetime.utcnow().timestamp())),
            user_id=data.get('user_id', ''),
            start_time=datetime.fromisoformat(data.get('start_time', datetime.utcnow().isoformat())),
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            duration_minutes=data.get('duration_minutes', 60.0),
            total_data_mb=data.get('total_data_mb', 100.0),
            avg_bandwidth_mbps=data.get('avg_bandwidth_mbps', 10.0),
            peak_bandwidth_mbps=data.get('peak_bandwidth_mbps', 20.0),
            applications_used=data.get('applications_used', []),
            connection_type=data.get('connection_type', 'wifi'),
            location_context=data.get('location_context'),
            quality_metrics=data.get('quality_metrics', {}),
            user_satisfaction=data.get('user_satisfaction')
        )
    
    def _extract_typical_hours(self, sessions: List[UsageSession]) -> List[int]:
        """Extract typical usage hours from sessions"""
        if not sessions:
            return []
        
        hour_counts = defaultdict(int)
        for session in sessions:
            hour_counts[session.start_time.hour] += 1
        
        # Get hours with above-average usage
        avg_usage = sum(hour_counts.values()) / 24  # Average per hour
        typical_hours = [hour for hour, count in hour_counts.items() if count > avg_usage]
        
        return sorted(typical_hours)
    
    def _calculate_daily_data_usage(self, sessions: List[UsageSession]) -> float:
        """Calculate average daily data usage"""
        if not sessions:
            return 1.0
        
        # Group sessions by date
        daily_usage = defaultdict(float)
        for session in sessions:
            date_key = session.start_time.date()
            daily_usage[date_key] += session.total_data_mb
        
        # Convert to GB and return average
        daily_gb_values = [mb / 1024 for mb in daily_usage.values()]
        return float(np.mean(daily_gb_values)) if daily_gb_values else 1.0
    
    def _extract_preferred_apps(self, sessions: List[UsageSession]) -> List[str]:
        """Extract user's preferred applications"""
        app_counts = defaultdict(int)
        
        for session in sessions:
            for app in session.applications_used:
                app_counts[app] += 1
        
        # Sort by frequency and return top 5
        sorted_apps = sorted(app_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return [app for app, _ in sorted_apps]
    
    def _extract_connection_preferences(self, sessions: List[UsageSession]) -> Dict[str, float]:
        """Extract connection type preferences"""
        connection_counts = defaultdict(int)
        
        for session in sessions:
            connection_counts[session.connection_type] += 1
        
        total_sessions = len(sessions)
        if total_sessions == 0:
            return {}
        
        return {conn_type: count / total_sessions 
                for conn_type, count in connection_counts.items()}
    
    async def predict_user_needs(self, user_id: str, 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict user needs based on profile and context"""
        try:
            if user_id not in self.user_profiles:
                return {'error': f'No profile found for user {user_id}'}
            
            profile = self.user_profiles[user_id]
            predicted_needs = await self.usage_predictor.predict(profile, context)
            
            return predicted_needs
            
        except Exception as e:
            self.logger.error(f"User need prediction failed for {user_id}: {e}")
            return {'error': str(e)}
    
    async def get_patterns(self, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get user patterns for current context"""
        try:
            if not user_context or 'user_id' not in user_context:
                # Return aggregate patterns across all users
                return await self._get_aggregate_patterns()
            
            user_id = user_context['user_id']
            
            if user_id in self.user_profiles:
                profile = self.user_profiles[user_id]
                
                # Get current predictions
                current_predictions = await self.usage_predictor.predict(
                    profile, user_context
                )
                
                return {
                    'user_profile': profile.to_dict(),
                    'current_predictions': current_predictions,
                    'personalization_active': True
                }
            else:
                return {'error': f'No patterns found for user {user_id}'}
                
        except Exception as e:
            self.logger.error(f"Pattern retrieval failed: {e}")
            return {'error': str(e)}
    
    async def _get_aggregate_patterns(self) -> Dict[str, Any]:
        """Get aggregate patterns across all users"""
        if not self.user_profiles:
            return {
                'predicted_usage': 10.0,  # Default 10 Mbps
                'quality_preference': 0.5,
                'cost_sensitivity': 0.5,
                'users_analyzed': 0
            }
        
        profiles = list(self.user_profiles.values())
        
        return {
            'predicted_usage': float(np.mean([p.avg_daily_data_gb for p in profiles])),
            'quality_preference': float(np.mean([p.latency_sensitivity for p in profiles])),
            'cost_sensitivity': float(np.mean([p.cost_consciousness for p in profiles])),
            'automation_acceptance': float(np.mean([p.automation_level for p in profiles])),
            'users_analyzed': len(profiles)
        }
    
    async def update_user_feedback(self, user_id: str, 
                                  feedback: Dict[str, Any]):
        """Update user profile based on feedback"""
        try:
            if user_id not in self.user_profiles:
                self.logger.warning(f"No profile found for user {user_id}, creating new one")
                await self.build_user_profile(user_id, [])
            
            profile = self.user_profiles[user_id]
            
            # Update based on feedback type
            feedback_type = feedback.get('type')
            
            if feedback_type == 'satisfaction':
                satisfaction = feedback.get('score', 0.5)
                # Update preferences based on satisfaction feedback
                # This would be more sophisticated in production
                
            elif feedback_type == 'manual_override':
                # User manually overrode AI decision
                profile.manual_override_frequency = min(1.0, profile.manual_override_frequency + 0.1)
                profile.automation_level = max(0.0, profile.automation_level - 0.05)
                
            elif feedback_type == 'accept_suggestion':
                # User accepted AI suggestion
                profile.optimization_acceptance = min(1.0, profile.optimization_acceptance + 0.05)
                profile.automation_level = min(1.0, profile.automation_level + 0.02)
            
            profile.last_updated = datetime.utcnow()
            
            # Save updated profile
            await self.user_storage.store_user_profile(profile.to_dict())
            
            self.logger.info(f"Updated user profile for {user_id} based on {feedback_type} feedback")
            
        except Exception as e:
            self.logger.error(f"User feedback update failed for {user_id}: {e}")
    
    async def get_personalization_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about user personalization"""
        try:
            if user_id not in self.user_profiles:
                return {'error': f'No profile found for user {user_id}'}
            
            profile = self.user_profiles[user_id]
            
            insights = {
                'profile_maturity': self._calculate_profile_maturity(profile),
                'personalization_opportunities': self._identify_personalization_opportunities(profile),
                'optimization_recommendations': await self._generate_optimization_recommendations(profile),
                'learning_status': {
                    'confidence_level': profile.confidence_score,
                    'sessions_analyzed': profile.total_sessions,
                    'automation_adoption': profile.automation_level,
                    'feedback_responsiveness': profile.feedback_responsiveness
                }
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Personalization insights failed for {user_id}: {e}")
            return {'error': str(e)}
    
    def _calculate_profile_maturity(self, profile: UserProfile) -> str:
        """Calculate how mature/complete the user profile is"""
        maturity_score = 0.0
        
        # Sessions factor
        session_score = min(1.0, profile.total_sessions / 50.0)  # Mature at 50+ sessions
        maturity_score += session_score * 0.3
        
        # Time factor
        days_since_creation = (datetime.utcnow() - profile.created_at).days
        time_score = min(1.0, days_since_creation / 30.0)  # Mature after 30 days
        maturity_score += time_score * 0.2
        
        # Data completeness factor
        completeness_score = profile.confidence_score
        maturity_score += completeness_score * 0.5
        
        if maturity_score >= 0.8:
            return 'mature'
        elif maturity_score >= 0.5:
            return 'developing'
        else:
            return 'new'
    
    def _identify_personalization_opportunities(self, profile: UserProfile) -> List[str]:
        """Identify opportunities for better personalization"""
        opportunities = []
        
        if profile.automation_level < 0.5:
            opportunities.append("Increase automation based on usage patterns")
        
        if profile.latency_sensitivity > 0.8 and 'video' in profile.preferred_applications:
            opportunities.append("Implement ultra-low latency mode for video applications")
        
        if profile.cost_consciousness > 0.7:
            opportunities.append("Enable data conservation features")
        
        if len(profile.preferred_applications) > 0:
            opportunities.append(f"Create custom optimization profile for {profile.preferred_applications[0]} usage")
        
        return opportunities
    
    async def _generate_optimization_recommendations(self, profile: UserProfile) -> List[str]:
        """Generate personalized optimization recommendations"""
        recommendations = []
        
        # Based on usage patterns
        if len(profile.typical_usage_hours) > 0:
            peak_hour = profile.typical_usage_hours[0]
            recommendations.append(
                f"Schedule automatic optimization for {peak_hour}:00 (your peak usage time)"
            )
        
        # Based on application preferences
        if 'gaming' in profile.preferred_applications:
            recommendations.append("Enable gaming optimization mode for reduced latency")
        elif 'streaming' in profile.preferred_applications:
            recommendations.append("Enable streaming optimization for consistent bandwidth")
        
        # Based on quality sensitivity
        if profile.latency_sensitivity > 0.8:
            recommendations.append("Configure ultra-low latency routing for your latency-sensitive usage")
        
        if profile.reliability_importance > 0.8:
            recommendations.append("Enable redundant connection monitoring for high reliability")
        
        return recommendations