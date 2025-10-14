"""
PdaNet Linux - Performance Optimization Module
P2-PERF: Memory management, caching, and resource optimization
"""

import gc
import threading
import time
import weakref
from collections import defaultdict, deque
from contextlib import contextmanager
from functools import lru_cache, wraps
from typing import Any, Callable, Dict, List, Optional, Tuple

from logger import get_logger


class MemoryOptimizer:
    """Advanced memory optimization and monitoring"""
    
    def __init__(self):
        self.logger = get_logger()
        self._memory_snapshots = deque(maxlen=100)  # Limited memory tracking history
        self._gc_stats = defaultdict(int)
        
    def track_memory_usage(self) -> Dict[str, Any]:
        """Track current memory usage with lightweight profiling"""
        try:
            import psutil
            process = psutil.Process()
            
            memory_info = {
                'rss': process.memory_info().rss,  # Resident Set Size
                'vms': process.memory_info().vms,  # Virtual Memory Size
                'timestamp': time.time(),
                'gc_counts': gc.get_count()
            }
            
            self._memory_snapshots.append(memory_info)
            return memory_info
            
        except ImportError:
            # Fallback when psutil not available
            return {
                'rss': 0,
                'vms': 0,
                'timestamp': time.time(),
                'gc_counts': gc.get_count()
            }
    
    def get_memory_trend(self, minutes: int = 5) -> Dict[str, float]:
        """Get memory usage trend over time"""
        if not self._memory_snapshots:
            return {'growth_rate': 0.0, 'avg_usage': 0.0}
        
        cutoff_time = time.time() - (minutes * 60)
        recent_snapshots = [
            snap for snap in self._memory_snapshots 
            if snap['timestamp'] >= cutoff_time
        ]
        
        if len(recent_snapshots) < 2:
            return {'growth_rate': 0.0, 'avg_usage': recent_snapshots[0]['rss'] if recent_snapshots else 0.0}
        
        # Calculate memory growth rate
        first_snapshot = recent_snapshots[0]
        last_snapshot = recent_snapshots[-1]
        
        time_delta = last_snapshot['timestamp'] - first_snapshot['timestamp']
        memory_delta = last_snapshot['rss'] - first_snapshot['rss']
        
        growth_rate = (memory_delta / time_delta) if time_delta > 0 else 0.0
        avg_usage = sum(snap['rss'] for snap in recent_snapshots) / len(recent_snapshots)
        
        return {
            'growth_rate': growth_rate,  # bytes per second
            'avg_usage': avg_usage,
            'samples': len(recent_snapshots)
        }
    
    def optimize_memory(self) -> Dict[str, Any]:
        """Trigger memory optimization and return results"""
        before_memory = self.track_memory_usage()
        
        # Force garbage collection
        collected = [gc.collect() for _ in range(3)]  # Multiple passes
        
        after_memory = self.track_memory_usage()
        
        freed_bytes = before_memory['rss'] - after_memory['rss']
        
        self._gc_stats['total_collections'] += 1
        self._gc_stats['total_freed'] += max(0, freed_bytes)
        
        result = {
            'freed_bytes': freed_bytes,
            'before_rss': before_memory['rss'],
            'after_rss': after_memory['rss'],
            'collected_objects': sum(collected)
        }
        
        if freed_bytes > 1024 * 1024:  # > 1MB freed
            self.logger.info(f"Memory optimization freed {freed_bytes / 1024 / 1024:.1f}MB")
        
        return result


class SmartCache:
    """Intelligent caching with TTL and memory-aware eviction"""
    
    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.cache = {}
        self.timestamps = {}
        self.hit_count = 0
        self.miss_count = 0
        self.lock = threading.RLock()
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get cached value with TTL check"""
        with self.lock:
            if key not in self.cache:
                self.miss_count += 1
                return default
                
            # Check if expired
            if time.time() - self.timestamps[key] > self.default_ttl:
                del self.cache[key]
                del self.timestamps[key]
                self.miss_count += 1
                return default
                
            self.hit_count += 1
            return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cached value with optional TTL override"""
        with self.lock:
            # Evict oldest entries if at max size
            if len(self.cache) >= self.max_size:
                self._evict_oldest()
                
            self.cache[key] = value
            self.timestamps[key] = time.time()
    
    def _evict_oldest(self) -> None:
        """Evict oldest cache entry"""
        if not self.cache:
            return
            
        oldest_key = min(self.timestamps.keys(), key=lambda k: self.timestamps[k])
        del self.cache[oldest_key]
        del self.timestamps[oldest_key]
    
    def clear_expired(self) -> int:
        """Clear expired entries and return count"""
        with self.lock:
            current_time = time.time()
            expired_keys = [
                key for key, timestamp in self.timestamps.items()
                if current_time - timestamp > self.default_ttl
            ]
            
            for key in expired_keys:
                del self.cache[key]
                del self.timestamps[key]
                
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests) if total_requests > 0 else 0.0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }


