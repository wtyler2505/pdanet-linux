#!/usr/bin/env python3
"""
AIEnhancedTunnel - AI-Optimized Tunnel Management System

Provides intelligent tunnel interface management with predictive scaling,
adaptive parameter optimization, and real-time performance monitoring.
"""

import asyncio
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import deque
from contextlib import asynccontextmanager

import psutil
import numpy as np
from sklearn.preprocessing import StandardScaler

from ..core.traffic_predictor import TrafficPredictor
from ..utils.config import Config
from ..utils.network_utils import NetworkUtils
from ..data.collectors import TunnelMetricsCollector

logger = logging.getLogger(__name__)

@dataclass
class TunnelConfiguration:
    """Tunnel configuration parameters"""
    interface_name: str
    mtu: int
    buffer_size: int
    queue_discipline: str
    congestion_control: str
    compression_enabled: bool
    encryption_enabled: bool
    keepalive_interval: int
    timeout_settings: Dict[str, int]
    qos_class: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class TunnelMetrics:
    """Real-time tunnel performance metrics"""
    timestamp: datetime
    bytes_sent: int
    bytes_received: int
    packets_sent: int
    packets_received: int
    errors: int
    drops: int
    latency: float
    jitter: float
    throughput_mbps: float
    cpu_usage: float
    memory_usage: float
    buffer_utilization: float
    
    def to_feature_vector(self) -> np.ndarray:
        """Convert metrics to ML feature vector"""
        return np.array([
            self.throughput_mbps,
            self.latency,
            self.jitter,
            self.errors / max(self.packets_sent, 1),
            self.drops / max(self.packets_sent, 1),
            self.cpu_usage,
            self.memory_usage,
            self.buffer_utilization,
        ], dtype=np.float32)

