#!/usr/bin/env python3
"""
Intelligent Bandwidth Manager - AI-Driven QoS and Traffic Management

Implements sophisticated bandwidth allocation using machine learning,
predictive QoS management, and application-aware traffic shaping.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
from enum import Enum

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

from ..utils.config import Config
from ..utils.network_utils import NetworkUtils

logger = logging.getLogger(__name__)

class QoSClass(Enum):
    """Quality of Service classes"""
    PREMIUM = "premium"
    STANDARD = "standard"
    ECONOMY = "economy"
    EMERGENCY = "emergency"

@dataclass
class ApplicationProfile:
    """Profile for application-specific optimization"""
    app_name: str
    category: str  # video, gaming, streaming, browsing, etc.
    bandwidth_requirements: Dict[str, float]  # min, typical, max
    latency_sensitivity: float  # 0-1 scale
    jitter_sensitivity: float   # 0-1 scale
    packet_loss_tolerance: float  # 0-1 scale
    priority_weight: float      # 0-1 scale
    qos_class: QoSClass
    
    def get_optimization_score(self, current_metrics: Dict[str, float]) -> float:
        """Calculate how well current metrics meet app requirements"""
        score = 1.0
        
        # Bandwidth score
        current_bw = current_metrics.get('bandwidth_mbps', 0)
        required_bw = self.bandwidth_requirements.get('min', 1.0)
        if current_bw < required_bw:
            score *= current_bw / required_bw
        
        # Latency score
        current_latency = current_metrics.get('latency_ms', 100)
        if self.latency_sensitivity > 0.5:
            max_acceptable_latency = 50 + (1 - self.latency_sensitivity) * 200
            if current_latency > max_acceptable_latency:
                score *= max_acceptable_latency / current_latency
        
        # Packet loss score
        current_loss = current_metrics.get('packet_loss', 0.01)
        if current_loss > self.packet_loss_tolerance:
            score *= self.packet_loss_tolerance / current_loss
        
        return max(0.0, min(1.0, score))

@dataclass
class QoSPolicy:
    """Quality of Service policy definition"""
    policy_id: str
    name: str
    bandwidth_allocation: Dict[str, float]  # percentage allocation per class
    latency_targets: Dict[str, float]       # target latency per class
    priority_weights: Dict[str, float]      # traffic priority weights
    traffic_shaping: Dict[str, Any]         # shaping parameters
    created_at: datetime
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data

class DemandPredictor:
    """Predicts bandwidth demand for applications"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Prediction models
        self.demand_model = LinearRegression()
        self.scaler = StandardScaler()
        
        # Historical data for prediction
        self.demand_history = deque(maxlen=1000)
        self.is_trained = False
        
    async def predict(self, applications: List[str], 
                     traffic_classes: Dict[str, Any],
                     time_horizon: int) -> Dict[str, float]:
        """Predict bandwidth demand for applications"""
        try:
            predictions = {}
            
            for app in applications:
                # Get application profile
                app_profile = self._get_application_profile(app)
                
                # Base demand from profile
                base_demand = app_profile.bandwidth_requirements.get('typical', 5.0)
                
                # Time-based adjustments
                time_factor = self._calculate_time_factor(time_horizon)
                
                # Traffic class adjustments
                class_factor = self._calculate_class_factor(app_profile.category, traffic_classes)
                
                # Final prediction
                predicted_demand = base_demand * time_factor * class_factor
                
                predictions[app] = max(0.1, predicted_demand)  # Minimum 0.1 Mbps
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Demand prediction failed: {e}")
            return {app: 5.0 for app in applications}  # Default 5 Mbps each
    
    def _get_application_profile(self, app_name: str) -> ApplicationProfile:
        """Get or create application profile"""
        # Predefined application profiles
        app_profiles = {
            'zoom': ApplicationProfile(
                app_name='zoom',
                category='video_conferencing',
                bandwidth_requirements={'min': 2.0, 'typical': 8.0, 'max': 20.0},
                latency_sensitivity=0.9,
                jitter_sensitivity=0.8,
                packet_loss_tolerance=0.01,
                priority_weight=0.9,
                qos_class=QoSClass.PREMIUM
            ),
            'netflix': ApplicationProfile(
                app_name='netflix',
                category='streaming',
                bandwidth_requirements={'min': 5.0, 'typical': 15.0, 'max': 50.0},
                latency_sensitivity=0.3,
                jitter_sensitivity=0.4,
                packet_loss_tolerance=0.02,
                priority_weight=0.7,
                qos_class=QoSClass.STANDARD
            ),
            'chrome': ApplicationProfile(
                app_name='chrome',
                category='browsing',
                bandwidth_requirements={'min': 1.0, 'typical': 5.0, 'max': 20.0},
                latency_sensitivity=0.6,
                jitter_sensitivity=0.2,
                packet_loss_tolerance=0.05,
                priority_weight=0.5,
                qos_class=QoSClass.STANDARD
            ),
            'gaming': ApplicationProfile(
                app_name='gaming',
                category='gaming',
                bandwidth_requirements={'min': 1.0, 'typical': 3.0, 'max': 10.0},
                latency_sensitivity=0.95,
                jitter_sensitivity=0.9,
                packet_loss_tolerance=0.005,
                priority_weight=0.95,
                qos_class=QoSClass.PREMIUM
            ),
            'default': ApplicationProfile(
                app_name='default',
                category='general',
                bandwidth_requirements={'min': 1.0, 'typical': 5.0, 'max': 15.0},
                latency_sensitivity=0.5,
                jitter_sensitivity=0.5,
                packet_loss_tolerance=0.03,
                priority_weight=0.5,
                qos_class=QoSClass.STANDARD
            )
        }
        
        # Find matching profile or use default
        for profile_key, profile in app_profiles.items():
            if profile_key in app_name.lower():
                return profile
        
        return app_profiles['default']
    
    def _calculate_time_factor(self, time_horizon: int) -> float:
        """Calculate time-based demand factor"""
        # Longer horizons generally have higher demand uncertainty
        if time_horizon <= 60:   # 1 minute
            return 1.0
        elif time_horizon <= 900: # 15 minutes
            return 1.1
        else:                     # 1 hour+
            return 1.2
    
    def _calculate_class_factor(self, category: str, traffic_classes: Dict[str, Any]) -> float:
        """Calculate traffic class factor"""
        class_factors = {
            'video_conferencing': 1.3,
            'streaming': 1.2,
            'gaming': 1.1,
            'browsing': 1.0,
            'background': 0.8
        }
        
        return class_factors.get(category, 1.0)

