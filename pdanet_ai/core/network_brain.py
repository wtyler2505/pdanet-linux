#!/usr/bin/env python3
"""
NetworkBrain - Central AI Coordination System for PDanet-Linux

This is the core orchestrator that coordinates all AI/ML components for intelligent
network management. It integrates traffic prediction, connection optimization,
security monitoring, and user behavior analysis.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager

import numpy as np
import torch
from sklearn.preprocessing import StandardScaler

from .traffic_predictor import TrafficPredictor
from .connection_optimizer import ConnectionOptimizer
from .security_monitor import SecurityMonitor
from .user_profiler import UserProfiler
from ..system.enhanced_tunnel import AIEnhancedTunnel
from ..system.bandwidth_manager import IntelligentBandwidthManager
from ..data.collectors import NetworkDataCollector
from ..utils.config import Config
from ..utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)

@dataclass
class NetworkState:
    """Current network state representation"""
    timestamp: datetime
    interfaces: Dict[str, Any]
    connections: List[Dict[str, Any]]
    bandwidth_usage: Dict[str, float]
    latency_metrics: Dict[str, float]
    packet_loss: float
    jitter: float
    cpu_usage: float
    memory_usage: float
    active_applications: List[str]
    user_context: Optional[Dict[str, Any]] = None
    
    def to_feature_vector(self) -> np.ndarray:
        """Convert network state to ML feature vector"""
        features = [
            # Bandwidth features
            self.bandwidth_usage.get('upload', 0.0),
            self.bandwidth_usage.get('download', 0.0),
            self.bandwidth_usage.get('total', 0.0),
            
            # Latency and quality features
            self.latency_metrics.get('avg', 0.0),
            self.latency_metrics.get('min', 0.0),
            self.latency_metrics.get('max', 0.0),
            self.packet_loss,
            self.jitter,
            
            # System resource features
            self.cpu_usage,
            self.memory_usage,
            
            # Connection features
            len(self.connections),
            len(self.active_applications),
            
            # Time-based features
            self.timestamp.hour,
            self.timestamp.weekday(),
            
            # Interface features
            len(self.interfaces),
            sum(1 for iface in self.interfaces.values() if iface.get('status') == 'up'),
        ]
        return np.array(features, dtype=np.float32)

@dataclass
class OptimizationResult:
    """Result of network optimization operation"""
    success: bool
    applied_changes: Dict[str, Any]
    performance_improvement: Dict[str, float]
    confidence_score: float
    explanation: str
    timestamp: datetime
    estimated_duration: int  # seconds

class DecisionEngine:
    """AI-driven decision making engine"""
    
    def __init__(self, config: Config):
        self.config = config
        self.decision_history: List[Dict] = []
        self.scaler = StandardScaler()
        self.model = None
        self._load_decision_model()
        
    def _load_decision_model(self):
        """Load or initialize the decision model"""
        try:
            model_path = self.config.get('decision_model_path')
            if model_path and model_path.exists():
                self.model = torch.load(model_path)
                logger.info(f"Loaded decision model from {model_path}")
            else:
                logger.info("Initializing new decision model")
                self._initialize_model()
        except Exception as e:
            logger.error(f"Error loading decision model: {e}")
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize a new decision model"""
        # Simple neural network for decision making
        import torch.nn as nn
        
        class DecisionNet(nn.Module):
            def __init__(self, input_dim=20, hidden_dim=128, output_dim=10):
                super().__init__()
                self.network = nn.Sequential(
                    nn.Linear(input_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(hidden_dim, hidden_dim // 2),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(hidden_dim // 2, output_dim),
                    nn.Softmax(dim=1)
                )
            
            def forward(self, x):
                return self.network(x)
        
        self.model = DecisionNet()
        logger.info("Initialized new decision neural network")
    
    async def decide(self, 
                    traffic_forecast: Dict[str, Any],
                    security_status: Dict[str, Any],
                    user_patterns: Dict[str, Any],
                    current_state: NetworkState) -> Dict[str, Any]:
        """Make optimization decisions based on AI analysis"""
        
        # Combine all inputs into decision context
        decision_context = {
            'traffic_forecast': traffic_forecast,
            'security_status': security_status,
            'user_patterns': user_patterns,
            'current_state': asdict(current_state),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Generate feature vector for ML model
        features = self._extract_decision_features(decision_context)
        
        # Get model prediction
        decision_scores = await self._predict_optimal_actions(features)
        
        # Convert model output to concrete actions
        optimal_config = await self._scores_to_config(decision_scores, decision_context)
        
        # Record decision for learning
        self.decision_history.append({
            'context': decision_context,
            'features': features.tolist(),
            'decision': optimal_config,
            'timestamp': datetime.utcnow()
        })
        
        return optimal_config
    
    def _extract_decision_features(self, context: Dict[str, Any]) -> np.ndarray:
        """Extract features for decision making"""
        features = []
        
        # Traffic forecast features
        forecast = context['traffic_forecast']
        features.extend([
            forecast.get('predicted_bandwidth', 0.0),
            forecast.get('confidence', 0.0),
            forecast.get('trend', 0.0),
        ])
        
        # Security features
        security = context['security_status']
        features.extend([
            security.get('threat_level', 0.0),
            security.get('anomaly_score', 0.0),
            len(security.get('active_threats', [])),
        ])
        
        # User pattern features
        user_patterns = context['user_patterns']
        features.extend([
            user_patterns.get('predicted_usage', 0.0),
            user_patterns.get('quality_preference', 0.5),
            user_patterns.get('cost_sensitivity', 0.5),
        ])
        
        # Current state features
        state = context['current_state']
        features.extend([
            state['bandwidth_usage'].get('total', 0.0),
            state.get('packet_loss', 0.0),
            state.get('cpu_usage', 0.0),
            state.get('memory_usage', 0.0),
            len(state.get('connections', [])),
            len(state.get('active_applications', [])),
        ])
        
        # Time features
        timestamp = datetime.fromisoformat(context['timestamp'])
        features.extend([
            timestamp.hour / 24.0,
            timestamp.weekday() / 7.0,
        ])
        
        return np.array(features, dtype=np.float32)
    
    async def _predict_optimal_actions(self, features: np.ndarray) -> torch.Tensor:
        """Predict optimal actions using ML model"""
        try:
            with torch.no_grad():
                # Normalize features
                if len(self.decision_history) > 10:  # Only scale if we have enough data
                    features_scaled = self.scaler.transform(features.reshape(1, -1))
                else:
                    features_scaled = features.reshape(1, -1)
                
                # Convert to tensor
                features_tensor = torch.FloatTensor(features_scaled)
                
                # Get model prediction
                predictions = self.model(features_tensor)
                return predictions.squeeze()
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            # Fallback to random baseline
            return torch.rand(10)
    
    async def _scores_to_config(self, scores: torch.Tensor, context: Dict) -> Dict[str, Any]:
        """Convert model scores to concrete configuration"""
        scores_np = scores.numpy()
        
        # Map scores to configuration parameters
        config = {
            'bandwidth_allocation': {
                'priority_adjustment': float(scores_np[0]),
                'qos_enabled': scores_np[1] > 0.5,
                'adaptive_rate': float(scores_np[2]),
            },
            'routing': {
                'path_optimization': scores_np[3] > 0.5,
                'load_balancing': float(scores_np[4]),
                'failover_threshold': float(scores_np[5]),
            },
            'security': {
                'threat_response_level': int(scores_np[6] * 3),  # 0-2 scale
                'monitoring_intensity': float(scores_np[7]),
            },
            'tunnel': {
                'mtu_optimization': scores_np[8] > 0.5,
                'compression_enabled': scores_np[9] > 0.5,
            },
            'confidence': float(torch.max(scores)),
        }
        
        return config

class NetworkBrain:
    """Central AI coordination system for PDanet-Linux"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize AI components
        self.traffic_predictor = TrafficPredictor(config)
        self.connection_optimizer = ConnectionOptimizer(config)
        self.security_monitor = SecurityMonitor(config)
        self.user_profiler = UserProfiler(config)
        self.decision_engine = DecisionEngine(config)
        
        # Initialize system components
        self.tunnel_manager = AIEnhancedTunnel(config)
        self.bandwidth_manager = IntelligentBandwidthManager(config)
        self.data_collector = NetworkDataCollector(config)
        self.metrics_collector = MetricsCollector(config)
        
        # State management
        self.current_state: Optional[NetworkState] = None
        self.optimization_history: List[OptimizationResult] = []
        self.is_running = False
        self.optimization_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Initialize all AI components"""
        self.logger.info("Initializing NetworkBrain components...")
        
        try:
            # Initialize all components
            await self.traffic_predictor.initialize()
            await self.connection_optimizer.initialize()
            await self.security_monitor.initialize()
            await self.user_profiler.initialize()
            await self.data_collector.initialize()
            
            self.logger.info("NetworkBrain initialization complete")
        except Exception as e:
            self.logger.error(f"Failed to initialize NetworkBrain: {e}")
            raise
    
    async def start_optimization_loop(self):
        """Start the main optimization loop"""
        if self.is_running:
            self.logger.warning("Optimization loop already running")
            return
        
        self.is_running = True
        self.optimization_task = asyncio.create_task(self._optimization_loop())
        self.logger.info("Started network optimization loop")
    
    async def stop_optimization_loop(self):
        """Stop the optimization loop"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.optimization_task:
            self.optimization_task.cancel()
            try:
                await self.optimization_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Stopped network optimization loop")
    
    async def _optimization_loop(self):
        """Main optimization loop"""
        optimization_interval = self.config.get('optimization_interval', 30)  # seconds
        
        while self.is_running:
            try:
                await self.optimize_network_once()
                await asyncio.sleep(optimization_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in optimization loop: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def optimize_network_once(self) -> OptimizationResult:
        """Perform one optimization cycle"""
        start_time = datetime.utcnow()
        
        try:
            # Collect current network state
            self.current_state = await self._collect_network_state()
            
            # Get predictions from all AI components
            traffic_forecast = await self.traffic_predictor.predict(self.current_state)
            security_assessment = await self.security_monitor.analyze(self.current_state)
            user_behavior = await self.user_profiler.get_patterns(
                self.current_state.user_context
            )
            
            # AI-driven decision making
            optimal_config = await self.decision_engine.decide(
                traffic_forecast=traffic_forecast,
                security_status=security_assessment,
                user_patterns=user_behavior,
                current_state=self.current_state
            )
            
            # Apply optimizations
            optimization_result = await self._apply_optimizations(optimal_config)
            
            # Record metrics
            await self.metrics_collector.record_optimization(
                optimization_result, 
                datetime.utcnow() - start_time
            )
            
            self.optimization_history.append(optimization_result)
            
            # Keep history manageable
            if len(self.optimization_history) > 1000:
                self.optimization_history = self.optimization_history[-800:]
            
            self.logger.info(
                f"Network optimization completed: confidence={optimal_config['confidence']:.2f}"
            )
            
            return optimization_result
            
        except Exception as e:
            error_result = OptimizationResult(
                success=False,
                applied_changes={},
                performance_improvement={},
                confidence_score=0.0,
                explanation=f"Optimization failed: {str(e)}",
                timestamp=datetime.utcnow(),
                estimated_duration=0
            )
            
            self.logger.error(f"Network optimization failed: {e}")
            return error_result
    
    async def _collect_network_state(self) -> NetworkState:
        """Collect comprehensive network state information"""
        # Collect data from all sources
        network_data = await self.data_collector.collect_all()
        
        return NetworkState(
            timestamp=datetime.utcnow(),
            interfaces=network_data.get('interfaces', {}),
            connections=network_data.get('connections', []),
            bandwidth_usage=network_data.get('bandwidth_usage', {}),
            latency_metrics=network_data.get('latency_metrics', {}),
            packet_loss=network_data.get('packet_loss', 0.0),
            jitter=network_data.get('jitter', 0.0),
            cpu_usage=network_data.get('cpu_usage', 0.0),
            memory_usage=network_data.get('memory_usage', 0.0),
            active_applications=network_data.get('active_applications', []),
            user_context=network_data.get('user_context')
        )
    
    async def _apply_optimizations(self, config: Dict[str, Any]) -> OptimizationResult:
        """Apply optimization configuration to the network"""
        applied_changes = {}
        performance_improvements = {}
        
        try:
            # Apply bandwidth optimizations
            if 'bandwidth_allocation' in config:
                bandwidth_result = await self.bandwidth_manager.apply_optimization(
                    config['bandwidth_allocation']
                )
                applied_changes['bandwidth'] = bandwidth_result
                
            # Apply routing optimizations
            if 'routing' in config:
                routing_result = await self.connection_optimizer.optimize_routing(
                    config['routing']
                )
                applied_changes['routing'] = routing_result
                
            # Apply tunnel optimizations
            if 'tunnel' in config:
                tunnel_result = await self.tunnel_manager.optimize_tunnel(
                    config['tunnel']
                )
                applied_changes['tunnel'] = tunnel_result
                
            # Apply security configurations
            if 'security' in config:
                security_result = await self.security_monitor.apply_security_config(
                    config['security']
                )
                applied_changes['security'] = security_result
            
            # Measure performance improvements
            await asyncio.sleep(5)  # Wait for changes to take effect
            new_state = await self._collect_network_state()
            
            if self.current_state:
                performance_improvements = self._calculate_improvements(
                    self.current_state, new_state
                )
            
            return OptimizationResult(
                success=True,
                applied_changes=applied_changes,
                performance_improvement=performance_improvements,
                confidence_score=config.get('confidence', 0.0),
                explanation="Successfully applied AI-driven network optimizations",
                timestamp=datetime.utcnow(),
                estimated_duration=300  # 5 minutes
            )
            
        except Exception as e:
            self.logger.error(f"Failed to apply optimizations: {e}")
            return OptimizationResult(
                success=False,
                applied_changes=applied_changes,
                performance_improvement={},
                confidence_score=0.0,
                explanation=f"Optimization failed: {str(e)}",
                timestamp=datetime.utcnow(),
                estimated_duration=0
            )
    
    def _calculate_improvements(self, old_state: NetworkState, new_state: NetworkState) -> Dict[str, float]:
        """Calculate performance improvements between states"""
        improvements = {}
        
        # Bandwidth improvement
        old_bw = old_state.bandwidth_usage.get('total', 0.0)
        new_bw = new_state.bandwidth_usage.get('total', 0.0)
        if old_bw > 0:
            improvements['bandwidth_efficiency'] = (new_bw - old_bw) / old_bw * 100
        
        # Latency improvement
        old_latency = old_state.latency_metrics.get('avg', 0.0)
        new_latency = new_state.latency_metrics.get('avg', 0.0)
        if old_latency > 0:
            improvements['latency_reduction'] = (old_latency - new_latency) / old_latency * 100
        
        # Packet loss improvement
        improvements['packet_loss_reduction'] = (old_state.packet_loss - new_state.packet_loss) * 100
        
        # CPU usage improvement
        improvements['cpu_efficiency'] = (old_state.cpu_usage - new_state.cpu_usage) * 100
        
        return improvements
    
    async def get_network_status(self) -> Dict[str, Any]:
        """Get current network status and AI insights"""
        if not self.current_state:
            await self.optimize_network_once()
        
        status = {
            'timestamp': datetime.utcnow().isoformat(),
            'current_state': asdict(self.current_state) if self.current_state else None,
            'optimization_status': {
                'is_running': self.is_running,
                'last_optimization': self.optimization_history[-1] if self.optimization_history else None,
                'total_optimizations': len(self.optimization_history),
            },
            'ai_insights': await self._generate_insights(),
        }
        
        return status
    
    async def _generate_insights(self) -> Dict[str, Any]:
        """Generate AI insights about network performance"""
        insights = {
            'performance_trends': [],
            'recommendations': [],
            'predicted_issues': [],
        }
        
        if len(self.optimization_history) >= 5:
            recent_results = self.optimization_history[-5:]
            
            # Analyze performance trends
            confidence_trend = [r.confidence_score for r in recent_results]
            if len(confidence_trend) > 1:
                trend_direction = "improving" if confidence_trend[-1] > confidence_trend[0] else "declining"
                insights['performance_trends'].append(f"AI confidence is {trend_direction}")
            
            # Generate recommendations
            avg_confidence = np.mean(confidence_trend)
            if avg_confidence < 0.7:
                insights['recommendations'].append(
                    "Consider manual network tuning - AI confidence is low"
                )
            
            # Predict potential issues
            if self.current_state and self.current_state.packet_loss > 0.05:
                insights['predicted_issues'].append(
                    "High packet loss detected - connection quality may degrade"
                )
        
        return insights
    
    @asynccontextmanager
    async def managed_optimization(self):
        """Context manager for safe optimization lifecycle"""
        try:
            await self.initialize()
            await self.start_optimization_loop()
            yield self
        finally:
            await self.stop_optimization_loop()

# Usage example
if __name__ == "__main__":
    import asyncio
    from ..utils.config import Config
    
    async def main():
        config = Config()
        
        async with NetworkBrain(config).managed_optimization() as brain:
            # Let it run for a few optimization cycles
            await asyncio.sleep(120)
            
            # Get status
            status = await brain.get_network_status()
            print(json.dumps(status, indent=2, default=str))
    
    asyncio.run(main())