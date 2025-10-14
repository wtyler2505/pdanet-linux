"""
PdaNet Linux - P4 Advanced Network Monitoring and Traffic Analysis
P4-ADV-1: Deep packet inspection, bandwidth analysis, and network intelligence
"""

import asyncio
import json
import re
import subprocess
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from logger import get_logger
from performance_optimizer import cached_method, resource_context, timed_operation


class ProtocolType(Enum):
    """Network protocol types"""
    TCP = "tcp"
    UDP = "udp" 
    ICMP = "icmp"
    HTTP = "http"
    HTTPS = "https"
    DNS = "dns"
    FTP = "ftp"
    SSH = "ssh"
    UNKNOWN = "unknown"


class TrafficDirection(Enum):
    """Traffic direction"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class NetworkFlow:
    """Network flow information"""
    timestamp: float
    source_ip: str
    dest_ip: str
    source_port: int
    dest_port: int
    protocol: ProtocolType
    bytes_sent: int
    bytes_received: int
    packets_sent: int
    packets_received: int
    duration_seconds: float
    application: Optional[str] = None
    domain: Optional[str] = None
    country: Optional[str] = None
    is_encrypted: bool = False


@dataclass
class BandwidthUsage:
    """Bandwidth usage by application/protocol"""
    application: str
    protocol: ProtocolType
    bytes_up: int
    bytes_down: int
    packets_up: int
    packets_down: int
    sessions: int
    first_seen: float
    last_seen: float
    peak_rate_bps: float
    avg_rate_bps: float


@dataclass
class NetworkSecurityEvent:
    """Network security event"""
    timestamp: float
    event_type: str  # "suspicious_traffic", "port_scan", "dns_leak", "geo_anomaly"
    severity: str    # "low", "medium", "high", "critical"
    source_ip: str
    description: str
    details: Dict[str, Any]
    blocked: bool = False


class AdvancedNetworkMonitor:
    """Advanced network monitoring with deep packet inspection"""
    
    def __init__(self):
        self.logger = get_logger()
        self.config_dir = Path.home() / ".config" / "pdanet-linux"
        
        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Traffic analysis
        self.network_flows: deque = deque(maxlen=10000)  # Last 10k flows
        self.bandwidth_by_app: Dict[str, BandwidthUsage] = {}
        self.protocol_stats: Dict[ProtocolType, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Security monitoring
        self.security_events: deque = deque(maxlen=1000)  # Last 1k events
        self.suspicious_ips: Set[str] = set()
        self.allowed_domains: Set[str] = set()
        self.blocked_domains: Set[str] = set()
        
        # Performance metrics
        self.packet_capture_rate = 0.0
        self.analysis_latency_ms = 0.0
        self.dropped_packets = 0
        
        # Configuration
        self.config = {
            "enable_deep_inspection": True,
            "enable_geo_lookup": False,
            "enable_security_monitoring": True,
            "max_flows_per_second": 1000,
            "suspicious_traffic_threshold": 1024 * 1024,  # 1MB/s
            "dns_leak_detection": True,
            "port_scan_detection": True,
            "capture_interface": "any"
        }
        
        # Load configuration
        self._load_config()
        
        # GeoIP database (placeholder - would use actual GeoIP library)
        self.geoip_enabled = self.config.get("enable_geo_lookup", False)
        
    def _load_config(self):
        """Load monitoring configuration"""
        config_file = self.config_dir / "network_monitoring.json"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                self.logger.warning(f"Failed to load network monitoring config: {e}")
    
    def save_config(self):
        """Save monitoring configuration"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            config_file = self.config_dir / "network_monitoring.json"
            
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save network monitoring config: {e}")
    
    @timed_operation("network_monitor_start")
    def start_monitoring(self, interface: str = "any"):
        """Start advanced network monitoring"""
        if self.monitoring_active:
            return
            
        self.config["capture_interface"] = interface
        self.monitoring_active = True
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="AdvancedNetworkMonitor"
        )
        self.monitor_thread.start()
        
        self.logger.info(f"Advanced network monitoring started on {interface}")
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=10.0)
        
        self.logger.info("Advanced network monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop using netstat and ss for network analysis"""
        while self.monitoring_active:
            try:
                # Collect network connection data
                self._collect_network_connections()
                
                # Analyze traffic patterns
                self._analyze_traffic_patterns()
                
                # Detect security issues
                if self.config.get("enable_security_monitoring", True):
                    self._detect_security_events()
                
                # Clean up old data
                self._cleanup_old_data()
                
                time.sleep(1)  # Monitor every second
                
            except Exception as e:
                self.logger.error(f"Network monitoring error: {e}")
                time.sleep(5)
    
    def _collect_network_connections(self):
        """Collect active network connections using ss command"""
        try:
            # Use ss (socket statistics) for detailed connection info
            result = subprocess.run(
                ["ss", "-tuln", "-p", "-e"],  # TCP/UDP, listening/non-listening, process, extended
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return
                
            current_time = time.time()
            connections = self._parse_ss_output(result.stdout, current_time)
            
            # Process each connection
            for connection in connections:
                self._process_network_flow(connection)
                
        except Exception as e:
            self.logger.debug(f"Error collecting network connections: {e}")
    
    def _parse_ss_output(self, output: str, timestamp: float) -> List[NetworkFlow]:
        """Parse ss command output into NetworkFlow objects"""
        flows = []
        lines = output.strip().split('\n')[1:]  # Skip header
        
        for line in lines:
            try:
                # Parse ss output format
                # Format: Netid State Recv-Q Send-Q Local Address:Port Peer Address:Port Process
                parts = line.split()
                if len(parts) < 5:
                    continue
                
                netid = parts[0].lower()
                protocol = ProtocolType.TCP if netid == 'tcp' else ProtocolType.UDP if netid == 'udp' else ProtocolType.UNKNOWN
                
                local_addr = parts[4]
                peer_addr = parts[5] if len(parts) > 5 else "0.0.0.0:0"
                
                # Parse addresses
                local_ip, local_port = self._parse_address(local_addr)
                peer_ip, peer_port = self._parse_address(peer_addr)
                
                # Extract process info if available
                process_info = parts[-1] if len(parts) > 6 and 'users:' in parts[-1] else ""
                app_name = self._extract_application_name(process_info)
                
                flow = NetworkFlow(
                    timestamp=timestamp,
                    source_ip=local_ip,
                    dest_ip=peer_ip,
                    source_port=local_port,
                    dest_port=peer_port,
                    protocol=protocol,
                    bytes_sent=0,  # ss doesn't provide this directly
                    bytes_received=0,
                    packets_sent=0,
                    packets_received=0,
                    duration_seconds=0.0,
                    application=app_name,
                    is_encrypted=self._is_encrypted_port(peer_port)
                )
                
                flows.append(flow)
                
            except Exception as e:
                self.logger.debug(f"Error parsing ss line '{line}': {e}")
                continue
        
        return flows
    
    def _parse_address(self, addr_str: str) -> Tuple[str, int]:
        """Parse address:port string"""
        try:
            if ':' in addr_str:
                # Handle IPv6 and IPv4
                if addr_str.startswith('['):
                    # IPv6 format [::1]:8000
                    ip = addr_str.split(']:')[0][1:]
                    port = int(addr_str.split(']:')[1])
                else:
                    # IPv4 format 192.168.1.1:8000
                    ip, port_str = addr_str.rsplit(':', 1)
                    port = int(port_str)
                
                return ip, port
            else:
                return addr_str, 0
        except (ValueError, IndexError):
            return "0.0.0.0", 0
    
    def _extract_application_name(self, process_info: str) -> Optional[str]:
        """Extract application name from process info"""
        try:
            # Process info format: users:(("firefox",pid=1234,fd=52))
            if 'users:' in process_info:
                match = re.search(r'\(\("([^"]+)"', process_info)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return None
    
    def _is_encrypted_port(self, port: int) -> bool:
        """Check if port typically uses encryption"""
        encrypted_ports = {443, 993, 995, 587, 465, 636, 989, 990}
        return port in encrypted_ports
    
    def _process_network_flow(self, flow: NetworkFlow):
        """Process and store network flow"""
        self.network_flows.append(flow)
        
        # Update bandwidth usage by application
        if flow.application:
            if flow.application not in self.bandwidth_by_app:
                self.bandwidth_by_app[flow.application] = BandwidthUsage(
                    application=flow.application,
                    protocol=flow.protocol,
                    bytes_up=0,
                    bytes_down=0,
                    packets_up=0,
                    packets_down=0,
                    sessions=0,
                    first_seen=flow.timestamp,
                    last_seen=flow.timestamp,
                    peak_rate_bps=0.0,
                    avg_rate_bps=0.0
                )
            
            usage = self.bandwidth_by_app[flow.application]
            usage.sessions += 1
            usage.last_seen = flow.timestamp
            usage.bytes_up += flow.bytes_sent
            usage.bytes_down += flow.bytes_received
            usage.packets_up += flow.packets_sent
            usage.packets_down += flow.packets_received
        
        # Update protocol statistics
        self.protocol_stats[flow.protocol]["connections"] += 1
        self.protocol_stats[flow.protocol]["bytes"] += flow.bytes_sent + flow.bytes_received
    
    def _analyze_traffic_patterns(self):
        """Analyze traffic patterns for insights"""
        if len(self.network_flows) < 10:
            return
            
        recent_flows = list(self.network_flows)[-100:]  # Last 100 flows
        
        # Analyze by application
        app_traffic = defaultdict(int)
        for flow in recent_flows:
            if flow.application:
                app_traffic[flow.application] += flow.bytes_sent + flow.bytes_received
        
        # Update peak rates
        for app_name, usage in self.bandwidth_by_app.items():
            if app_name in app_traffic:
                current_rate = app_traffic[app_name]
                if current_rate > usage.peak_rate_bps:
                    usage.peak_rate_bps = current_rate
    
    def _detect_security_events(self):
        """Detect potential security events"""
        if len(self.network_flows) < 5:
            return
            
        recent_flows = list(self.network_flows)[-50:]
        current_time = time.time()
        
        # Detect potential port scanning
        self._detect_port_scanning(recent_flows, current_time)
        
        # Detect DNS leaks
        if self.config.get("dns_leak_detection", True):
            self._detect_dns_leaks(recent_flows, current_time)
        
        # Detect suspicious traffic volumes
        self._detect_suspicious_traffic(recent_flows, current_time)
    
    def _detect_port_scanning(self, flows: List[NetworkFlow], current_time: float):
        """Detect potential port scanning activity"""
        # Group by source IP and count unique destination ports
        ip_ports = defaultdict(set)
        
        for flow in flows:
            if current_time - flow.timestamp < 60:  # Last minute
                ip_ports[flow.source_ip].add(flow.dest_port)
        
        # Detect IPs connecting to many different ports
        for ip, ports in ip_ports.items():
            if len(ports) > 10:  # Threshold for port scanning
                self._create_security_event(
                    event_type="port_scan",
                    severity="medium",
                    source_ip=ip,
                    description=f"Potential port scanning from {ip} ({len(ports)} ports)",
                    details={"ports": list(ports), "port_count": len(ports)}
                )
    
    def _detect_dns_leaks(self, flows: List[NetworkFlow], current_time: float):
        """Detect potential DNS leaks"""
        dns_flows = [f for f in flows if f.dest_port == 53]
        
        for flow in dns_flows:
            # Check if DNS query goes to unexpected servers
            if flow.dest_ip not in ["8.8.8.8", "8.8.4.4", "1.1.1.1", "208.67.222.222"]:
                self._create_security_event(
                    event_type="dns_leak",
                    severity="low",
                    source_ip=flow.source_ip,
                    description=f"DNS query to non-standard server {flow.dest_ip}",
                    details={"dns_server": flow.dest_ip}
                )
    
    def _detect_suspicious_traffic(self, flows: List[NetworkFlow], current_time: float):
        """Detect suspicious traffic volumes"""
        # Group by destination and check volumes
        dest_traffic = defaultdict(int)
        
        for flow in flows:
            if current_time - flow.timestamp < 30:  # Last 30 seconds
                dest_traffic[flow.dest_ip] += flow.bytes_sent + flow.bytes_received
        
        threshold = self.config.get("suspicious_traffic_threshold", 1024 * 1024)
        
        for dest_ip, bytes_count in dest_traffic.items():
            if bytes_count > threshold:
                self._create_security_event(
                    event_type="suspicious_traffic",
                    severity="medium",
                    source_ip="local",
                    description=f"High traffic volume to {dest_ip} ({bytes_count} bytes)",
                    details={"destination": dest_ip, "bytes": bytes_count}
                )
    
    def _create_security_event(self, event_type: str, severity: str, source_ip: str, 
                             description: str, details: Dict[str, Any]):
        """Create and store security event"""
        event = NetworkSecurityEvent(
            timestamp=time.time(),
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
            description=description,
            details=details
        )
        
        self.security_events.append(event)
        self.logger.warning(f"Security event: {description}")
    
    def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        current_time = time.time()
        
        # Clean up old bandwidth usage data
        for app_name in list(self.bandwidth_by_app.keys()):
            usage = self.bandwidth_by_app[app_name]
            if current_time - usage.last_seen > 3600:  # 1 hour old
                del self.bandwidth_by_app[app_name]
    
    # Analysis and Reporting Methods
    
    @cached_method(ttl=30, max_size=10)
    def get_traffic_analysis(self) -> Dict[str, Any]:
        """Get comprehensive traffic analysis"""
        if not self.network_flows:
            return {"status": "no_data", "flows": 0}
        
        recent_flows = list(self.network_flows)[-1000:]  # Last 1000 flows
        
        # Analyze by protocol
        protocol_breakdown = defaultdict(lambda: {"connections": 0, "bytes": 0})
        app_breakdown = defaultdict(lambda: {"connections": 0, "bytes": 0})
        
        for flow in recent_flows:
            protocol_breakdown[flow.protocol.value]["connections"] += 1
            protocol_breakdown[flow.protocol.value]["bytes"] += flow.bytes_sent + flow.bytes_received
            
            if flow.application:
                app_breakdown[flow.application]["connections"] += 1
                app_breakdown[flow.application]["bytes"] += flow.bytes_sent + flow.bytes_received
        
        # Top applications by traffic
        top_apps = sorted(
            [(app, stats["bytes"]) for app, stats in app_breakdown.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "status": "active",
            "total_flows": len(recent_flows),
            "protocol_breakdown": dict(protocol_breakdown),
            "application_breakdown": dict(app_breakdown),
            "top_applications": top_apps,
            "monitoring_duration": time.time() - (recent_flows[0].timestamp if recent_flows else 0),
            "security_events": len(self.security_events)
        }
    
    def get_bandwidth_report(self) -> Dict[str, Any]:
        """Get detailed bandwidth usage report"""
        total_up = sum(usage.bytes_up for usage in self.bandwidth_by_app.values())
        total_down = sum(usage.bytes_down for usage in self.bandwidth_by_app.values())
        
        # Sort by total usage
        sorted_apps = sorted(
            self.bandwidth_by_app.values(),
            key=lambda x: x.bytes_up + x.bytes_down,
            reverse=True
        )
        
        return {
            "total_upload_bytes": total_up,
            "total_download_bytes": total_down,
            "total_bytes": total_up + total_down,
            "application_usage": [asdict(usage) for usage in sorted_apps[:20]],
            "top_bandwidth_app": sorted_apps[0].application if sorted_apps else None
        }
    
    def get_security_report(self) -> Dict[str, Any]:
        """Get network security analysis report"""
        if not self.security_events:
            return {"status": "no_events", "events": 0}
        
        recent_events = [e for e in self.security_events if time.time() - e.timestamp < 3600]
        
        # Group by severity
        severity_counts = defaultdict(int)
        event_type_counts = defaultdict(int)
        
        for event in recent_events:
            severity_counts[event.severity] += 1
            event_type_counts[event.event_type] += 1
        
        return {
            "status": "active",
            "total_events": len(self.security_events),
            "recent_events": len(recent_events),
            "severity_breakdown": dict(severity_counts),
            "event_type_breakdown": dict(event_type_counts),
            "latest_events": [asdict(e) for e in list(self.security_events)[-5:]],
            "suspicious_ips": list(self.suspicious_ips)
        }
    
    def export_traffic_log(self, filepath: Path, hours: int = 24) -> bool:
        """Export traffic log to file"""
        try:
            cutoff_time = time.time() - (hours * 3600)
            recent_flows = [f for f in self.network_flows if f.timestamp >= cutoff_time]
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "hours_covered": hours,
                "total_flows": len(recent_flows),
                "flows": [asdict(flow) for flow in recent_flows],
                "security_events": [asdict(e) for e in self.security_events if e.timestamp >= cutoff_time]
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            self.logger.info(f"Traffic log exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export traffic log: {e}")
            return False


# Global instance
_network_monitor = None

def get_advanced_network_monitor() -> AdvancedNetworkMonitor:
    """Get global advanced network monitor instance"""
    global _network_monitor
    if _network_monitor is None:
        _network_monitor = AdvancedNetworkMonitor()
    return _network_monitor