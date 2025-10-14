#!/usr/bin/env python3
"""
Data Collection System for AI-Enhanced PDanet-Linux

Provides comprehensive data collection capabilities for network metrics,
traffic patterns, user behavior, and system performance monitoring.
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from pathlib import Path

import psutil
import numpy as np

from ..utils.config import Config
from ..utils.network_utils import NetworkUtils

logger = logging.getLogger(__name__)

@dataclass
class NetworkDataPoint:
    """Single network measurement data point"""
    timestamp: datetime
    interface_name: str
    bytes_sent: int
    bytes_received: int
    packets_sent: int
    packets_received: int
    errors_in: int
    errors_out: int
    drops_in: int
    drops_out: int
    throughput_mbps: float
    latency_ms: float
    jitter_ms: float
    packet_loss_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    load_average: List[float]
    network_connections: int
    active_processes: int
    uptime_seconds: float
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class NetworkDataCollector:
    """Collects network interface statistics and performance metrics"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.network_utils = NetworkUtils(config)
        
        # Data storage
        self.data_buffer = deque(maxlen=10000)
        self.interface_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Collection state
        self.is_collecting = False
        self.collection_task: Optional[asyncio.Task] = None
        self.collection_interval = config.get('network.monitoring_interval', 5)
        
    async def initialize(self):
        """Initialize the network data collector"""
        self.logger.info("Initializing NetworkDataCollector...")
        
        try:
            # Verify network utilities are available
            capabilities = self.network_utils.get_capabilities()
            self.logger.info(f"Network capabilities: {capabilities}")
            
            # Collect initial baseline
            await self._collect_baseline()
            
            self.logger.info("NetworkDataCollector initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize NetworkDataCollector: {e}")
            raise
    
    async def _collect_baseline(self):
        """Collect initial baseline measurements"""
        try:
            # Get initial interface measurements
            interfaces = await self.network_utils.get_network_interfaces()
            
            for interface_name in interfaces.keys():
                # Skip virtual interfaces for baseline
                if not interface_name.startswith(('lo', 'docker', 'br-')):
                    baseline_data = await self._collect_interface_data(interface_name)
                    if baseline_data:
                        self.interface_history[interface_name].append(baseline_data)
            
            self.logger.info(f"Collected baseline for {len(self.interface_history)} interfaces")
            
        except Exception as e:
            self.logger.error(f"Failed to collect baseline: {e}")
    
    async def start_collection(self):
        """Start continuous data collection"""
        if self.is_collecting:
            self.logger.warning("Data collection already running")
            return
        
        self.is_collecting = True
        self.collection_task = asyncio.create_task(self._collection_loop())
        self.logger.info("Started network data collection")
    
    async def stop_collection(self):
        """Stop data collection"""
        if not self.is_collecting:
            return
        
        self.is_collecting = False
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Stopped network data collection")
    
    async def _collection_loop(self):
        """Main data collection loop"""
        while self.is_collecting:
            try:
                await self._collect_all_interfaces()
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Collection loop error: {e}")
                await asyncio.sleep(self.collection_interval * 2)  # Back off on error
    
    async def _collect_all_interfaces(self):
        """Collect data from all network interfaces"""
        try:
            interfaces = await self.network_utils.get_network_interfaces()
            
            for interface_name in interfaces.keys():
                # Skip certain virtual interfaces
                if interface_name.startswith(('lo', 'docker0', 'br-')):
                    continue
                
                try:
                    data_point = await self._collect_interface_data(interface_name)
                    if data_point:
                        self.interface_history[interface_name].append(data_point)
                        self.data_buffer.append(data_point)
                except Exception as e:
                    self.logger.debug(f"Failed to collect data for {interface_name}: {e}")
        
        except Exception as e:
            self.logger.error(f"Failed to collect interface data: {e}")
    
    async def _collect_interface_data(self, interface_name: str) -> Optional[NetworkDataPoint]:
        """Collect data for a specific interface"""
        try:
            # Get detailed interface information
            details = await self.network_utils.get_interface_details(interface_name)
            
            if 'statistics' not in details:
                return None
            
            stats = details['statistics']
            throughput = details.get('throughput', {})
            error_rates = details.get('error_rates', {})
            
            # Calculate packet loss rate
            packets_total = stats.get('packets_sent', 0) + stats.get('packets_recv', 0)
            drops_total = stats.get('drops_in', 0) + stats.get('drops_out', 0)
            packet_loss_rate = (drops_total / max(packets_total, 1)) * 100
            
            # Estimate latency and jitter (simplified)
            latency = await self._estimate_latency(interface_name)
            jitter = await self._estimate_jitter(interface_name)
            
            return NetworkDataPoint(
                timestamp=datetime.utcnow(),
                interface_name=interface_name,
                bytes_sent=stats.get('bytes_sent', 0),
                bytes_received=stats.get('bytes_recv', 0),
                packets_sent=stats.get('packets_sent', 0),
                packets_received=stats.get('packets_recv', 0),
                errors_in=stats.get('errors_in', 0),
                errors_out=stats.get('errors_out', 0),
                drops_in=stats.get('drops_in', 0),
                drops_out=stats.get('drops_out', 0),
                throughput_mbps=throughput.get('total_mbps', 0.0),
                latency_ms=latency,
                jitter_ms=jitter,
                packet_loss_rate=packet_loss_rate
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect data for {interface_name}: {e}")
            return None
    
    async def _estimate_latency(self, interface_name: str) -> float:
        """Estimate network latency (simplified implementation)"""
        try:
            # This is a simplified estimation - in production would use proper ping
            start_time = time.time()
            
            # Simulate a network test
            await asyncio.sleep(0.001)  # 1ms simulated latency
            
            end_time = time.time()
            return (end_time - start_time) * 1000  # Convert to milliseconds
            
        except Exception:
            return 50.0  # Default latency estimate
    
    async def _estimate_jitter(self, interface_name: str) -> float:
        """Estimate network jitter (simplified implementation)"""
        try:
            # Get recent latency measurements for this interface
            if interface_name in self.interface_history:
                recent_data = list(self.interface_history[interface_name])[-5:]  # Last 5 measurements
                if len(recent_data) >= 2:
                    latencies = [data.latency_ms for data in recent_data]
                    return float(np.std(latencies))
            
            return 5.0  # Default jitter estimate
            
        except Exception:
            return 5.0
    
    async def get_recent_data(self, interface_name: Optional[str] = None, 
                            minutes: int = 10) -> List[NetworkDataPoint]:
        """Get recent data points"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        if interface_name:
            # Get data for specific interface
            if interface_name in self.interface_history:
                return [data for data in self.interface_history[interface_name] 
                       if data.timestamp >= cutoff_time]
            else:
                return []
        else:
            # Get data for all interfaces
            return [data for data in self.data_buffer if data.timestamp >= cutoff_time]
    
    async def get_interface_summary(self, interface_name: str) -> Dict[str, Any]:
        """Get summary statistics for an interface"""
        if interface_name not in self.interface_history:
            return {'error': f'No data for interface {interface_name}'}
        
        try:
            data_points = list(self.interface_history[interface_name])
            
            if not data_points:
                return {'error': 'No data points available'}
            
            # Calculate summary statistics
            throughputs = [dp.throughput_mbps for dp in data_points]
            latencies = [dp.latency_ms for dp in data_points]
            packet_loss_rates = [dp.packet_loss_rate for dp in data_points]
            
            summary = {
                'interface_name': interface_name,
                'data_points': len(data_points),
                'time_range': {
                    'start': data_points[0].timestamp.isoformat(),
                    'end': data_points[-1].timestamp.isoformat()
                },
                'throughput': {
                    'avg_mbps': float(np.mean(throughputs)),
                    'max_mbps': float(np.max(throughputs)),
                    'min_mbps': float(np.min(throughputs)),
                    'std_mbps': float(np.std(throughputs))
                },
                'latency': {
                    'avg_ms': float(np.mean(latencies)),
                    'max_ms': float(np.max(latencies)),
                    'min_ms': float(np.min(latencies)),
                    'std_ms': float(np.std(latencies))
                },
                'packet_loss': {
                    'avg_rate': float(np.mean(packet_loss_rates)),
                    'max_rate': float(np.max(packet_loss_rates))
                }
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary for {interface_name}: {e}")
            return {'error': str(e)}
    
    async def collect_all(self) -> Dict[str, Any]:
        """Collect comprehensive network data for AI processing"""
        try:
            # Get current network metrics
            network_metrics = await self.network_utils.collect_comprehensive_metrics()
            
            # Get recent historical data
            recent_data = await self.get_recent_data(minutes=5)
            
            # Combine current and historical data
            collected_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'current_metrics': network_metrics,
                'recent_history': [dp.to_dict() for dp in recent_data[-10:]],  # Last 10 points
                'interface_summaries': {},
                'collection_status': {
                    'is_collecting': self.is_collecting,
                    'total_data_points': len(self.data_buffer),
                    'monitored_interfaces': len(self.interface_history)
                }
            }
            
            # Add interface summaries
            for interface_name in self.interface_history.keys():
                collected_data['interface_summaries'][interface_name] = await self.get_interface_summary(interface_name)
            
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Failed to collect all data: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

class SystemMetricsCollector:
    """Collects system performance metrics"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Data storage
        self.metrics_history = deque(maxlen=1000)
        
        # Collection state
        self.is_collecting = False
        self.collection_task: Optional[asyncio.Task] = None
        self.collection_interval = config.get('system.monitoring_interval', 10)
    
    async def initialize(self):
        """Initialize system metrics collector"""
        self.logger.info("Initializing SystemMetricsCollector...")
        
        try:
            # Collect initial metrics
            initial_metrics = await self.collect_current_metrics()
            if initial_metrics:
                self.metrics_history.append(initial_metrics)
            
            self.logger.info("SystemMetricsCollector initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize SystemMetricsCollector: {e}")
            raise
    
    async def start_collection(self):
        """Start continuous metrics collection"""
        if self.is_collecting:
            return
        
        self.is_collecting = True
        self.collection_task = asyncio.create_task(self._collection_loop())
        self.logger.info("Started system metrics collection")
    
    async def stop_collection(self):
        """Stop metrics collection"""
        if not self.is_collecting:
            return
        
        self.is_collecting = False
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Stopped system metrics collection")
    
    async def _collection_loop(self):
        """Main collection loop for system metrics"""
        while self.is_collecting:
            try:
                metrics = await self.collect_current_metrics()
                if metrics:
                    self.metrics_history.append(metrics)
                
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"System metrics collection error: {e}")
                await asyncio.sleep(self.collection_interval * 2)
    
    async def collect_current_metrics(self) -> Optional[SystemMetrics]:
        """Collect current system metrics"""
        try:
            # CPU metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # Load average (if available)
            try:
                load_avg = list(psutil.getloadavg())
            except AttributeError:
                load_avg = [0.0, 0.0, 0.0]  # Default for systems without getloadavg
            
            # Network connections
            try:
                connections = psutil.net_connections()
                network_connections = len(connections)
            except psutil.AccessDenied:
                network_connections = 0
            
            # Process count
            active_processes = len(psutil.pids())
            
            # System uptime
            uptime_seconds = time.time() - psutil.boot_time()
            
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                load_average=load_avg,
                network_connections=network_connections,
                active_processes=active_processes,
                uptime_seconds=uptime_seconds
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            return None
    
    async def get_recent_metrics(self, minutes: int = 30) -> List[SystemMetrics]:
        """Get recent system metrics"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        return [metrics for metrics in self.metrics_history if metrics.timestamp >= cutoff_time]
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of system metrics"""
        if not self.metrics_history:
            return {'error': 'No metrics data available'}
        
        try:
            metrics_list = list(self.metrics_history)
            
            cpu_values = [m.cpu_usage for m in metrics_list]
            memory_values = [m.memory_usage for m in metrics_list]
            disk_values = [m.disk_usage for m in metrics_list]
            
            summary = {
                'data_points': len(metrics_list),
                'time_range': {
                    'start': metrics_list[0].timestamp.isoformat(),
                    'end': metrics_list[-1].timestamp.isoformat()
                },
                'cpu': {
                    'current': cpu_values[-1],
                    'avg': float(np.mean(cpu_values)),
                    'max': float(np.max(cpu_values)),
                    'min': float(np.min(cpu_values))
                },
                'memory': {
                    'current': memory_values[-1],
                    'avg': float(np.mean(memory_values)),
                    'max': float(np.max(memory_values)),
                    'min': float(np.min(memory_values))
                },
                'disk': {
                    'current': disk_values[-1],
                    'avg': float(np.mean(disk_values)),
                    'max': float(np.max(disk_values)),
                    'min': float(np.min(disk_values))
                },
                'network_connections': metrics_list[-1].network_connections,
                'active_processes': metrics_list[-1].active_processes,
                'uptime_hours': metrics_list[-1].uptime_seconds / 3600
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate metrics summary: {e}")
            return {'error': str(e)}

class TunnelMetricsCollector:
    """Collects metrics specific to tunnel interfaces"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Tunnel-specific data
        self.tunnel_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=500))
        self.active_tunnels = set()
    
    async def initialize(self):
        """Initialize tunnel metrics collector"""
        self.logger.info("Initializing TunnelMetricsCollector...")
        
        try:
            # Detect existing tunnel interfaces
            await self._detect_tunnel_interfaces()
            
            self.logger.info(f"TunnelMetricsCollector initialized with {len(self.active_tunnels)} tunnels")
        except Exception as e:
            self.logger.error(f"Failed to initialize TunnelMetricsCollector: {e}")
            raise
    
    async def _detect_tunnel_interfaces(self):
        """Detect active tunnel interfaces"""
        try:
            interfaces = psutil.net_io_counters(pernic=True)
            
            for interface_name in interfaces.keys():
                if interface_name.startswith(('tun', 'tap', 'wg')):
                    self.active_tunnels.add(interface_name)
                    self.logger.info(f"Detected tunnel interface: {interface_name}")
        
        except Exception as e:
            self.logger.error(f"Failed to detect tunnel interfaces: {e}")
    
    async def store_metrics(self, tunnel_name: str, metrics: Any):
        """Store metrics for a specific tunnel"""
        try:
            # Convert metrics to dictionary if it's an object
            if hasattr(metrics, '__dict__'):
                metrics_dict = asdict(metrics)
            elif hasattr(metrics, 'to_dict'):
                metrics_dict = metrics.to_dict()
            else:
                metrics_dict = dict(metrics) if metrics else {}
            
            # Add timestamp if not present
            if 'timestamp' not in metrics_dict:
                metrics_dict['timestamp'] = datetime.utcnow().isoformat()
            
            # Store in tunnel-specific history
            self.tunnel_metrics[tunnel_name].append(metrics_dict)
            
            # Add to active tunnels set
            self.active_tunnels.add(tunnel_name)
            
        except Exception as e:
            self.logger.error(f"Failed to store metrics for tunnel {tunnel_name}: {e}")
    
    async def get_tunnel_metrics(self, tunnel_name: str) -> List[Dict[str, Any]]:
        """Get metrics for a specific tunnel"""
        if tunnel_name in self.tunnel_metrics:
            return list(self.tunnel_metrics[tunnel_name])
        return []
    
    async def get_all_tunnel_metrics(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get metrics for all tunnels"""
        return {
            tunnel_name: list(metrics_queue)
            for tunnel_name, metrics_queue in self.tunnel_metrics.items()
        }
    
    async def get_tunnel_summary(self) -> Dict[str, Any]:
        """Get summary of all tunnel metrics"""
        summary = {
            'active_tunnels': len(self.active_tunnels),
            'tunnel_names': list(self.active_tunnels),
            'total_data_points': sum(len(metrics) for metrics in self.tunnel_metrics.values()),
            'tunnels': {}
        }
        
        for tunnel_name in self.active_tunnels:
            metrics_list = list(self.tunnel_metrics.get(tunnel_name, []))
            if metrics_list:
                tunnel_summary = {
                    'data_points': len(metrics_list),
                    'last_update': metrics_list[-1].get('timestamp') if metrics_list else None,
                    'metrics_available': list(metrics_list[-1].keys()) if metrics_list else []
                }
                summary['tunnels'][tunnel_name] = tunnel_summary
        
        return summary

class DataCollectorManager:
    """Manages all data collection components"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize collectors
        self.network_collector = NetworkDataCollector(config)
        self.system_collector = SystemMetricsCollector(config)
        self.tunnel_collector = TunnelMetricsCollector(config)
        
        # State management
        self.is_initialized = False
        self.collectors = [
            self.network_collector,
            self.system_collector,
            self.tunnel_collector
        ]
    
    async def initialize_all(self):
        """Initialize all data collectors"""
        self.logger.info("Initializing all data collectors...")
        
        try:
            # Initialize each collector
            for collector in self.collectors:
                await collector.initialize()
            
            self.is_initialized = True
            self.logger.info("All data collectors initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize data collectors: {e}")
            raise
    
    async def start_all_collection(self):
        """Start all data collection processes"""
        if not self.is_initialized:
            await self.initialize_all()
        
        try:
            # Start network and system collectors
            await self.network_collector.start_collection()
            await self.system_collector.start_collection()
            
            self.logger.info("All data collection started")
            
        except Exception as e:
            self.logger.error(f"Failed to start data collection: {e}")
            raise
    
    async def stop_all_collection(self):
        """Stop all data collection processes"""
        try:
            await self.network_collector.stop_collection()
            await self.system_collector.stop_collection()
            
            self.logger.info("All data collection stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop data collection: {e}")
    
    async def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all collectors"""
        try:
            status = {
                'timestamp': datetime.utcnow().isoformat(),
                'initialized': self.is_initialized,
                'network_collector': {
                    'is_collecting': self.network_collector.is_collecting,
                    'data_points': len(self.network_collector.data_buffer),
                    'monitored_interfaces': len(self.network_collector.interface_history)
                },
                'system_collector': {
                    'is_collecting': self.system_collector.is_collecting,
                    'metrics_points': len(self.system_collector.metrics_history)
                },
                'tunnel_collector': {
                    'active_tunnels': len(self.tunnel_collector.active_tunnels),
                    'total_data_points': sum(len(metrics) for metrics in self.tunnel_collector.tunnel_metrics.values())
                }
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get comprehensive status: {e}")
            return {'error': str(e), 'timestamp': datetime.utcnow().isoformat()}
    
    async def collect_all_data(self) -> Dict[str, Any]:
        """Collect data from all collectors"""
        try:
            collected_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'network_data': await self.network_collector.collect_all(),
                'system_metrics': await self.system_collector.get_metrics_summary(),
                'tunnel_data': await self.tunnel_collector.get_tunnel_summary()
            }
            
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Failed to collect all data: {e}")
            return {'error': str(e), 'timestamp': datetime.utcnow().isoformat()}