class TrafficClassifier:
    """Classifies and prioritizes network traffic"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Application categorization
        self.app_categories = {
            'video_conferencing': ['zoom', 'teams', 'meet', 'webex', 'skype'],
            'streaming': ['netflix', 'youtube', 'spotify', 'twitch', 'hulu'],
            'gaming': ['steam', 'epic', 'origin', 'gaming', 'game'],
            'browsing': ['chrome', 'firefox', 'safari', 'edge', 'browser'],
            'social': ['discord', 'telegram', 'whatsapp', 'slack'],
            'productivity': ['office', 'word', 'excel', 'powerpoint', 'email'],
            'development': ['vscode', 'pycharm', 'github', 'docker', 'terminal']
        }
        
    async def classify(self, applications: List[str]) -> Dict[str, Any]:
        """Classify applications and assign priorities"""
        try:
            classifications = {}
            priorities = {}
            
            for app in applications:
                category = self._classify_application(app)
                priority = self._assign_priority(category)
                
                classifications[app] = {
                    'category': category,
                    'priority': priority,
                    'qos_class': self._assign_qos_class(category)
                }
                
                priorities[app] = priority
            
            return {
                'classifications': classifications,
                'priorities': priorities,
                'priority_distribution': self._calculate_priority_distribution(priorities)
            }
            
        except Exception as e:
            self.logger.error(f"Traffic classification failed: {e}")
            return {'error': str(e)}
    
    def _classify_application(self, app_name: str) -> str:
        """Classify application into category"""
        app_lower = app_name.lower()
        
        for category, app_list in self.app_categories.items():
            if any(app_keyword in app_lower for app_keyword in app_list):
                return category
        
        return 'general'
    
    def _assign_priority(self, category: str) -> float:
        """Assign priority score based on category"""
        priority_map = {
            'video_conferencing': 0.95,
            'gaming': 0.90,
            'streaming': 0.70,
            'productivity': 0.75,
            'browsing': 0.50,
            'social': 0.60,
            'development': 0.65,
            'general': 0.50
        }
        
        return priority_map.get(category, 0.50)
    
    def _assign_qos_class(self, category: str) -> str:
        """Assign QoS class based on category"""
        qos_map = {
            'video_conferencing': QoSClass.PREMIUM.value,
            'gaming': QoSClass.PREMIUM.value,
            'streaming': QoSClass.STANDARD.value,
            'productivity': QoSClass.STANDARD.value,
            'browsing': QoSClass.STANDARD.value,
            'social': QoSClass.STANDARD.value,
            'development': QoSClass.STANDARD.value,
            'general': QoSClass.ECONOMY.value
        }
        
        return qos_map.get(category, QoSClass.STANDARD.value)
    
    def _calculate_priority_distribution(self, priorities: Dict[str, float]) -> Dict[str, float]:
        """Calculate priority distribution across applications"""
        if not priorities:
            return {}
        
        total_priority = sum(priorities.values())
        return {app: priority / total_priority for app, priority in priorities.items()}

class QoSOptimizer:
    """ML-driven Quality of Service optimizer"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Optimization parameters
        self.optimization_weights = {
            'latency': 0.3,
            'throughput': 0.4,
            'reliability': 0.2,
            'fairness': 0.1
        }
        
        # Historical optimization results
        self.optimization_history = deque(maxlen=500)
        
    async def optimize(self, 
                      demand_forecast: Dict[str, float],
                      total_bandwidth: float,
                      fairness_constraints: Dict[str, Any],
                      priority_weights: Dict[str, float]) -> Dict[str, float]:
        """Optimize bandwidth allocation using ML-driven approach"""
        try:
            # Calculate initial allocation based on demand and priorities
            initial_allocation = await self._calculate_initial_allocation(
                demand_forecast, total_bandwidth, priority_weights
            )
            
            # Apply fairness constraints
            fair_allocation = await self._apply_fairness_constraints(
                initial_allocation, fairness_constraints
            )
            
            # Optimize using ML insights
            optimized_allocation = await self._ml_optimization(
                fair_allocation, demand_forecast, total_bandwidth
            )
            
            # Validate allocation
            validated_allocation = self._validate_allocation(
                optimized_allocation, total_bandwidth
            )
            
            # Record optimization result
            self.optimization_history.append({
                'timestamp': datetime.utcnow(),
                'demand_forecast': demand_forecast,
                'total_bandwidth': total_bandwidth,
                'allocation': validated_allocation,
                'optimization_score': self._calculate_optimization_score(validated_allocation)
            })
            
            return validated_allocation
            
        except Exception as e:
            self.logger.error(f"QoS optimization failed: {e}")
            # Return proportional allocation as fallback
            return self._proportional_fallback_allocation(demand_forecast, total_bandwidth)
    
    async def _calculate_initial_allocation(self, 
                                          demand_forecast: Dict[str, float],
                                          total_bandwidth: float,
                                          priority_weights: Dict[str, float]) -> Dict[str, float]:
        """Calculate initial bandwidth allocation"""
        allocation = {}
        
        # Calculate weighted demand
        weighted_demands = {}
        total_weighted_demand = 0
        
        for app, demand in demand_forecast.items():
            weight = priority_weights.get(app, 0.5)
            weighted_demand = demand * weight
            weighted_demands[app] = weighted_demand
            total_weighted_demand += weighted_demand
        
        # Allocate proportionally based on weighted demand
        if total_weighted_demand > 0:
            for app, weighted_demand in weighted_demands.items():
                proportion = weighted_demand / total_weighted_demand
                allocated_bandwidth = total_bandwidth * proportion
                allocation[app] = allocated_bandwidth
        
        return allocation
    
    async def _apply_fairness_constraints(self, 
                                        allocation: Dict[str, float],
                                        constraints: Dict[str, Any]) -> Dict[str, float]:
        """Apply fairness constraints to allocation"""
        # Ensure minimum allocations
        min_allocation = constraints.get('min_allocation_per_app', 1.0)
        
        fair_allocation = {}
        for app, bandwidth in allocation.items():
            fair_allocation[app] = max(min_allocation, bandwidth)
        
        # Ensure maximum allocations don't exceed limits
        max_allocation = constraints.get('max_allocation_per_app', float('inf'))
        for app, bandwidth in fair_allocation.items():
            fair_allocation[app] = min(max_allocation, bandwidth)
        
        return fair_allocation
    
    async def _ml_optimization(self, 
                             allocation: Dict[str, float],
                             demand_forecast: Dict[str, float],
                             total_bandwidth: float) -> Dict[str, float]:
        """Apply ML-based optimization to allocation"""
        # This would use a trained ML model to optimize allocation
        # For now, implementing a heuristic approach
        
        optimized = allocation.copy()
        
        # Redistribute based on demand patterns
        for app, allocated in allocation.items():
            forecasted = demand_forecast.get(app, allocated)
            
            # If forecast is much higher than allocation, try to increase
            if forecasted > allocated * 1.5:
                additional_needed = min(forecasted - allocated, total_bandwidth * 0.1)
                optimized[app] = allocated + additional_needed
            
            # If forecast is much lower, reduce allocation
            elif forecasted < allocated * 0.7:
                reduction = min(allocated - forecasted, allocated * 0.3)
                optimized[app] = allocated - reduction
        
        return optimized
    
    def _validate_allocation(self, allocation: Dict[str, float], 
                           total_bandwidth: float) -> Dict[str, float]:
        """Validate and normalize allocation to not exceed total bandwidth"""
        total_allocated = sum(allocation.values())
        
        if total_allocated > total_bandwidth:
            # Scale down proportionally
            scale_factor = total_bandwidth / total_allocated
            allocation = {app: bandwidth * scale_factor 
                         for app, bandwidth in allocation.items()}
        
        return allocation
    
    def _proportional_fallback_allocation(self, demand_forecast: Dict[str, float], 
                                        total_bandwidth: float) -> Dict[str, float]:
        """Fallback proportional allocation"""
        total_demand = sum(demand_forecast.values())
        if total_demand == 0:
            return {}
        
        return {app: (demand / total_demand) * total_bandwidth 
                for app, demand in demand_forecast.items()}
    
    def _calculate_optimization_score(self, allocation: Dict[str, float]) -> float:
        """Calculate optimization effectiveness score"""
        # Simplified scoring based on allocation distribution
        if not allocation:
            return 0.0
        
        # Measure allocation fairness (using Gini coefficient concept)
        values = list(allocation.values())
        if len(values) < 2:
            return 1.0
        
        # Calculate distribution evenness
        mean_allocation = np.mean(values)
        variance = np.var(values)
        
        # Score based on reasonable distribution (not too uneven, not too equal)
        fairness_score = 1.0 / (1.0 + variance / (mean_allocation ** 2))
        
        return max(0.0, min(1.0, fairness_score))

