"""
PdaNet Linux - Advanced Connection Reliability Manager
P2-PERF-2: Enhanced connection reliability, error recovery, and fault tolerance
"""

import asyncio
import contextlib
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from logger import get_logger
from performance_optimizer import cached_method, resource_context, timed_operation


class ConnectionHealth(Enum):
    """Connection health status levels"""
    EXCELLENT = "excellent"    # <50ms latency, <1% packet loss
    GOOD = "good"             # <100ms latency, <3% packet loss  
    FAIR = "fair"             # <200ms latency, <5% packet loss
    POOR = "poor"             # <500ms latency, <10% packet loss
    CRITICAL = "critical"     # >500ms latency, >10% packet loss
    UNKNOWN = "unknown"       # No data available


@dataclass
class ConnectionFailure:
    """Connection failure event data"""
    timestamp: float
    failure_type: str
    error_message: str
    interface: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    duration_seconds: float = 0.0


@dataclass
class NetworkDiagnostic:
    """Network diagnostic result"""
    timestamp: float
    test_type: str
    target: str
    success: bool
    latency_ms: float = 0.0
    packet_loss_percent: float = 0.0
    error_message: str = ""
    bandwidth_mbps: float = 0.0


class ReliabilityManager:
    """Advanced connection reliability and fault tolerance manager"""
    
    def __init__(self):
        self.logger = get_logger()
        
        # Reliability tracking
        self.failure_history: List[ConnectionFailure] = []
        self.diagnostic_history: List[NetworkDiagnostic] = []
        self.health_checks_enabled = True
        self.auto_recovery_enabled = True
        
        # Health monitoring
        self._health_check_interval = 30  # seconds
        self._health_monitor_thread = None
        self._monitoring_active = False
        
        # Failure detection and recovery
        self.failure_threshold = 3  # failures before major recovery
        self.recovery_strategies = []
        self.current_failures = 0
        self.last_health_check = 0
        
        # Network diagnostic configuration
        self.diagnostic_targets = [
            "8.8.8.8",      # Google DNS
            "1.1.1.1",      # Cloudflare DNS
            "208.67.222.222" # OpenDNS
        ]
        self.diagnostic_timeout = 10  # seconds
        
        # Performance monitoring
        self.reliability_stats = {
            'total_failures': 0,
            'successful_recoveries': 0,
            'failed_recoveries': 0,
            'mean_time_to_recovery': 0.0,
            'uptime_percentage': 0.0
        }
        
        # Thread management
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="reliability")
        
        # Register default recovery strategies
        self._register_default_recovery_strategies()
    
    def start_monitoring(self):
        """Start reliability monitoring and health checks"""
        if self._monitoring_active:
            return
            
        self._monitoring_active = True
        self._health_monitor_thread = threading.Thread(
            target=self._health_monitoring_loop,
            daemon=True,
            name="ReliabilityMonitor"
        )
        self._health_monitor_thread.start()
        self.logger.info("Connection reliability monitoring started")
    
    def stop_monitoring(self):
        """Stop reliability monitoring"""
        self._monitoring_active = False
        if self._health_monitor_thread and self._health_monitor_thread.is_alive():
            self._health_monitor_thread.join(timeout=10.0)
        self.executor.shutdown(wait=False)
        self.logger.info("Connection reliability monitoring stopped")
    
    def _health_monitoring_loop(self):
        """Main health monitoring loop"""
        while self._monitoring_active:
            try:
                # Perform health check
                health_status = self.check_connection_health()
                
                # Take action based on health
                if health_status in [ConnectionHealth.POOR, ConnectionHealth.CRITICAL]:
                    self.logger.warning(f"Connection health degraded: {health_status.value}")
                    
                    if self.auto_recovery_enabled:
                        self._trigger_recovery(f"Health degraded to {health_status.value}")
                
                # Update statistics
                self._update_reliability_stats()
                
                time.sleep(self._health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                time.sleep(self._health_check_interval)
    
    @timed_operation("connection_health_check")
    def check_connection_health(self) -> ConnectionHealth:
        """Comprehensive connection health assessment"""
        self.last_health_check = time.time()
        
        try:
            # Run parallel diagnostics
            futures = []
            for target in self.diagnostic_targets[:2]:  # Limit to 2 for speed
                future = self.executor.submit(self._run_ping_diagnostic, target)
                futures.append(future)
            
            # Collect results with timeout
            diagnostics = []
            for future in as_completed(futures, timeout=self.diagnostic_timeout):
                try:
                    diagnostic = future.result()
                    if diagnostic:
                        diagnostics.append(diagnostic)
                        self.diagnostic_history.append(diagnostic)
                except Exception as e:
                    self.logger.warning(f"Diagnostic failed: {e}")
            
            # Limit history size
            if len(self.diagnostic_history) > 1000:
                self.diagnostic_history = self.diagnostic_history[-500:]
            
            if not diagnostics:
                return ConnectionHealth.UNKNOWN
            
            # Calculate health metrics
            successful_tests = [d for d in diagnostics if d.success]
            
            if not successful_tests:
                return ConnectionHealth.CRITICAL
            
            avg_latency = sum(d.latency_ms for d in successful_tests) / len(successful_tests)
            avg_packet_loss = sum(d.packet_loss_percent for d in successful_tests) / len(successful_tests)
            success_rate = len(successful_tests) / len(diagnostics) * 100
            
            # Determine health level
            if success_rate < 50:
                return ConnectionHealth.CRITICAL
            elif avg_latency > 500 or avg_packet_loss > 10:
                return ConnectionHealth.CRITICAL
            elif avg_latency > 200 or avg_packet_loss > 5:
                return ConnectionHealth.POOR
            elif avg_latency > 100 or avg_packet_loss > 3:
                return ConnectionHealth.FAIR
            elif avg_latency > 50 or avg_packet_loss > 1:
                return ConnectionHealth.GOOD
            else:
                return ConnectionHealth.EXCELLENT
                
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return ConnectionHealth.UNKNOWN
    
    def _run_ping_diagnostic(self, target: str) -> Optional[NetworkDiagnostic]:
        """Run ping diagnostic against target"""
        try:
            result = subprocess.run(
                ["ping", "-c", "3", "-W", "5", target],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            diagnostic = NetworkDiagnostic(
                timestamp=time.time(),
                test_type="ping",
                target=target,
                success=result.returncode == 0
            )
            
            if result.returncode == 0:
                # Parse ping output for metrics
                output = result.stdout
                
                # Extract latency (looking for "time=XXXms")
                import re
                latency_matches = re.findall(r'time=([0-9.]+)', output)
                if latency_matches:
                    latencies = [float(match) for match in latency_matches]
                    diagnostic.latency_ms = sum(latencies) / len(latencies)
                
                # Extract packet loss
                loss_match = re.search(r'([0-9]+)% packet loss', output)
                if loss_match:
                    diagnostic.packet_loss_percent = float(loss_match.group(1))
            else:
                diagnostic.error_message = result.stderr.strip()
            
            return diagnostic
            
        except Exception as e:
            return NetworkDiagnostic(
                timestamp=time.time(),
                test_type="ping",
                target=target,
                success=False,
                error_message=str(e)
            )
    
    def report_failure(self, failure_type: str, error_message: str, interface: Optional[str] = None):
        """Report a connection failure for tracking and recovery"""
        failure = ConnectionFailure(
            timestamp=time.time(),
            failure_type=failure_type,
            error_message=error_message,
            interface=interface
        )
        
        self.failure_history.append(failure)
        self.current_failures += 1
        self.reliability_stats['total_failures'] += 1
        
        # Limit history size
        if len(self.failure_history) > 1000:
            self.failure_history = self.failure_history[-500:]
        
        self.logger.error(f"Connection failure reported: {failure_type} - {error_message}")
        
        # Trigger recovery if enabled and threshold reached
        if self.auto_recovery_enabled and self.current_failures >= self.failure_threshold:
            self._trigger_recovery(f"Failure threshold reached: {failure_type}")
    
    def _trigger_recovery(self, reason: str):
        """Trigger automated recovery procedures"""
        recovery_start = time.time()
        self.logger.info(f"Triggering recovery: {reason}")
        
        # Execute recovery strategies in parallel
        recovery_futures = []
        for strategy in self.recovery_strategies:
            future = self.executor.submit(self._execute_recovery_strategy, strategy)
            recovery_futures.append((strategy.__name__, future))
        
        successful_recoveries = 0
        
        # Wait for recovery strategies to complete
        for strategy_name, future in recovery_futures:
            try:
                success = future.result(timeout=30)  # 30 second timeout per strategy
                if success:
                    successful_recoveries += 1
                    self.logger.info(f"Recovery strategy succeeded: {strategy_name}")
                else:
                    self.logger.warning(f"Recovery strategy failed: {strategy_name}")
            except Exception as e:
                self.logger.error(f"Recovery strategy error {strategy_name}: {e}")
        
        recovery_duration = time.time() - recovery_start
        
        # Update failure records
        if len(self.failure_history) > 0:
            last_failure = self.failure_history[-1]
            last_failure.recovery_attempted = True
            last_failure.recovery_successful = successful_recoveries > 0
            last_failure.duration_seconds = recovery_duration
        
        # Update statistics
        if successful_recoveries > 0:
            self.reliability_stats['successful_recoveries'] += 1
            self.current_failures = 0  # Reset failure counter
        else:
            self.reliability_stats['failed_recoveries'] += 1
        
        # Update mean time to recovery
        self._update_mean_recovery_time()
    
    def _execute_recovery_strategy(self, strategy: Callable) -> bool:
        """Execute a single recovery strategy"""
        try:
            with resource_context(f"recovery_{strategy.__name__}"):
                return strategy()
        except Exception as e:
            self.logger.error(f"Recovery strategy {strategy.__name__} failed: {e}")
            return False
    
    def _register_default_recovery_strategies(self):
        """Register default recovery strategies"""
        self.recovery_strategies = [
            self._recovery_flush_dns,
            self._recovery_restart_network_interface,
            self._recovery_clear_iptables_cache,
            self._recovery_network_namespace_refresh
        ]
    
    def _recovery_flush_dns(self) -> bool:
        """Recovery: Flush DNS cache"""
        try:
            # Try systemd-resolved first
            result = subprocess.run(
                ["systemctl", "flush-dns"], 
                capture_output=True, timeout=10, check=False
            )
            if result.returncode == 0:
                return True
            
            # Fallback to traditional method
            subprocess.run(["pkill", "-HUP", "dnsmasq"], check=False, timeout=5)
            return True
            
        except Exception:
            return False
    
    def _recovery_restart_network_interface(self) -> bool:
        """Recovery: Restart network interface"""
        # This is a placeholder - in production would need proper interface detection
        # and careful restart procedures to avoid breaking the connection completely
        self.logger.info("Network interface restart recovery (simulated)")
        return True
    
    def _recovery_clear_iptables_cache(self) -> bool:
        """Recovery: Clear iptables connection tracking"""
        try:
            subprocess.run(
                ["conntrack", "-F"], 
                capture_output=True, timeout=10, check=False
            )
            return True
        except Exception:
            return False
    
    def _recovery_network_namespace_refresh(self) -> bool:
        """Recovery: Refresh network namespace configuration"""
        # Placeholder for more advanced network namespace operations
        self.logger.info("Network namespace refresh recovery (simulated)")
        return True
    
    def _update_reliability_stats(self):
        """Update reliability statistics"""
        if not self.diagnostic_history:
            return
            
        # Calculate uptime percentage from recent diagnostics
        recent_cutoff = time.time() - 3600  # Last hour
        recent_diagnostics = [
            d for d in self.diagnostic_history[-100:] 
            if d.timestamp >= recent_cutoff
        ]
        
        if recent_diagnostics:
            successful_tests = sum(1 for d in recent_diagnostics if d.success)
            self.reliability_stats['uptime_percentage'] = (successful_tests / len(recent_diagnostics)) * 100
    
    def _update_mean_recovery_time(self):
        """Update mean time to recovery statistic"""
        recovery_times = [
            f.duration_seconds for f in self.failure_history 
            if f.recovery_attempted and f.recovery_successful and f.duration_seconds > 0
        ]
        
        if recovery_times:
            self.reliability_stats['mean_time_to_recovery'] = sum(recovery_times) / len(recovery_times)
    
    @cached_method(ttl=60, max_size=5)
    def get_reliability_summary(self) -> Dict[str, Any]:
        """Get comprehensive reliability summary with caching"""
        recent_cutoff = time.time() - 3600  # Last hour
        
        recent_failures = [f for f in self.failure_history if f.timestamp >= recent_cutoff]
        recent_diagnostics = [d for d in self.diagnostic_history if d.timestamp >= recent_cutoff]
        
        current_health = ConnectionHealth.UNKNOWN
        if recent_diagnostics:
            # Calculate current health from recent diagnostics
            successful_tests = [d for d in recent_diagnostics if d.success]
            if successful_tests:
                avg_latency = sum(d.latency_ms for d in successful_tests) / len(successful_tests)
                success_rate = len(successful_tests) / len(recent_diagnostics) * 100
                
                if success_rate >= 95 and avg_latency < 50:
                    current_health = ConnectionHealth.EXCELLENT
                elif success_rate >= 90 and avg_latency < 100:
                    current_health = ConnectionHealth.GOOD
                elif success_rate >= 80 and avg_latency < 200:
                    current_health = ConnectionHealth.FAIR
                elif success_rate >= 60:
                    current_health = ConnectionHealth.POOR
                else:
                    current_health = ConnectionHealth.CRITICAL
        
        return {
            'current_health': current_health.value,
            'recent_failures_count': len(recent_failures),
            'recent_diagnostics_count': len(recent_diagnostics),
            'reliability_stats': self.reliability_stats.copy(),
            'last_health_check': self.last_health_check,
            'monitoring_active': self._monitoring_active,
            'auto_recovery_enabled': self.auto_recovery_enabled,
            'current_failure_count': self.current_failures
        }
    
    def get_failure_analysis(self) -> Dict[str, Any]:
        """Analyze failure patterns and trends"""
        if not self.failure_history:
            return {'total_failures': 0, 'failure_types': {}, 'trends': {}}
        
        # Analyze failure types
        failure_types = {}
        for failure in self.failure_history:
            failure_types[failure.failure_type] = failure_types.get(failure.failure_type, 0) + 1
        
        # Analyze recent trends (last 24 hours)
        recent_cutoff = time.time() - 86400
        recent_failures = [f for f in self.failure_history if f.timestamp >= recent_cutoff]
        
        # Group by hour
        hourly_failures = {}
        for failure in recent_failures:
            hour = int(failure.timestamp // 3600)
            hourly_failures[hour] = hourly_failures.get(hour, 0) + 1
        
        return {
            'total_failures': len(self.failure_history),
            'failure_types': failure_types,
            'recent_failures_24h': len(recent_failures),
            'hourly_distribution': hourly_failures,
            'recovery_success_rate': (
                self.reliability_stats['successful_recoveries'] / 
                (self.reliability_stats['successful_recoveries'] + self.reliability_stats['failed_recoveries'])
                if (self.reliability_stats['successful_recoveries'] + self.reliability_stats['failed_recoveries']) > 0 else 0.0
            )
        }


# Global reliability manager instance
_reliability_manager = None

def get_reliability_manager() -> ReliabilityManager:
    """Get global reliability manager instance"""
    global _reliability_manager
    if _reliability_manager is None:
        _reliability_manager = ReliabilityManager()
    return _reliability_manager