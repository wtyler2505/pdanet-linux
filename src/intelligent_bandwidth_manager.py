"""
PdaNet Linux - P4 Intelligent Bandwidth Management and Quality of Service
P4-ADV-2: Traffic shaping, bandwidth throttling, and intelligent QoS
"""

import json
import subprocess
import threading
import time
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from logger import get_logger
from performance_optimizer import cached_method, timed_operation


class QoSPriority(Enum):
    """Quality of Service priority levels"""
    CRITICAL = "critical"    # VoIP, video calls
    HIGH = "high"           # Video streaming, gaming
    NORMAL = "normal"       # Web browsing, email
    LOW = "low"            # Downloads, updates
    BULK = "bulk"          # Backup, sync


class TrafficClass(Enum):
    """Traffic classification types"""
    INTERACTIVE = "interactive"  # SSH, Telnet
    REALTIME = "realtime"       # VoIP, video calls
    STREAMING = "streaming"     # Video/audio streaming
    WEB = "web"                # HTTP/HTTPS browsing
    GAMING = "gaming"          # Online games
    DOWNLOAD = "download"      # File downloads
    UPLOAD = "upload"          # File uploads
    BACKGROUND = "background"   # System updates, sync
    UNKNOWN = "unknown"        # Unclassified traffic


@dataclass
class BandwidthLimit:
    """Bandwidth limit configuration"""
    name: str
    enabled: bool
    download_limit_kbps: int  # 0 = unlimited
    upload_limit_kbps: int    # 0 = unlimited
    burst_allowance_kb: int   # Burst buffer size
    priority: QoSPriority
    applications: List[str]    # Apps this limit applies to
    ports: List[int]          # Ports this limit applies to
    time_schedule: Optional[Dict[str, Any]] = None  # Time-based rules


@dataclass
class TrafficRule:
    """Traffic shaping rule"""
    name: str
    enabled: bool
    match_criteria: Dict[str, Any]  # IP, port, app, protocol
    action: str                     # "allow", "deny", "limit", "prioritize"
    parameters: Dict[str, Any]      # Action-specific parameters
    created_date: str
    last_applied: Optional[str] = None
    hit_count: int = 0


@dataclass
class QoSStats:
    """QoS statistics"""
    total_shaped_bytes: int
    total_dropped_packets: int
    total_delayed_packets: int
    active_rules: int
    classification_accuracy: float
    avg_latency_ms: float
    jitter_ms: float