class PerformanceOptimizer:
    """ML-based tunnel performance optimizer"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.scaler = StandardScaler()
        self.optimization_history = deque(maxlen=1000)
        
        # Performance baselines
        self.baseline_metrics = {
            'throughput': 10.0,  # Mbps
            'latency': 100.0,    # ms
            'jitter': 10.0,      # ms
            'error_rate': 0.01,  # 1%
        }
        
    async def calculate_optimal_config(self, 
                                     traffic_forecast: Dict[str, Any],
                                     connection_type: str,
                                     historical_performance: List[TunnelMetrics]) -> TunnelConfiguration:
        """Calculate optimal tunnel configuration based on predictions and history"""
        
        try:
            # Analyze historical performance
            performance_analysis = self._analyze_historical_performance(historical_performance)
            
            # Extract traffic predictions
            predicted_bandwidth = traffic_forecast.get('predictions', {}).get('15min', {}).get('predicted_bandwidth', 10.0)
            
            # Optimize MTU based on predicted traffic and connection type
            optimal_mtu = self._optimize_mtu(predicted_bandwidth, connection_type, performance_analysis)
            
            # Optimize buffer size
            optimal_buffer_size = self._optimize_buffer_size(predicted_bandwidth, performance_analysis)
            
            # Select optimal queue discipline
            optimal_qdisc = self._select_queue_discipline(predicted_bandwidth, performance_analysis)
            
            # Select congestion control algorithm
            optimal_cc = self._select_congestion_control(connection_type, performance_analysis)
            
            # Determine compression and encryption settings
            compression_enabled = self._should_enable_compression(predicted_bandwidth, performance_analysis)
            encryption_enabled = self._should_enable_encryption(connection_type)
            
            # Calculate QoS settings
            qos_class = self._determine_qos_class(predicted_bandwidth, traffic_forecast)
            
            config = TunnelConfiguration(
                interface_name='tun_ai',
                mtu=optimal_mtu,
                buffer_size=optimal_buffer_size,
                queue_discipline=optimal_qdisc,
                congestion_control=optimal_cc,
                compression_enabled=compression_enabled,
                encryption_enabled=encryption_enabled,
                keepalive_interval=self._calculate_keepalive_interval(performance_analysis),
                timeout_settings=self._calculate_timeout_settings(connection_type),
                qos_class=qos_class
            )
            
            self.logger.info(
                f"Optimized tunnel config: MTU={optimal_mtu}, "
                f"Buffer={optimal_buffer_size}, QDisc={optimal_qdisc}, "
                f"CC={optimal_cc}, Compression={compression_enabled}"
            )
            
            return config
            
        except Exception as e:
            self.logger.error(f"Config optimization failed: {e}")
            return self._get_default_config()
    
    def _analyze_historical_performance(self, metrics: List[TunnelMetrics]) -> Dict[str, Any]:
        """Analyze historical performance metrics"""
        if not metrics:
            return {'avg_throughput': 10.0, 'avg_latency': 100.0, 'error_rate': 0.01, 'stability': 0.5}
        
        throughputs = [m.throughput_mbps for m in metrics]
        latencies = [m.latency for m in metrics]
        error_rates = [m.errors / max(m.packets_sent, 1) for m in metrics]
        
        analysis = {
            'avg_throughput': np.mean(throughputs),
            'max_throughput': np.max(throughputs),
            'avg_latency': np.mean(latencies),
            'min_latency': np.min(latencies),
            'error_rate': np.mean(error_rates),
            'throughput_stability': 1.0 - np.std(throughputs) / max(np.mean(throughputs), 1.0),
            'latency_stability': 1.0 - np.std(latencies) / max(np.mean(latencies), 1.0),
        }
        
        return analysis
    
    def _optimize_mtu(self, predicted_bandwidth: float, connection_type: str, 
                     performance: Dict[str, Any]) -> int:
        """Optimize MTU based on network conditions"""
        base_mtu = 1500  # Standard Ethernet MTU
        
        # Adjust based on connection type
        if connection_type == 'cellular':
            base_mtu = 1420  # Account for carrier overhead
        elif connection_type == 'wifi':
            base_mtu = 1472  # Account for WiFi overhead
        
        # Adjust based on predicted bandwidth
        if predicted_bandwidth > 50.0:  # High bandwidth
            base_mtu = min(base_mtu + 100, 1500)  # Larger packets for efficiency
        elif predicted_bandwidth < 5.0:   # Low bandwidth
            base_mtu = max(base_mtu - 100, 576)   # Smaller packets for reliability
        
        # Adjust based on historical error rate
        error_rate = performance.get('error_rate', 0.01)
        if error_rate > 0.05:  # High error rate
            base_mtu = max(base_mtu - 200, 576)  # Smaller packets for reliability
        
        return base_mtu
    
    def _optimize_buffer_size(self, predicted_bandwidth: float, performance: Dict[str, Any]) -> int:
        """Optimize buffer size based on traffic patterns"""
        # Base buffer size calculation: bandwidth-delay product
        base_latency = performance.get('avg_latency', 100.0) / 1000.0  # Convert to seconds
        bdp_bytes = int(predicted_bandwidth * 1024 * 1024 * base_latency / 8)  # Convert Mbps to bytes
        
        # Ensure reasonable bounds
        min_buffer = 64 * 1024    # 64KB minimum
        max_buffer = 16 * 1024 * 1024  # 16MB maximum
        
        optimal_buffer = max(min_buffer, min(bdp_bytes * 2, max_buffer))  # 2x BDP for buffer
        
        return optimal_buffer
    
    def _select_queue_discipline(self, predicted_bandwidth: float, 
                               performance: Dict[str, Any]) -> str:
        """Select optimal queue discipline"""
        throughput_stability = performance.get('throughput_stability', 0.5)
        
        if predicted_bandwidth > 100.0:  # High bandwidth
            return 'fq_codel'  # Fair queuing with controlled delay
        elif throughput_stability < 0.3:  # Unstable connection
            return 'cake'      # Comprehensive queue management
        else:
            return 'fq'        # Fair queuing (default)
    
    def _select_congestion_control(self, connection_type: str, 
                                 performance: Dict[str, Any]) -> str:
        """Select optimal congestion control algorithm"""
        latency_stability = performance.get('latency_stability', 0.5)
        avg_latency = performance.get('avg_latency', 100.0)
        
        if connection_type == 'cellular':
            if avg_latency > 200.0:  # High latency cellular
                return 'hybla'   # Optimized for satellite/high-latency
            else:
                return 'westwood+' # Mobile-optimized
        elif latency_stability < 0.3:  # Variable latency
            return 'vegas'      # Delay-based congestion control
        else:
            return 'cubic'      # Default modern algorithm
    
    def _should_enable_compression(self, predicted_bandwidth: float, 
                                 performance: Dict[str, Any]) -> bool:
        """Determine if compression should be enabled"""
        avg_cpu = performance.get('avg_cpu_usage', 0.5)
        
        # Enable compression for low bandwidth or low CPU usage
        return predicted_bandwidth < 20.0 or avg_cpu < 0.3
    
    def _should_enable_encryption(self, connection_type: str) -> bool:
        """Determine if encryption should be enabled"""
        # Always enable encryption for cellular connections
        # For WiFi, assume the underlying connection might already be encrypted
        return connection_type in ['cellular', 'public_wifi']
    
    def _determine_qos_class(self, predicted_bandwidth: float, 
                           traffic_forecast: Dict[str, Any]) -> str:
        """Determine appropriate QoS class"""
        confidence = traffic_forecast.get('confidence', 0.5)
        
        if predicted_bandwidth > 50.0 and confidence > 0.8:
            return 'premium'    # High bandwidth, high confidence
        elif predicted_bandwidth > 20.0:
            return 'standard'   # Medium bandwidth
        else:
            return 'economy'    # Low bandwidth
    
    def _calculate_keepalive_interval(self, performance: Dict[str, Any]) -> int:
        """Calculate optimal keepalive interval"""
        stability = performance.get('throughput_stability', 0.5)
        
        if stability > 0.8:  # Stable connection
            return 60  # 60 seconds
        elif stability > 0.5:  # Moderate stability
            return 30  # 30 seconds
        else:  # Unstable connection
            return 15  # 15 seconds
    
    def _calculate_timeout_settings(self, connection_type: str) -> Dict[str, int]:
        """Calculate timeout settings based on connection type"""
        if connection_type == 'cellular':
            return {
                'connect_timeout': 30,
                'read_timeout': 60,
                'write_timeout': 30,
            }
        else:
            return {
                'connect_timeout': 10,
                'read_timeout': 30,
                'write_timeout': 10,
            }
    
    def _get_default_config(self) -> TunnelConfiguration:
        """Get default tunnel configuration as fallback"""
        return TunnelConfiguration(
            interface_name='tun_ai',
            mtu=1420,
            buffer_size=1024 * 1024,  # 1MB
            queue_discipline='fq_codel',
            congestion_control='cubic',
            compression_enabled=True,
            encryption_enabled=True,
            keepalive_interval=30,
            timeout_settings={'connect_timeout': 15, 'read_timeout': 30, 'write_timeout': 15},
            qos_class='standard'
        )
    
    async def suggest_adjustments(self, current_metrics: TunnelMetrics,
                                traffic_patterns: Dict[str, Any]) -> 'OptimizationSuggestions':
        """Suggest real-time adjustments based on current performance"""
        suggestions = OptimizationSuggestions()
        
        # Analyze current performance vs baselines
        throughput_ratio = current_metrics.throughput_mbps / self.baseline_metrics['throughput']
        latency_ratio = current_metrics.latency / self.baseline_metrics['latency']
        
        # MTU adjustment suggestions
        if current_metrics.errors > 0 and current_metrics.throughput_mbps < 5.0:
            suggestions.mtu_adjustment = -100  # Reduce MTU for reliability
            suggestions.confidence = 0.8
        elif throughput_ratio > 2.0 and current_metrics.errors == 0:
            suggestions.mtu_adjustment = 50   # Increase MTU for efficiency
            suggestions.confidence = 0.6
        
        # Buffer adjustment suggestions
        if current_metrics.buffer_utilization > 0.9:
            suggestions.buffer_adjustment = 1024 * 1024  # Increase by 1MB
            suggestions.confidence = max(suggestions.confidence, 0.9)
        elif current_metrics.buffer_utilization < 0.1:
            suggestions.buffer_adjustment = -512 * 1024  # Decrease by 512KB
            suggestions.confidence = max(suggestions.confidence, 0.7)
        
        # Compression suggestions
        if current_metrics.cpu_usage > 0.8 and current_metrics.throughput_mbps > 20.0:
            suggestions.disable_compression = True
            suggestions.confidence = max(suggestions.confidence, 0.8)
        elif current_metrics.cpu_usage < 0.3 and current_metrics.throughput_mbps < 10.0:
            suggestions.enable_compression = True
            suggestions.confidence = max(suggestions.confidence, 0.7)
        
        return suggestions

@dataclass
class OptimizationSuggestions:
    """Suggestions for tunnel optimization"""
    mtu_adjustment: int = 0
    buffer_adjustment: int = 0
    enable_compression: bool = False
    disable_compression: bool = False
    qdisc_change: Optional[str] = None
    congestion_control_change: Optional[str] = None
    confidence: float = 0.0

class AdaptiveMTUManager:
    """Manages adaptive MTU optimization"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.current_mtu = 1420
        self.mtu_history = deque(maxlen=100)
        self.performance_history = deque(maxlen=100)
        
    async def optimize_mtu(self, interface: str, current_metrics: TunnelMetrics) -> int:
        """Dynamically optimize MTU based on current performance"""
        try:
            # Record current performance
            self.performance_history.append(current_metrics)
            
            if len(self.performance_history) < 5:  # Need history for optimization
                return self.current_mtu
            
            # Analyze recent performance trend
            recent_metrics = list(self.performance_history)[-5:]
            
            avg_errors = np.mean([m.errors for m in recent_metrics])
            avg_throughput = np.mean([m.throughput_mbps for m in recent_metrics])
            
            new_mtu = self.current_mtu
            
            # Increase MTU if low errors and good throughput
            if avg_errors < 0.01 and avg_throughput > 20.0 and self.current_mtu < 1500:
                new_mtu = min(self.current_mtu + 20, 1500)
                self.logger.info(f"Increasing MTU to {new_mtu} due to good performance")
            
            # Decrease MTU if high errors or poor throughput
            elif avg_errors > 0.05 or (avg_throughput < 5.0 and self.current_mtu > 576):
                new_mtu = max(self.current_mtu - 50, 576)
                self.logger.info(f"Decreasing MTU to {new_mtu} due to poor performance")
            
            if new_mtu != self.current_mtu:
                await self._apply_mtu_change(interface, new_mtu)
                self.current_mtu = new_mtu
                self.mtu_history.append(new_mtu)
            
            return self.current_mtu
            
        except Exception as e:
            self.logger.error(f"MTU optimization failed: {e}")
            return self.current_mtu
    
    async def _apply_mtu_change(self, interface: str, new_mtu: int):
        """Apply MTU change to network interface"""
        try:
            cmd = f"ip link set dev {interface} mtu {new_mtu}"
            result = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                self.logger.error(f"MTU change failed: {stderr.decode()}")
            else:
                self.logger.info(f"Successfully changed {interface} MTU to {new_mtu}")
                
        except Exception as e:
            self.logger.error(f"Error applying MTU change: {e}")