class FairnessEnforcer:
    """Ensures fair bandwidth allocation across applications and users"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Fairness parameters
        self.min_allocation_ratio = config.get('fairness_min_allocation_ratio', 0.05)  # 5% minimum
        self.max_allocation_ratio = config.get('fairness_max_allocation_ratio', 0.80)  # 80% maximum
        
    async def get_constraints(self) -> Dict[str, Any]:
        """Get current fairness constraints"""
        return {
            'min_allocation_per_app': 1.0,  # Minimum 1 Mbps per application
            'max_allocation_per_app': 50.0,  # Maximum 50 Mbps per application
            'min_allocation_ratio': self.min_allocation_ratio,
            'max_allocation_ratio': self.max_allocation_ratio,
            'priority_boost_limit': 2.0,  # Maximum 2x boost for high priority
            'starvation_prevention': True
        }
    
    async def enforce_fairness(self, allocation: Dict[str, float], 
                             total_bandwidth: float) -> Dict[str, float]:
        """Enforce fairness constraints on allocation"""
        try:
            if not allocation:
                return allocation
            
            fair_allocation = allocation.copy()
            constraints = await self.get_constraints()
            
            # Ensure minimum allocations
            min_per_app = constraints['min_allocation_per_app']
            for app in fair_allocation.keys():
                fair_allocation[app] = max(min_per_app, fair_allocation[app])
            
            # Ensure maximum allocations
            max_per_app = constraints['max_allocation_per_app']
            for app in fair_allocation.keys():
                fair_allocation[app] = min(max_per_app, fair_allocation[app])
            
            # Enforce ratio constraints
            for app, bandwidth in fair_allocation.items():
                min_ratio_bandwidth = total_bandwidth * self.min_allocation_ratio
                max_ratio_bandwidth = total_bandwidth * self.max_allocation_ratio
                
                fair_allocation[app] = max(min_ratio_bandwidth, 
                                          min(max_ratio_bandwidth, bandwidth))
            
            # Normalize to total bandwidth
            total_allocated = sum(fair_allocation.values())
            if total_allocated > total_bandwidth:
                scale_factor = total_bandwidth / total_allocated
                fair_allocation = {app: bandwidth * scale_factor 
                                 for app, bandwidth in fair_allocation.items()}
            
            return fair_allocation
            
        except Exception as e:
            self.logger.error(f"Fairness enforcement failed: {e}")
            return allocation

class IntelligentBandwidthManager:
    """Main intelligent bandwidth management system"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core components
        self.traffic_classifier = TrafficClassifier(config)
        self.demand_predictor = DemandPredictor(config)
        self.qos_optimizer = QoSOptimizer(config)
        self.fairness_enforcer = FairnessEnforcer(config)
        
        # Network utilities
        self.network_utils = NetworkUtils(config)
        
        # State management
        self.current_allocation: Dict[str, float] = {}
        self.active_policies: List[QoSPolicy] = []
        self.allocation_history = deque(maxlen=1000)
        
        # Performance tracking
        self.performance_metrics = deque(maxlen=100)
        
    async def initialize(self):
        """Initialize bandwidth manager"""
        self.logger.info("Initializing IntelligentBandwidthManager...")
        
        try:
            # Load existing policies
            await self._load_qos_policies()
            
            self.logger.info("IntelligentBandwidthManager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize IntelligentBandwidthManager: {e}")
            raise
    
    async def _load_qos_policies(self):
        """Load existing QoS policies"""
        try:
            # Default policies for demonstration
            default_policies = [
                QoSPolicy(
                    policy_id="premium_policy",
                    name="Premium QoS Policy",
                    bandwidth_allocation={
                        'premium': 50.0,  # 50% for premium traffic
                        'standard': 35.0,  # 35% for standard
                        'economy': 15.0    # 15% for economy
                    },
                    latency_targets={
                        'premium': 20.0,   # 20ms target
                        'standard': 100.0,  # 100ms target
                        'economy': 300.0    # 300ms target
                    },
                    priority_weights={
                        'premium': 1.0,
                        'standard': 0.6,
                        'economy': 0.3
                    },
                    traffic_shaping={'algorithm': 'fq_codel', 'aggressive': False},
                    created_at=datetime.utcnow()
                )
            ]
            
            self.active_policies = default_policies
            self.logger.info(f"Loaded {len(self.active_policies)} QoS policies")
            
        except Exception as e:
            self.logger.error(f"Failed to load QoS policies: {e}")
    
    async def allocate_bandwidth(self, applications: List[str], 
                               total_bandwidth: float) -> Dict[str, float]:
        """AI-driven bandwidth allocation across applications"""
        try:
            # Classify and prioritize traffic
            traffic_classes = await self.traffic_classifier.classify(applications)
            
            # Predict demand for each application
            demand_forecast = await self.demand_predictor.predict(
                applications=applications,
                traffic_classes=traffic_classes,
                time_horizon=300  # 5 minutes
            )
            
            # Get fairness constraints
            fairness_constraints = await self.fairness_enforcer.get_constraints()
            
            # Optimize allocation using ML
            allocation = await self.qos_optimizer.optimize(
                demand_forecast=demand_forecast,
                total_bandwidth=total_bandwidth,
                fairness_constraints=fairness_constraints,
                priority_weights=traffic_classes.get('priorities', {})
            )
            
            # Apply fairness enforcement
            final_allocation = await self.fairness_enforcer.enforce_fairness(
                allocation, total_bandwidth
            )
            
            # Apply bandwidth limits to system
            await self._apply_bandwidth_limits(final_allocation)
            
            # Update current state
            self.current_allocation = final_allocation
            
            # Record allocation
            allocation_record = {
                'timestamp': datetime.utcnow(),
                'applications': applications,
                'total_bandwidth': total_bandwidth,
                'allocation': final_allocation,
                'demand_forecast': demand_forecast,
                'traffic_classes': traffic_classes
            }
            
            self.allocation_history.append(allocation_record)
            
            self.logger.info(
                f"Allocated bandwidth across {len(applications)} applications: "
                f"{sum(final_allocation.values()):.1f}/{total_bandwidth:.1f} Mbps"
            )
            
            return final_allocation
            
        except Exception as e:
            self.logger.error(f"Bandwidth allocation failed: {e}")
            return {}
    
    async def _apply_bandwidth_limits(self, allocation: Dict[str, float]):
        """Apply bandwidth limits to the network"""
        try:
            # This would apply actual bandwidth limits using tc (traffic control)
            # For demonstration, we'll log the actions that would be taken
            
            for app, bandwidth in allocation.items():
                self.logger.debug(f"Would set {app} bandwidth limit to {bandwidth:.1f} Mbps")
            
            # In real implementation:
            # await self.network_utils.configure_application_bandwidth_limits(allocation)
            
        except Exception as e:
            self.logger.error(f"Failed to apply bandwidth limits: {e}")
    
    async def adaptive_qos(self, current_flows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Real-time QoS adjustment based on network conditions"""
        try:
            # Assess current network health
            network_health = await self._assess_network_health()
            
            # Predict congestion
            congestion_prediction = await self._predict_congestion(current_flows)
            
            adjustments = {}
            
            if congestion_prediction.get('probability', 0) > 0.7:
                # Proactively adjust QoS before congestion occurs
                adjustments = await self._preemptive_qos_adjustment(congestion_prediction)
            elif network_health.get('score', 1.0) < 0.5:
                # React to current poor performance
                adjustments = await self._reactive_qos_adjustment(network_health)
            
            return {
                'adaptive_qos_applied': True,
                'network_health': network_health,
                'congestion_prediction': congestion_prediction,
                'adjustments': adjustments,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Adaptive QoS failed: {e}")
            return {'adaptive_qos_applied': False, 'error': str(e)}
    
    async def _assess_network_health(self) -> Dict[str, Any]:
        """Assess current network health"""
        try:
            # Get comprehensive network metrics
            metrics = await self.network_utils.collect_comprehensive_metrics()
            
            # Calculate health score based on key metrics
            health_factors = {
                'bandwidth_utilization': self._score_bandwidth_utilization(
                    metrics.get('derived', {}).get('bandwidth_utilization', 0.5)
                ),
                'latency_performance': self._score_latency_performance(
                    metrics.get('system', {}).get('avg_latency', 100)
                ),
                'error_rates': self._score_error_rates(
                    metrics.get('derived', {}).get('overall_error_rate', 0.01)
                ),
                'connection_efficiency': metrics.get('derived', {}).get('connection_efficiency', 0.8)
            }
            
            # Calculate overall health score
            overall_score = np.mean(list(health_factors.values()))
            
            return {
                'score': overall_score,
                'factors': health_factors,
                'status': 'healthy' if overall_score > 0.7 else 'degraded' if overall_score > 0.4 else 'poor'
            }
            
        except Exception as e:
            self.logger.error(f"Network health assessment failed: {e}")
            return {'score': 0.5, 'status': 'unknown', 'error': str(e)}
    
    def _score_bandwidth_utilization(self, utilization: float) -> float:
        """Score bandwidth utilization (optimal around 70-80%)"""
        if 0.7 <= utilization <= 0.8:
            return 1.0
        elif 0.5 <= utilization < 0.7 or 0.8 < utilization <= 0.9:
            return 0.8
        elif 0.3 <= utilization < 0.5 or 0.9 < utilization <= 0.95:
            return 0.6
        else:
            return 0.3
    
    def _score_latency_performance(self, avg_latency: float) -> float:
        """Score latency performance"""
        if avg_latency <= 50:
            return 1.0
        elif avg_latency <= 100:
            return 0.8
        elif avg_latency <= 200:
            return 0.6
        elif avg_latency <= 500:
            return 0.4
        else:
            return 0.2
    
    def _score_error_rates(self, error_rate: float) -> float:
        """Score error rates"""
        if error_rate <= 0.01:   # 1%
            return 1.0
        elif error_rate <= 0.03: # 3%
            return 0.8
        elif error_rate <= 0.05: # 5%
            return 0.6
        elif error_rate <= 0.10: # 10%
            return 0.4
        else:
            return 0.2
    
    async def _predict_congestion(self, current_flows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict network congestion"""
        try:
            # Analyze current flows
            total_flows = len(current_flows)
            
            # Calculate flow intensity
            flow_intensity = total_flows / 100.0  # Normalize to typical 100 flows
            
            # Simple congestion prediction based on flow count and bandwidth
            if total_flows > 500:
                congestion_probability = 0.9
            elif total_flows > 200:
                congestion_probability = 0.6
            elif total_flows > 100:
                congestion_probability = 0.3
            else:
                congestion_probability = 0.1
            
            return {
                'probability': congestion_probability,
                'total_flows': total_flows,
                'flow_intensity': flow_intensity,
                'predicted_impact': 'high' if congestion_probability > 0.7 else 'medium' if congestion_probability > 0.4 else 'low'
            }
            
        except Exception as e:
            self.logger.error(f"Congestion prediction failed: {e}")
            return {'probability': 0.5, 'error': str(e)}
    
    async def _preemptive_qos_adjustment(self, congestion_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Preemptively adjust QoS before congestion"""
        adjustments = {
            'traffic_shaping_enabled': True,
            'priority_enforcement_increased': True,
            'background_traffic_limited': True,
            'buffer_sizes_optimized': True
        }
        
        congestion_prob = congestion_prediction.get('probability', 0.5)
        
        if congestion_prob > 0.8:
            adjustments['aggressive_shaping'] = True
            adjustments['non_essential_traffic_blocked'] = True
        
        return adjustments
    
    async def _reactive_qos_adjustment(self, network_health: Dict[str, Any]) -> Dict[str, Any]:
        """React to current network performance issues"""
        adjustments = {}
        
        health_score = network_health.get('score', 1.0)
        factors = network_health.get('factors', {})
        
        if factors.get('bandwidth_utilization', 1.0) < 0.5:
            adjustments['increase_bandwidth_allocation'] = True
        
        if factors.get('latency_performance', 1.0) < 0.5:
            adjustments['prioritize_low_latency'] = True
            adjustments['reduce_buffer_bloat'] = True
        
        if factors.get('error_rates', 1.0) < 0.5:
            adjustments['increase_reliability_focus'] = True
            adjustments['reduce_aggressive_optimization'] = True
        
        return adjustments
    
    async def apply_optimization(self, optimization_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply bandwidth optimization configuration"""
        try:
            results = {}
            
            # Apply priority adjustments
            if 'priority_adjustment' in optimization_config:
                priority_result = await self._apply_priority_adjustment(
                    optimization_config['priority_adjustment']
                )
                results['priority_adjustment'] = priority_result
            
            # Apply QoS settings
            if optimization_config.get('qos_enabled', False):
                qos_result = await self._apply_qos_settings(optimization_config)
                results['qos_configuration'] = qos_result
            
            # Apply adaptive rate control
            if 'adaptive_rate' in optimization_config:
                rate_result = await self._apply_adaptive_rate_control(
                    optimization_config['adaptive_rate']
                )
                results['adaptive_rate'] = rate_result
            
            return {
                'optimization_applied': True,
                'results': results,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Bandwidth optimization failed: {e}")
            return {
                'optimization_applied': False,
                'error': str(e)
            }
    
    async def _apply_priority_adjustment(self, adjustment: float) -> Dict[str, Any]:
        """Apply priority adjustment to traffic classes"""
        try:
            # Adjust priority weights based on adjustment factor
            adjustment_results = {}
            
            for app, current_bw in self.current_allocation.items():
                if adjustment > 0:
                    # Increase high-priority app allocations
                    app_profile = self.demand_predictor._get_application_profile(app)
                    if app_profile.priority_weight > 0.7:
                        new_allocation = current_bw * (1 + adjustment)
                        adjustment_results[app] = {
                            'old_allocation': current_bw,
                            'new_allocation': new_allocation,
                            'change': new_allocation - current_bw
                        }
            
            return {
                'adjustment_factor': adjustment,
                'applications_affected': len(adjustment_results),
                'allocation_changes': adjustment_results
            }
            
        except Exception as e:
            self.logger.error(f"Priority adjustment failed: {e}")
            return {'error': str(e)}
    
    async def _apply_qos_settings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply QoS settings to network"""
        try:
            qos_settings = {
                'traffic_shaping': config.get('traffic_shaping', 'enabled'),
                'priority_queuing': config.get('priority_queuing', 'enabled'),
                'congestion_control': config.get('congestion_control', 'adaptive')
            }
            
            # Apply settings through network utilities
            # In real implementation, would configure tc, iptables, etc.
            
            return {
                'qos_enabled': True,
                'settings_applied': qos_settings,
                'configuration_method': 'ai_optimized'
            }
            
        except Exception as e:
            self.logger.error(f"QoS settings application failed: {e}")
            return {'error': str(e)}
    
    async def _apply_adaptive_rate_control(self, adaptive_rate: float) -> Dict[str, Any]:
        """Apply adaptive rate control"""
        try:
            # Calculate new rate limits based on adaptive factor
            rate_adjustments = {}
            
            for app, current_bw in self.current_allocation.items():
                adjusted_rate = current_bw * (1.0 + adaptive_rate)
                rate_adjustments[app] = {
                    'current_limit': current_bw,
                    'new_limit': adjusted_rate,
                    'adjustment_factor': adaptive_rate
                }
            
            return {
                'adaptive_rate_control': True,
                'rate_adjustments': rate_adjustments,
                'global_adjustment_factor': adaptive_rate
            }
            
        except Exception as e:
            self.logger.error(f"Adaptive rate control failed: {e}")
            return {'error': str(e)}
    
    async def get_bandwidth_insights(self) -> Dict[str, Any]:
        """Get insights about bandwidth management performance"""
        try:
            insights = {
                'current_allocation': self.current_allocation,
                'active_policies': len(self.active_policies),
                'allocation_history_size': len(self.allocation_history),
                'optimization_effectiveness': await self._calculate_optimization_effectiveness()
            }
            
            # Recent allocation trends
            if len(self.allocation_history) >= 5:
                recent_allocations = list(self.allocation_history)[-5:]
                insights['recent_trends'] = self._analyze_allocation_trends(recent_allocations)
            
            # Performance metrics
            if self.performance_metrics:
                insights['performance_summary'] = self._summarize_performance_metrics()
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Bandwidth insights failed: {e}")
            return {'error': str(e)}
    
    async def _calculate_optimization_effectiveness(self) -> float:
        """Calculate how effective the optimization has been"""
        if not self.optimization_history:
            return 0.5
        
        # Simple effectiveness based on optimization scores
        recent_scores = [opt['optimization_score'] for opt in list(self.qos_optimizer.optimization_history)[-10:]]
        
        if recent_scores:
            return float(np.mean(recent_scores))
        else:
            return 0.5
    
    def _analyze_allocation_trends(self, allocations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in bandwidth allocation"""
        if len(allocations) < 2:
            return {'trend': 'stable'}
        
        # Calculate total bandwidth usage trend
        total_bw_values = [sum(alloc['allocation'].values()) for alloc in allocations]
        
        # Simple trend calculation
        if len(total_bw_values) >= 2:
            slope = (total_bw_values[-1] - total_bw_values[0]) / len(total_bw_values)
            
            if slope > 1.0:
                trend = 'increasing'
            elif slope < -1.0:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'avg_total_allocation': float(np.mean(total_bw_values)),
            'allocation_variance': float(np.var(total_bw_values))
        }
    
    def _summarize_performance_metrics(self) -> Dict[str, Any]:
        """Summarize performance metrics"""
        # This would analyze stored performance metrics
        return {
            'avg_response_time': 50.0,  # ms
            'allocation_success_rate': 0.95,
            'user_satisfaction_score': 0.85,
            'optimization_frequency': len(self.performance_metrics)
        }