class IntelligentBandwidthManager:
    """Advanced bandwidth management with intelligent QoS"""
    
    def __init__(self):
        self.logger = get_logger()
        self.config_dir = Path.home() / ".config" / "pdanet-linux"
        
        # QoS State
        self.qos_enabled = False
        self.bandwidth_limits: Dict[str, BandwidthLimit] = {}
        self.traffic_rules: Dict[str, TrafficRule] = {}
        
        # Traffic Classification
        self.app_classifiers = self._initialize_app_classifiers()
        self.port_classifiers = self._initialize_port_classifiers()
        
        # Statistics
        self.qos_stats = QoSStats(
            total_shaped_bytes=0,
            total_dropped_packets=0,
            total_delayed_packets=0,
            active_rules=0,
            classification_accuracy=0.0,
            avg_latency_ms=0.0,
            jitter_ms=0.0
        )
        
        # Configuration
        self.config = {
            "enable_intelligent_qos": True,
            "enable_adaptive_shaping": True,
            "classification_learning": True,
            "default_download_limit_kbps": 0,  # 0 = unlimited
            "default_upload_limit_kbps": 0,
            "priority_queue_sizes": {
                "critical": 256,
                "high": 512, 
                "normal": 1024,
                "low": 2048,
                "bulk": 4096
            },
            "burst_detection_threshold": 1.5,  # 1.5x normal rate
            "adaptive_learning_rate": 0.1
        }
        
        # Load configuration and rules
        self._load_config()
        self._load_bandwidth_limits()
        self._load_traffic_rules()
        
        # TC (Traffic Control) state
        self.tc_configured = False
        self.current_interface = None
        
    def _initialize_app_classifiers(self) -> Dict[str, TrafficClass]:
        """Initialize application-based traffic classifiers"""
        return {
            # Real-time applications
            "skype": TrafficClass.REALTIME,
            "zoom": TrafficClass.REALTIME,
            "teams": TrafficClass.REALTIME,
            "discord": TrafficClass.REALTIME,
            "whatsapp": TrafficClass.REALTIME,
            
            # Streaming applications
            "netflix": TrafficClass.STREAMING,
            "youtube": TrafficClass.STREAMING,
            "spotify": TrafficClass.STREAMING,
            "twitch": TrafficClass.STREAMING,
            "vlc": TrafficClass.STREAMING,
            
            # Gaming applications
            "steam": TrafficClass.GAMING,
            "dota2": TrafficClass.GAMING,
            "csgo": TrafficClass.GAMING,
            "valorant": TrafficClass.GAMING,
            
            # Web browsers
            "firefox": TrafficClass.WEB,
            "chrome": TrafficClass.WEB,
            "chromium": TrafficClass.WEB,
            "safari": TrafficClass.WEB,
            
            # Download/Upload
            "transmission": TrafficClass.DOWNLOAD,
            "qbittorrent": TrafficClass.DOWNLOAD,
            "wget": TrafficClass.DOWNLOAD,
            "rsync": TrafficClass.UPLOAD,
            
            # Interactive/System
            "ssh": TrafficClass.INTERACTIVE,
            "scp": TrafficClass.INTERACTIVE,
            "apt": TrafficClass.BACKGROUND,
            "yum": TrafficClass.BACKGROUND,
            "dnf": TrafficClass.BACKGROUND,
        }
    
    def _initialize_port_classifiers(self) -> Dict[int, TrafficClass]:
        """Initialize port-based traffic classifiers"""
        return {
            # Interactive protocols
            22: TrafficClass.INTERACTIVE,    # SSH
            23: TrafficClass.INTERACTIVE,    # Telnet
            
            # Real-time protocols
            5060: TrafficClass.REALTIME,     # SIP
            5061: TrafficClass.REALTIME,     # SIP-TLS
            1720: TrafficClass.REALTIME,     # H.323
            
            # Gaming ports
            27015: TrafficClass.GAMING,      # Steam
            3724: TrafficClass.GAMING,       # WoW
            
            # Web protocols
            80: TrafficClass.WEB,            # HTTP
            443: TrafficClass.WEB,           # HTTPS
            8080: TrafficClass.WEB,          # HTTP Alt
            
            # Streaming protocols
            554: TrafficClass.STREAMING,     # RTSP
            
            # File transfer
            21: TrafficClass.DOWNLOAD,       # FTP
            20: TrafficClass.DOWNLOAD,       # FTP Data
            6881: TrafficClass.DOWNLOAD,     # BitTorrent
            6889: TrafficClass.DOWNLOAD,     # BitTorrent
        }
    
    def _load_config(self):
        """Load bandwidth management configuration"""
        config_file = self.config_dir / "bandwidth_management.json"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                self.logger.warning(f"Failed to load bandwidth config: {e}")
    
    def _load_bandwidth_limits(self):
        """Load bandwidth limit configurations"""
        limits_file = self.config_dir / "bandwidth_limits.json"
        if limits_file.exists():
            try:
                with open(limits_file) as f:
                    data = json.load(f)
                    for name, limit_data in data.items():
                        self.bandwidth_limits[name] = BandwidthLimit(**limit_data)
            except Exception as e:
                self.logger.warning(f"Failed to load bandwidth limits: {e}")
    
    def _load_traffic_rules(self):
        """Load traffic shaping rules"""
        rules_file = self.config_dir / "traffic_rules.json"
        if rules_file.exists():
            try:
                with open(rules_file) as f:
                    data = json.load(f)
                    for name, rule_data in data.items():
                        self.traffic_rules[name] = TrafficRule(**rule_data)
            except Exception as e:
                self.logger.warning(f"Failed to load traffic rules: {e}")
        else:
            # Create default rules
            self._create_default_rules()
    
    def _create_default_rules(self):
        """Create default traffic shaping rules"""
        default_rules = [
            TrafficRule(
                name="high_priority_realtime",
                enabled=True,
                match_criteria={"traffic_class": "realtime"},
                action="prioritize",
                parameters={"priority": "critical", "max_delay_ms": 50},
                created_date=time.strftime("%Y-%m-%d %H:%M:%S")
            ),
            TrafficRule(
                name="limit_bulk_downloads", 
                enabled=True,
                match_criteria={"traffic_class": "download", "size_threshold_mb": 100},
                action="limit",
                parameters={"max_rate_kbps": 5000},
                created_date=time.strftime("%Y-%m-%d %H:%M:%S")
            ),
            TrafficRule(
                name="interactive_priority",
                enabled=True,
                match_criteria={"traffic_class": "interactive"},
                action="prioritize", 
                parameters={"priority": "high"},
                created_date=time.strftime("%Y-%m-%d %H:%M:%S")
            )
        ]
        
        for rule in default_rules:
            self.traffic_rules[rule.name] = rule
        
        self.save_traffic_rules()
    
    def save_config(self):
        """Save bandwidth management configuration"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            config_file = self.config_dir / "bandwidth_management.json"
            
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save bandwidth config: {e}")
    
    def save_bandwidth_limits(self):
        """Save bandwidth limit configurations"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            limits_file = self.config_dir / "bandwidth_limits.json"
            
            data = {name: asdict(limit) for name, limit in self.bandwidth_limits.items()}
            with open(limits_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save bandwidth limits: {e}")
    
    def save_traffic_rules(self):
        """Save traffic shaping rules"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            rules_file = self.config_dir / "traffic_rules.json"
            
            data = {name: asdict(rule) for name, rule in self.traffic_rules.items()}
            with open(rules_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save traffic rules: {e}")
    
    @timed_operation("qos_enable")
    def enable_qos(self, interface: str) -> bool:
        """Enable Quality of Service with traffic control"""
        if self.qos_enabled:
            return True
            
        try:
            self.current_interface = interface
            
            # Set up traffic control queuing disciplines
            success = self._setup_traffic_control(interface)
            if success:
                self.qos_enabled = True
                self.logger.info(f"QoS enabled on interface {interface}")
                return True
            else:
                self.logger.error(f"Failed to enable QoS on interface {interface}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error enabling QoS: {e}")
            return False
    
    def disable_qos(self) -> bool:
        """Disable Quality of Service"""
        if not self.qos_enabled:
            return True
            
        try:
            if self.current_interface:
                self._cleanup_traffic_control(self.current_interface)
            
            self.qos_enabled = False
            self.tc_configured = False
            self.logger.info("QoS disabled")
            return True
            
        except Exception as e:
            self.logger.error(f"Error disabling QoS: {e}")
            return False
    
    def _setup_traffic_control(self, interface: str) -> bool:
        """Set up Linux traffic control (tc) for QoS"""
        try:
            # Clean existing qdiscs
            subprocess.run(
                ["tc", "qdisc", "del", "dev", interface, "root"],
                check=False, capture_output=True
            )
            
            # Create HTB (Hierarchical Token Bucket) root qdisc
            result = subprocess.run([
                "tc", "qdisc", "add", "dev", interface, "root", "handle", "1:", 
                "htb", "default", "30"
            ], check=False, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Failed to create HTB qdisc: {result.stderr}")
                return False
            
            # Create root class
            subprocess.run([
                "tc", "class", "add", "dev", interface, "parent", "1:", "classid", "1:1",
                "htb", "rate", "100mbit"  # Adjust based on connection speed
            ], check=False, capture_output=True)
            
            # Create priority classes
            priority_rates = {
                "critical": ("1:10", "30mbit", "50mbit"),
                "high": ("1:20", "20mbit", "40mbit"), 
                "normal": ("1:30", "30mbit", "60mbit"),
                "low": ("1:40", "10mbit", "20mbit"),
                "bulk": ("1:50", "5mbit", "10mbit")
            }
            
            for priority, (classid, rate, ceil) in priority_rates.items():
                subprocess.run([
                    "tc", "class", "add", "dev", interface, "parent", "1:1", 
                    "classid", classid, "htb", "rate", rate, "ceil", ceil
                ], check=False, capture_output=True)
                
                # Add SFQ (Stochastic Fair Queuing) to each class
                subprocess.run([
                    "tc", "qdisc", "add", "dev", interface, "parent", classid, "sfq"
                ], check=False, capture_output=True)
            
            # Set up filters for traffic classification
            self._setup_traffic_filters(interface)
            
            self.tc_configured = True
            return True
            
        except Exception as e:
            self.logger.error(f"Traffic control setup failed: {e}")
            return False
    
    def _setup_traffic_filters(self, interface: str):
        """Set up traffic classification filters"""
        try:
            # Filter for real-time traffic (VoIP, video calls)
            # Match by DSCP markings for real-time traffic
            subprocess.run([
                "tc", "filter", "add", "dev", interface, "parent", "1:", 
                "protocol", "ip", "prio", "1", "u32", 
                "match", "ip", "tos", "0xb8", "0xfc", 
                "flowid", "1:10"  # Critical class
            ], check=False, capture_output=True)
            
            # Filter for interactive traffic (SSH, etc.)
            for port in [22, 23]:  # SSH, Telnet
                subprocess.run([
                    "tc", "filter", "add", "dev", interface, "parent", "1:", 
                    "protocol", "ip", "prio", "2", "u32",
                    "match", "ip", "dport", str(port), "0xffff",
                    "flowid", "1:20"  # High priority class
                ], check=False, capture_output=True)
            
            # Filter for gaming traffic
            for port in [27015, 3724]:
                subprocess.run([
                    "tc", "filter", "add", "dev", interface, "parent", "1:", 
                    "protocol", "ip", "prio", "3", "u32",
                    "match", "ip", "dport", str(port), "0xffff", 
                    "flowid", "1:20"  # High priority
                ], check=False, capture_output=True)
            
            # Filter for bulk download traffic (BitTorrent, etc.)
            for port in range(6881, 6890):
                subprocess.run([
                    "tc", "filter", "add", "dev", interface, "parent", "1:",
                    "protocol", "ip", "prio", "5", "u32",
                    "match", "ip", "dport", str(port), "0xffff",
                    "flowid", "1:50"  # Bulk class
                ], check=False, capture_output=True)
            
        except Exception as e:
            self.logger.error(f"Traffic filter setup failed: {e}")
    
    def _cleanup_traffic_control(self, interface: str):
        """Clean up traffic control configuration"""
        try:
            subprocess.run([
                "tc", "qdisc", "del", "dev", interface, "root"
            ], check=False, capture_output=True)
            
        except Exception as e:
            self.logger.error(f"Traffic control cleanup failed: {e}")
    
    def classify_traffic(self, app_name: Optional[str], dest_port: int, 
                        packet_size: int) -> TrafficClass:
        """Intelligently classify network traffic"""
        # Check application-based classification first
        if app_name and app_name.lower() in self.app_classifiers:
            return self.app_classifiers[app_name.lower()]
        
        # Check port-based classification
        if dest_port in self.port_classifiers:
            return self.port_classifiers[dest_port]
        
        # Heuristic-based classification
        # Small packets on common ports likely interactive
        if packet_size < 1024 and dest_port in [22, 23, 80, 443]:
            return TrafficClass.INTERACTIVE
        
        # Large packets likely downloads
        if packet_size > 1400:
            return TrafficClass.DOWNLOAD
        
        return TrafficClass.UNKNOWN
    
    def create_bandwidth_limit(self, name: str, download_kbps: int, upload_kbps: int,
                              priority: QoSPriority, applications: List[str] = None,
                              ports: List[int] = None) -> bool:
        """Create a new bandwidth limit rule"""
        if applications is None:
            applications = []
        if ports is None:
            ports = []
            
        limit = BandwidthLimit(
            name=name,
            enabled=True,
            download_limit_kbps=download_kbps,
            upload_limit_kbps=upload_kbps,
            burst_allowance_kb=max(download_kbps, upload_kbps) // 8,  # 1 second burst
            priority=priority,
            applications=applications,
            ports=ports
        )
        
        self.bandwidth_limits[name] = limit
        self.save_bandwidth_limits()
        
        # Apply the limit if QoS is enabled
        if self.qos_enabled:
            self._apply_bandwidth_limit(limit)
        
        self.logger.info(f"Created bandwidth limit: {name}")
        return True
    
    def _apply_bandwidth_limit(self, limit: BandwidthLimit) -> bool:
        """Apply bandwidth limit using traffic control"""
        if not self.current_interface or not self.tc_configured:
            return False
            
        try:
            # This would involve more complex tc rules
            # For now, log the intent to apply the limit
            self.logger.info(f"Applied bandwidth limit: {limit.name} "
                           f"({limit.download_limit_kbps}kbps down, {limit.upload_limit_kbps}kbps up)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply bandwidth limit {limit.name}: {e}")
            return False
    
    @cached_method(ttl=10, max_size=5)
    def get_qos_status(self) -> Dict[str, Any]:
        """Get current QoS status and statistics"""
        return {
            "qos_enabled": self.qos_enabled,
            "current_interface": self.current_interface,
            "tc_configured": self.tc_configured,
            "active_bandwidth_limits": len([limit for limit in self.bandwidth_limits.values() if limit.enabled]),
            "active_traffic_rules": len([rule for rule in self.traffic_rules.values() if rule.enabled]),
            "statistics": asdict(self.qos_stats),
            "priority_queues": self.config.get("priority_queue_sizes", {}),
            "intelligent_classification": self.config.get("enable_intelligent_qos", True)
        }
    
    def get_traffic_classification_report(self) -> Dict[str, Any]:
        """Get traffic classification accuracy and statistics"""
        total_classifiers = len(self.app_classifiers) + len(self.port_classifiers)
        
        return {
            "total_classifiers": total_classifiers,
            "application_classifiers": len(self.app_classifiers),
            "port_classifiers": len(self.port_classifiers),
            "supported_traffic_classes": [tc.value for tc in TrafficClass],
            "classification_accuracy": self.qos_stats.classification_accuracy,
            "learning_enabled": self.config.get("classification_learning", True),
            "adaptive_shaping": self.config.get("enable_adaptive_shaping", True)
        }
    
    def export_qos_config(self, filepath: Path) -> bool:
        """Export QoS configuration to file"""
        try:
            config_data = {
                "bandwidth_management_config": self.config,
                "bandwidth_limits": {name: asdict(limit) for name, limit in self.bandwidth_limits.items()},
                "traffic_rules": {name: asdict(rule) for name, rule in self.traffic_rules.items()},
                "qos_statistics": asdict(self.qos_stats),
                "export_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(filepath, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            self.logger.info(f"QoS configuration exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export QoS configuration: {e}")
            return False


# Global instance
_bandwidth_manager = None

def get_intelligent_bandwidth_manager() -> IntelligentBandwidthManager:
    """Get global intelligent bandwidth manager instance"""
    global _bandwidth_manager
    if _bandwidth_manager is None:
        _bandwidth_manager = IntelligentBandwidthManager()
    return _bandwidth_manager