class ResourceManager:
    """System resource monitoring and management"""
    
    def __init__(self):
        self.logger = get_logger()
        self.memory_optimizer = MemoryOptimizer()
        self.cache = SmartCache()
        self._monitoring = False
        self._monitor_thread = None
        
    def start_monitoring(self, interval: int = 30):
        """Start background resource monitoring"""
        if self._monitoring:
            return
            
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_resources, 
            args=(interval,),
            daemon=True,
            name="ResourceMonitor"
        )
        self._monitor_thread.start()
        # Only log once at startup, not repeatedly
        if not hasattr(self, '_monitoring_started_logged'):
            self.logger.info(f"Resource monitoring started (interval: {interval}s)")
            self._monitoring_started_logged = True
    
    def stop_monitoring(self):
        """Stop background resource monitoring"""
        if not self._monitoring:
            return
            
        self._monitoring = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)  # Reduced timeout
        
        # Only log once at shutdown, not repeatedly  
        if not hasattr(self, '_monitoring_stopped_logged'):
            self.logger.info("Resource monitoring stopped")
            self._monitoring_stopped_logged = True
    
    def _monitor_resources(self, interval: int):
        """Background resource monitoring loop"""
        while self._monitoring:
            try:
                # Track memory usage
                self.memory_optimizer.track_memory_usage()
                
                # Check memory growth trend (reduce frequency of warnings)
                trend = self.memory_optimizer.get_memory_trend()
                
                # Only warn about memory growth occasionally, not constantly
                if (trend['growth_rate'] > 1024 * 1024 and 
                    not hasattr(self, '_last_memory_warning') or 
                    time.time() - getattr(self, '_last_memory_warning', 0) > 60):  # Max once per minute
                    self.logger.warning(f"High memory growth detected: {trend['growth_rate'] / 1024 / 1024:.1f}MB/s")
                    self._last_memory_warning = time.time()
                    self.memory_optimizer.optimize_memory()
                
                # Clear expired cache entries (reduce logging frequency)
                expired_count = self.cache.clear_expired()
                if (expired_count > 10 and  # Only log if significant cleanup
                    (not hasattr(self, '_last_cache_log') or 
                     time.time() - getattr(self, '_last_cache_log', 0) > 300)):  # Max once per 5 minutes
                    self.logger.debug(f"Cleared {expired_count} expired cache entries")
                    self._last_cache_log = time.time()
                
                time.sleep(interval)
                
            except Exception as e:
                # Reduce error logging frequency
                if (not hasattr(self, '_last_error_log') or 
                    time.time() - getattr(self, '_last_error_log', 0) > 30):  # Max once per 30 seconds
                    self.logger.error(f"Resource monitoring error: {e}")
                    self._last_error_log = time.time()
                time.sleep(interval)
    
    def get_resource_summary(self) -> Dict[str, Any]:
        """Get comprehensive resource usage summary"""
        try:
            import psutil
            process = psutil.Process()
            
            return {
                'memory': {
                    'rss_mb': process.memory_info().rss / 1024 / 1024,
                    'vms_mb': process.memory_info().vms / 1024 / 1024,
                    'percent': process.memory_percent()
                },
                'cpu': {
                    'percent': process.cpu_percent(),
                    'num_threads': process.num_threads()
                },
                'io': {
                    'read_count': process.io_counters().read_count,
                    'write_count': process.io_counters().write_count,
                    'read_bytes': process.io_counters().read_bytes,
                    'write_bytes': process.io_counters().write_bytes
                },
                'cache': self.cache.get_stats(),
                'gc': {
                    'counts': gc.get_count(),
                    'stats': self.memory_optimizer._gc_stats.copy()
                }
            }
        except ImportError:
            return {
                'memory': {'error': 'psutil not available'},
                'cache': self.cache.get_stats(),
                'gc': {'counts': gc.get_count()}
            }


# Performance decorators
def timed_operation(operation_name: str = None):
    """Decorator to time function execution and log slow operations"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = time.time() - start_time
                name = operation_name or f"{func.__module__}.{func.__name__}"
                
                # Log slow operations (>100ms)
                if elapsed > 0.1:
                    logger = get_logger()
                    logger.warning(f"Slow operation: {name} took {elapsed:.3f}s")
                elif elapsed > 0.01:
                    logger = get_logger()
                    logger.debug(f"Operation timing: {name} took {elapsed:.3f}s")
                    
        return wrapper
    return decorator


def cached_method(ttl: int = 300, max_size: int = 100):
    """Method caching decorator with TTL"""
    def decorator(method: Callable) -> Callable:
        cache = SmartCache(default_ttl=ttl, max_size=max_size)
        
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            # Create cache key from method name and arguments
            cache_key = f"{method.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            
            # Try to get cached result
            result = cache.get(cache_key)
            if result is not None:
                return result
                
            # Compute and cache result
            result = method(self, *args, **kwargs)
            cache.set(cache_key, result)
            return result
            
        # Expose cache stats
        wrapper.cache_stats = lambda: cache.get_stats()
        wrapper.clear_cache = lambda: cache.cache.clear() or cache.timestamps.clear()
        
        return wrapper
    return decorator


@contextmanager
def resource_context(name: str = "operation"):
    """Context manager for resource tracking"""
    logger = get_logger()
    optimizer = MemoryOptimizer()
    
    start_memory = optimizer.track_memory_usage()
    start_time = time.time()
    
    try:
        yield
    finally:
        end_time = time.time()
        end_memory = optimizer.track_memory_usage()
        
        elapsed = end_time - start_time
        memory_delta = end_memory['rss'] - start_memory['rss']
        
        if elapsed > 1.0 or abs(memory_delta) > 1024 * 1024:  # >1s or >1MB change
            logger.info(f"Resource usage [{name}]: {elapsed:.3f}s, {memory_delta / 1024:.0f}KB")


# Global resource manager instance
_resource_manager = None

def get_resource_manager() -> ResourceManager:
    """Get global resource manager instance"""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager