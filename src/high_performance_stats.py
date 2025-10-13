"""
PdaNet Linux - High-Performance Statistics Collector
P2-PERF: Enhanced with memory optimization, intelligent caching, and resource management
"""

import json
import subprocess
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from logger import get_logger
from performance_optimizer import (
    cached_method,
    get_resource_manager, 
    resource_context,
    timed_operation
)

CONFIG_DIR = str(Path.home() / ".config" / "pdanet-linux")


class HighPerformanceStatsCollector:
    """Enhanced statistics collector with performance optimizations"""
    
    def __init__(self):
        self._logger = get_logger()
        self.resource_manager = get_resource_manager()
        
        # Session state
        self.start_time = None
        self.bytes_sent = 0
        self.bytes_received = 0
        
        # Optimized rolling windows with memory-efficient deques
        self.rx_history = deque(maxlen=120)  # 2 minutes at 1Hz
        self.tx_history = deque(maxlen=120)
        self.latency_history = deque(maxlen=60)   # 1 minute
        self.packet_loss_history = deque(maxlen=30)  # 30 samples
        
        # Legacy compatibility (optimized)
        self.bytes_sent_history = deque(maxlen=100)  # Limited size
        self.bytes_received_history = deque(maxlen=100)
        
        # Interface tracking with caching
        self.current_interface = None
        self.last_rx_bytes = 0
        self.last_tx_bytes = 0
        self.last_update_time = 0
        
        # Performance metrics
        self._update_count = 0
        self._total_update_time = 0.0
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Start resource monitoring
        self.resource_manager.start_monitoring(interval=60)
    
    def start_session(self):
        """Start a new connection session with performance tracking"""
        with resource_context("session_start"):
            with self._lock:
                self.start_time = time.time()
                self.bytes_sent = 0
                self.bytes_received = 0
                self.rx_history.clear()
                self.tx_history.clear()
                self.latency_history.clear()
                self.packet_loss_history.clear()
                
                # Reset performance counters
                self._update_count = 0
                self._total_update_time = 0.0
                
                if self._logger:
                    self._logger.info("High-performance stats session started")
    
    def stop_session(self):
        """End current session with optimized history saving"""
        with resource_context("session_stop"):
            with self._lock:
                if self.start_time:
                    self._save_session_to_history_optimized()
                self.start_time = None
                
                # Log performance metrics
                if self._update_count > 0:
                    avg_update_time = self._total_update_time / self._update_count
                    self._logger.info(f"Session performance: {self._update_count} updates, "
                                    f"avg {avg_update_time * 1000:.1f}ms per update")
    
    @timed_operation("session_save")
    def _save_session_to_history_optimized(self):
        """Optimized session history saving with batching"""
        if not self.start_time:
            return
            
        try:
            history_file = Path(CONFIG_DIR) / "connection_history.json"
            Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)
            
            session_data = {
                "timestamp": datetime.now().isoformat(),
                "duration": self.get_uptime(),
                "downloaded": self.get_total_downloaded(),
                "uploaded": self.get_total_uploaded(),
                "interface": self.current_interface,
                "avg_latency": self.get_average_latency(),
                "quality_score": self._calculate_quality_score(),
                "performance": {
                    "update_count": self._update_count,
                    "avg_update_time_ms": (self._total_update_time / self._update_count * 1000) if self._update_count > 0 else 0
                }
            }
            
            # Atomic write with backup
            temp_file = history_file.with_suffix('.tmp')
            
            # Load existing history efficiently
            history = self._load_history_efficiently(history_file)
            
            # Add new session and maintain size limit
            history.append(session_data)
            history = history[-200:]  # Keep last 200 sessions (doubled for better history)
            
            # Atomic write
            with open(temp_file, 'w') as f:
                json.dump(history, f, indent=2)
            temp_file.replace(history_file)  # Atomic move
            
            if self._logger:
                self._logger.info(f"Session saved: {session_data['duration']:.1f}s, "
                                f"↓{self._format_bytes(session_data['downloaded'])} "
                                f"↑{self._format_bytes(session_data['uploaded'])}")
                                
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to save session history: {e}")
    
    def _load_history_efficiently(self, history_file: Path) -> List[Dict]:
        """Load history with error recovery and validation"""
        if not history_file.exists():
            return []
            
        try:
            with open(history_file) as f:
                history = json.load(f)
                
            # Validate history structure
            if not isinstance(history, list):
                return []
                
            # Filter out invalid entries
            valid_history = []
            for entry in history:
                if isinstance(entry, dict) and 'timestamp' in entry and 'duration' in entry:
                    valid_history.append(entry)
                    
            return valid_history
            
        except (json.JSONDecodeError, IOError) as e:
            if self._logger:
                self._logger.warning(f"History file corrupted, starting fresh: {e}")
            return []
    
    @timed_operation("bandwidth_update")
    def update_bandwidth(self, interface: str = "usb0"):
        """High-performance bandwidth update with optimized I/O"""
        update_start = time.time()
        
        try:
            with self._lock:
                # Optimized interface stats reading
                rx_bytes, tx_bytes = self._read_interface_stats_optimized(interface)
                if rx_bytes is None or tx_bytes is None:
                    return
                
                current_time = time.time()
                
                if self.last_update_time > 0:
                    time_delta = current_time - self.last_update_time
                    
                    if time_delta > 0:  # Avoid division by zero
                        # Calculate rates efficiently
                        rx_rate = (rx_bytes - self.last_rx_bytes) / time_delta
                        tx_rate = (tx_bytes - self.last_tx_bytes) / time_delta
                        
                        # Update rolling windows (deques are very efficient)
                        self.rx_history.append((current_time, rx_rate))
                        self.tx_history.append((current_time, tx_rate))
                        
                        # Update totals
                        delta_rx = rx_bytes - self.last_rx_bytes
                        delta_tx = tx_bytes - self.last_tx_bytes
                        self.bytes_received += max(0, delta_rx)  # Prevent negative values
                        self.bytes_sent += max(0, delta_tx)
                        
                        # Legacy compatibility (memory-limited)
                        self.bytes_received_history.append((current_time, self.bytes_received))
                        self.bytes_sent_history.append((current_time, self.bytes_sent))
                
                # Update tracking variables
                self.last_rx_bytes = rx_bytes
                self.last_tx_bytes = tx_bytes
                self.last_update_time = current_time
                self.current_interface = interface
                
                # Performance tracking
                self._update_count += 1
                self._total_update_time += time.time() - update_start
                
        except Exception as e:
            if self._logger:
                self._logger.error(f"Bandwidth update failed: {e}")
    
    def _read_interface_stats_optimized(self, interface: str) -> Tuple[Optional[int], Optional[int]]:
        """Optimized interface statistics reading with error handling"""
        try:
            rx_path = f"/sys/class/net/{interface}/statistics/rx_bytes"
            tx_path = f"/sys/class/net/{interface}/statistics/tx_bytes"
            
            # Check existence once
            if not (Path(rx_path).exists() and Path(tx_path).exists()):
                return None, None
            
            # Single read operation for both values
            with open(rx_path) as f:
                rx_bytes = int(f.read().strip())
            with open(tx_path) as f:
                tx_bytes = int(f.read().strip())
                
            return rx_bytes, tx_bytes
            
        except (IOError, ValueError):
            # Interface might have disappeared
            return None, None
    
    @cached_method(ttl=5, max_size=10)  # Cache for 5 seconds
    def get_average_download_rate(self, seconds: int = 10) -> float:
        """Cached average download rate calculation"""
        if not self.rx_history:
            return 0.0
        
        cutoff_time = time.time() - seconds
        recent_rates = [rate for ts, rate in self.rx_history if ts >= cutoff_time]
        
        return sum(recent_rates) / len(recent_rates) if recent_rates else 0.0
    
    @cached_method(ttl=5, max_size=10)  # Cache for 5 seconds
    def get_average_upload_rate(self, seconds: int = 10) -> float:
        """Cached average upload rate calculation"""
        if not self.tx_history:
            return 0.0
            
        cutoff_time = time.time() - seconds
        recent_rates = [rate for ts, rate in self.tx_history if ts >= cutoff_time]
        
        return sum(recent_rates) / len(recent_rates) if recent_rates else 0.0
    
    def get_current_download_rate(self) -> float:
        """Get current download rate (most recent measurement)"""
        return self.rx_history[-1][1] if self.rx_history else 0.0
    
    def get_current_upload_rate(self) -> float:
        """Get current upload rate (most recent measurement)"""
        return self.tx_history[-1][1] if self.tx_history else 0.0
    
    def get_uptime(self) -> float:
        """Get connection uptime in seconds"""
        return time.time() - self.start_time if self.start_time else 0.0
    
    def get_total_downloaded(self) -> int:
        """Get total bytes downloaded this session"""
        return self.bytes_received
    
    def get_total_uploaded(self) -> int:
        """Get total bytes uploaded this session"""
        return self.bytes_sent
    
    @cached_method(ttl=30, max_size=5)  # Cache latency measurements for 30 seconds
    def get_average_latency(self) -> float:
        """Get average latency with intelligent caching"""
        if not self.latency_history:
            return 0.0
        return sum(self.latency_history) / len(self.latency_history)
    
    def get_packet_loss(self) -> float:
        """Get packet loss percentage"""
        if not self.packet_loss_history:
            return 0.0
        return sum(self.packet_loss_history) / len(self.packet_loss_history)
    
    def _calculate_quality_score(self) -> float:
        """Calculate connection quality score (0-100)"""
        if not self.start_time:
            return 0.0
            
        score = 100.0
        
        # Latency penalty
        avg_latency = self.get_average_latency()
        if avg_latency > 0:
            if avg_latency > 200:  # >200ms
                score -= 30
            elif avg_latency > 100:  # >100ms
                score -= 15
            elif avg_latency > 50:   # >50ms
                score -= 5
        
        # Packet loss penalty
        packet_loss = self.get_packet_loss()
        score -= packet_loss * 2  # 2 points per 1% loss
        
        # Uptime bonus
        uptime = self.get_uptime()
        if uptime > 3600:  # >1 hour
            score += 10
        elif uptime > 1800:  # >30 min
            score += 5
        
        return max(0.0, min(100.0, score))
    
    def get_performance_stats(self) -> Dict[str, any]:
        """Get detailed performance statistics"""
        with self._lock:
            cache_stats = {}
            
            # Collect cache statistics from cached methods
            for method_name in ['get_average_download_rate', 'get_average_upload_rate', 'get_average_latency']:
                method = getattr(self, method_name, None)
                if method and hasattr(method, 'cache_stats'):
                    cache_stats[method_name] = method.cache_stats()
            
            return {
                'update_performance': {
                    'total_updates': self._update_count,
                    'total_time': self._total_update_time,
                    'avg_update_time_ms': (self._total_update_time / self._update_count * 1000) if self._update_count > 0 else 0,
                    'updates_per_second': self._update_count / self.get_uptime() if self.get_uptime() > 0 else 0
                },
                'cache_stats': cache_stats,
                'memory_usage': self.resource_manager.get_resource_summary(),
                'data_structures': {
                    'rx_history_size': len(self.rx_history),
                    'tx_history_size': len(self.tx_history),
                    'latency_history_size': len(self.latency_history),
                    'packet_loss_history_size': len(self.packet_loss_history)
                }
            }
    
    @staticmethod
    def _format_bytes(bytes_value: int) -> str:
        """Format bytes in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024:
                return f"{bytes_value:.1f}{unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f}TB"
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            if hasattr(self, 'resource_manager'):
                self.resource_manager.stop_monitoring()
        except:
            pass  # Ignore cleanup errors


# Legacy compatibility function
def get_stats():
    """Get global high-performance stats collector instance"""
    global _stats_instance
    if not hasattr(get_stats, '_stats_instance'):
        get_stats._stats_instance = HighPerformanceStatsCollector()
    return get_stats._stats_instance


# Performance monitoring for existing stats collector
class StatsCollectorWrapper:
    """Wrapper to add performance monitoring to existing StatsCollector"""
    
    def __init__(self, original_collector):
        self.original = original_collector
        self.performance_monitor = get_resource_manager()
        
    def __getattr__(self, name):
        """Delegate to original collector with performance monitoring"""
        attr = getattr(self.original, name)
        
        if callable(attr) and name in ['update_bandwidth', 'start_session', 'stop_session']:
            # Wrap performance-critical methods
            @timed_operation(f"StatsCollector.{name}")
            @resource_context(name)
            def wrapped(*args, **kwargs):
                return attr(*args, **kwargs)
            return wrapped
        
        return attr