class TunnelManager:
    """Core tunnel management functionality"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.network_utils = NetworkUtils()
        self.active_tunnels: Dict[str, Dict[str, Any]] = {}
        
    async def create_tunnel(self, 
                          mtu: int,
                          buffer_size: int,
                          queue_discipline: str,
                          congestion_control: str) -> Dict[str, Any]:
        """Create optimized tunnel interface"""
        tunnel_name = f"tun_ai_{datetime.now().strftime('%H%M%S')}"
        
        try:
            # Create TUN interface
            await self._create_tun_interface(tunnel_name, mtu)
            
            # Configure queue discipline
            await self._configure_qdisc(tunnel_name, queue_discipline)
            
            # Set congestion control
            await self._set_congestion_control(congestion_control)
            
            # Configure buffer sizes
            await self._configure_buffers(tunnel_name, buffer_size)
            
            tunnel_info = {
                'name': tunnel_name,
                'mtu': mtu,
                'buffer_size': buffer_size,
                'queue_discipline': queue_discipline,
                'congestion_control': congestion_control,
                'created_at': datetime.utcnow(),
                'status': 'active'
            }
            
            self.active_tunnels[tunnel_name] = tunnel_info
            
            self.logger.info(f"Created tunnel {tunnel_name} with optimized parameters")
            return tunnel_info
            
        except Exception as e:
            self.logger.error(f"Tunnel creation failed: {e}")
            raise
    
    async def _create_tun_interface(self, name: str, mtu: int):
        """Create TUN network interface"""
        commands = [
            f"ip tuntap add name {name} mode tun",
            f"ip link set {name} up",
            f"ip link set dev {name} mtu {mtu}"
        ]
        
        for cmd in commands:
            result = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                raise Exception(f"Command failed: {cmd}, Error: {stderr.decode()}")
    
    async def _configure_qdisc(self, interface: str, qdisc: str):
        """Configure queue discipline for interface"""
        cmd = f"tc qdisc replace dev {interface} root {qdisc}"
        
        result = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await result.communicate()
        
        if result.returncode != 0:
            self.logger.warning(f"QDisc configuration failed: {stderr.decode()}")
    
    async def _set_congestion_control(self, algorithm: str):
        """Set system-wide congestion control algorithm"""
        try:
            with open('/proc/sys/net/ipv4/tcp_congestion_control', 'w') as f:
                f.write(algorithm)
            self.logger.info(f"Set congestion control to {algorithm}")
        except Exception as e:
            self.logger.warning(f"Could not set congestion control: {e}")
    
    async def _configure_buffers(self, interface: str, buffer_size: int):
        """Configure network buffer sizes"""
        try:
            # Set socket buffer sizes
            commands = [
                f"echo {buffer_size} > /proc/sys/net/core/rmem_default",
                f"echo {buffer_size * 2} > /proc/sys/net/core/rmem_max",
                f"echo {buffer_size} > /proc/sys/net/core/wmem_default",
                f"echo {buffer_size * 2} > /proc/sys/net/core/wmem_max"
            ]
            
            for cmd in commands:
                result = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await result.communicate()
                
        except Exception as e:
            self.logger.warning(f"Buffer configuration failed: {e}")
    
    async def get_metrics(self, tunnel: Dict[str, Any]) -> TunnelMetrics:
        """Get current metrics for tunnel interface"""
        interface_name = tunnel['name']
        
        try:
            # Get network interface statistics
            net_stats = psutil.net_io_counters(pernic=True).get(interface_name)
            
            if not net_stats:
                raise Exception(f"Interface {interface_name} not found")
            
            # Get system resource usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Calculate throughput (simplified - would need time-series data for accuracy)
            throughput_mbps = (net_stats.bytes_sent + net_stats.bytes_recv) / (1024 * 1024)
            
            return TunnelMetrics(
                timestamp=datetime.utcnow(),
                bytes_sent=net_stats.bytes_sent,
                bytes_received=net_stats.bytes_recv,
                packets_sent=net_stats.packets_sent,
                packets_received=net_stats.packets_recv,
                errors=net_stats.errin + net_stats.errout,
                drops=net_stats.dropin + net_stats.dropout,
                latency=await self._measure_latency(interface_name),
                jitter=await self._measure_jitter(interface_name),
                throughput_mbps=throughput_mbps,
                cpu_usage=cpu_percent / 100.0,
                memory_usage=memory.percent / 100.0,
                buffer_utilization=0.5  # Placeholder - would need actual buffer monitoring
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get tunnel metrics: {e}")
            # Return default metrics
            return TunnelMetrics(
                timestamp=datetime.utcnow(),
                bytes_sent=0, bytes_received=0,
                packets_sent=0, packets_received=0,
                errors=0, drops=0,
                latency=100.0, jitter=10.0,
                throughput_mbps=1.0,
                cpu_usage=0.5, memory_usage=0.5,
                buffer_utilization=0.5
            )
    
    async def _measure_latency(self, interface: str) -> float:
        """Measure network latency through interface (simplified)"""
        try:
            # Ping through specific interface (simplified)
            cmd = f"ping -c 1 -W 1 8.8.8.8"
            result = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                output = stdout.decode()
                # Extract latency from ping output (simplified parsing)
                for line in output.split('\n'):
                    if 'time=' in line:
                        time_part = line.split('time=')[1].split(' ')[0]
                        return float(time_part)
            
            return 100.0  # Default latency
            
        except Exception:
            return 100.0
    
    async def _measure_jitter(self, interface: str) -> float:
        """Measure network jitter (simplified)"""
        # Simplified jitter measurement - in practice would need multiple samples
        latencies = []
        for _ in range(3):
            latency = await self._measure_latency(interface)
            latencies.append(latency)
            await asyncio.sleep(0.1)
        
        return np.std(latencies) if latencies else 10.0

class AIEnhancedTunnel:
    """Main AI-enhanced tunnel management system"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core components
        self.tunnel_manager = TunnelManager(config)
        self.performance_optimizer = PerformanceOptimizer(config)
        self.adaptive_mtu = AdaptiveMTUManager(config)
        self.metrics_collector = TunnelMetricsCollector(config)
        
        # AI integration
        self.traffic_predictor: Optional[TrafficPredictor] = None
        
        # State tracking
        self.active_tunnels: Dict[str, Any] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        
    async def initialize(self, traffic_predictor: TrafficPredictor):
        """Initialize with traffic predictor reference"""
        self.traffic_predictor = traffic_predictor
        await self.metrics_collector.initialize()
        self.logger.info("AIEnhancedTunnel initialized")
    
    async def create_intelligent_tunnel(self, connection_params: Dict[str, Any]) -> Dict[str, Any]:
        """Create tunnel with AI-optimized parameters"""
        try:
            # Get traffic predictions if available
            traffic_forecast = {}
            if self.traffic_predictor:
                current_metrics = await self._get_current_network_metrics()
                traffic_forecast = await self.traffic_predictor.predict(current_metrics)
            
            # Get historical performance data
            historical_performance = await self._get_historical_performance()
            
            # Calculate optimal configuration
            optimal_params = await self.performance_optimizer.calculate_optimal_config(
                traffic_forecast=traffic_forecast,
                connection_type=connection_params.get('type', 'wifi'),
                historical_performance=historical_performance
            )
            
            # Create tunnel with optimized settings
            tunnel = await self.tunnel_manager.create_tunnel(
                mtu=optimal_params.mtu,
                buffer_size=optimal_params.buffer_size,
                queue_discipline=optimal_params.queue_discipline,
                congestion_control=optimal_params.congestion_control
            )
            
            # Store tunnel configuration
            tunnel['ai_config'] = optimal_params
            self.active_tunnels[tunnel['name']] = tunnel
            
            # Start adaptive monitoring
            await self.start_adaptive_monitoring(tunnel, optimal_params)
            
            self.logger.info(f"Created intelligent tunnel: {tunnel['name']}")
            return tunnel
            
        except Exception as e:
            self.logger.error(f"Intelligent tunnel creation failed: {e}")
            raise
    
    async def _get_current_network_metrics(self) -> Dict[str, Any]:
        """Get current network metrics for prediction"""
        # Simplified metrics collection
        net_stats = psutil.net_io_counters()
        
        return {
            'timestamp': datetime.utcnow(),
            'bandwidth_usage': {'total': (net_stats.bytes_sent + net_stats.bytes_recv) / (1024 * 1024)},
            'connections': [],
            'active_applications': [],
            'latency_metrics': {'avg': 50.0},
            'packet_loss': 0.01,
            'jitter': 5.0,
        }
    
    async def _get_historical_performance(self) -> List[TunnelMetrics]:
        """Get historical performance metrics"""
        # In a real implementation, this would load from storage
        # For now, return empty list
        return []
    
    async def start_adaptive_monitoring(self, tunnel: Dict[str, Any], config: TunnelConfiguration):
        """Start adaptive monitoring and optimization for tunnel"""
        tunnel_name = tunnel['name']
        
        async def monitor_and_optimize():
            """Monitoring and optimization loop"""
            while tunnel_name in self.active_tunnels:
                try:
                    # Get current metrics
                    metrics = await self.tunnel_manager.get_metrics(tunnel)
                    
                    # Store metrics
                    await self.metrics_collector.store_metrics(tunnel_name, metrics)
                    
                    # Adaptive MTU optimization
                    new_mtu = await self.adaptive_mtu.optimize_mtu(tunnel_name, metrics)
                    
                    # Get optimization suggestions
                    if self.traffic_predictor:
                        traffic_patterns = await self.traffic_predictor.get_current_patterns()
                        suggestions = await self.performance_optimizer.suggest_adjustments(
                            metrics, traffic_patterns
                        )
                        
                        # Apply suggestions if confidence is high
                        if suggestions.confidence > 0.8:
                            await self._apply_optimization_suggestions(tunnel_name, suggestions)
                    
                    # Wait before next check
                    await asyncio.sleep(30)  # Monitor every 30 seconds
                    
                except Exception as e:
                    self.logger.error(f"Monitoring error for {tunnel_name}: {e}")
                    await asyncio.sleep(60)  # Longer wait on error
        
        # Start monitoring task
        task = asyncio.create_task(monitor_and_optimize())
        self.monitoring_tasks[tunnel_name] = task
        
        self.logger.info(f"Started adaptive monitoring for {tunnel_name}")
    
    async def _apply_optimization_suggestions(self, tunnel_name: str, 
                                            suggestions: OptimizationSuggestions):
        """Apply optimization suggestions to tunnel"""
        try:
            if suggestions.mtu_adjustment != 0:
                current_mtu = self.adaptive_mtu.current_mtu
                new_mtu = max(576, min(1500, current_mtu + suggestions.mtu_adjustment))
                await self.adaptive_mtu._apply_mtu_change(tunnel_name, new_mtu)
            
            if suggestions.qdisc_change:
                await self.tunnel_manager._configure_qdisc(tunnel_name, suggestions.qdisc_change)
            
            if suggestions.congestion_control_change:
                await self.tunnel_manager._set_congestion_control(suggestions.congestion_control_change)
            
            self.logger.info(f"Applied optimization suggestions to {tunnel_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to apply optimizations: {e}")
    
    async def optimize_tunnel(self, optimization_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize existing tunnel based on configuration"""
        try:
            results = {}
            
            # Apply MTU optimization if requested
            if optimization_config.get('mtu_optimization', False):
                for tunnel_name, tunnel in self.active_tunnels.items():
                    metrics = await self.tunnel_manager.get_metrics(tunnel)
                    new_mtu = await self.adaptive_mtu.optimize_mtu(tunnel_name, metrics)
                    results['mtu_optimized'] = new_mtu
            
            # Apply compression settings
            if 'compression_enabled' in optimization_config:
                results['compression'] = optimization_config['compression_enabled']
                # Implementation would configure compression here
            
            return {
                'optimization_applied': True,
                'results': results,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Tunnel optimization failed: {e}")
            return {
                'optimization_applied': False,
                'error': str(e)
            }
    
    async def get_tunnel_status(self) -> Dict[str, Any]:
        """Get status of all active tunnels"""
        status = {
            'active_tunnels': len(self.active_tunnels),
            'tunnels': {},
            'monitoring_active': len(self.monitoring_tasks)
        }
        
        for tunnel_name, tunnel in self.active_tunnels.items():
            try:
                metrics = await self.tunnel_manager.get_metrics(tunnel)
                status['tunnels'][tunnel_name] = {
                    'config': tunnel,
                    'current_metrics': asdict(metrics),
                    'monitoring': tunnel_name in self.monitoring_tasks
                }
            except Exception as e:
                status['tunnels'][tunnel_name] = {
                    'error': str(e)
                }
        
        return status
    
    async def cleanup(self):
        """Clean up resources"""
        # Cancel monitoring tasks
        for task in self.monitoring_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self.monitoring_tasks:
            await asyncio.gather(*self.monitoring_tasks.values(), return_exceptions=True)
        
        self.monitoring_tasks.clear()
        self.active_tunnels.clear()
        
        self.logger.info("AIEnhancedTunnel cleanup completed")