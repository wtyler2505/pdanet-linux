"""
PdaNet Linux - P3 User Experience Enhancements  
Advanced UX improvements for desktop network tethering application
"""

import json
import os
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from logger import get_logger
from performance_optimizer import cached_method, resource_context


@dataclass
class ConnectionProfile:
    """User connection profile for quick switching"""
    name: str
    mode: str  # "usb", "wifi", "iphone"
    ssid: Optional[str] = None
    password_keyring_id: Optional[str] = None  # Reference to keyring entry
    auto_connect: bool = False
    stealth_enabled: bool = True
    stealth_level: int = 3  # 1=basic, 2=moderate, 3=aggressive
    description: str = ""
    created_date: str = ""
    last_used: Optional[str] = None
    use_count: int = 0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.created_date:
            self.created_date = datetime.now().isoformat()


@dataclass
class NetworkQualityMetrics:
    """Real-time network quality assessment"""
    timestamp: float
    latency_ms: float
    jitter_ms: float
    packet_loss_percent: float
    throughput_mbps: float
    signal_strength_dbm: float
    quality_score: int  # 0-100
    connection_stability: str  # "excellent", "good", "fair", "poor"
    recommendation: str = ""


@dataclass  
class UsageStatistics:
    """Comprehensive usage statistics"""
    total_sessions: int = 0
    total_uptime_hours: float = 0.0
    total_data_gb: float = 0.0
    favorite_mode: str = "usb"
    peak_speed_mbps: float = 0.0
    average_session_duration: float = 0.0
    success_rate_percent: float = 100.0
    most_used_profile: str = ""
    last_week_usage: Dict[str, float] = None
    monthly_trends: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.last_week_usage is None:
            self.last_week_usage = {}
        if self.monthly_trends is None:
            self.monthly_trends = {}


class UserExperienceManager:
    """Advanced user experience and personalization manager"""
    
    def __init__(self):
        self.logger = get_logger()
        self.config_dir = Path.home() / ".config" / "pdanet-linux"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Profile management
        self.profiles_file = self.config_dir / "profiles.json"
        self.user_profiles: Dict[str, ConnectionProfile] = {}
        
        # User preferences
        self.preferences_file = self.config_dir / "user_preferences.json"
        self.user_preferences = self._load_user_preferences()
        
        # Usage analytics
        self.usage_file = self.config_dir / "usage_statistics.json"
        self.usage_stats = self._load_usage_statistics()
        
        # Quality monitoring
        self.quality_history: List[NetworkQualityMetrics] = []
        self.quality_monitoring_enabled = True
        
        # Quick actions
        self.quick_actions = [
            {"name": "Quick Connect", "action": "connect_last_used", "hotkey": "Ctrl+Q"},
            {"name": "Speed Test", "action": "run_speed_test", "hotkey": "Ctrl+T"}, 
            {"name": "Toggle Stealth", "action": "toggle_stealth", "hotkey": "Ctrl+S"},
            {"name": "Profile Switch", "action": "show_profile_menu", "hotkey": "Ctrl+P"}
        ]
        
        # Load existing profiles
        self._load_profiles()
        
        # Start quality monitoring
        self._start_quality_monitoring()
    
    def _load_user_preferences(self) -> Dict[str, Any]:
        """Load user preferences with defaults"""
        defaults = {
            "theme": "cyberpunk_dark",
            "notifications_enabled": True,
            "auto_connect_on_startup": False,
            "minimize_to_tray": True,
            "show_advanced_metrics": False,
            "preferred_connection_mode": "usb",
            "data_usage_warnings": True,
            "warning_threshold_gb": 10.0,
            "quality_monitoring_interval": 30,
            "auto_profile_suggestions": True,
            "connection_timeout_seconds": 60,
            "log_level": "INFO",
            "language": "en_US",
            "metric_units": "metric"  # or "imperial"
        }
        
        if not self.preferences_file.exists():
            # Save defaults for first time
            try:
                self.config_dir.mkdir(parents=True, exist_ok=True)
                with open(self.preferences_file, 'w') as f:
                    json.dump(defaults, f, indent=2)
                self.logger.info("Created default user preferences")
            except Exception as e:
                self.logger.warning(f"Could not create default preferences: {e}")
            return defaults.copy()
        
        try:
            with open(self.preferences_file) as f:
                loaded = json.load(f)
                # Merge with defaults to ensure all keys exist
                result = defaults.copy()
                result.update(loaded)
                return result
        except Exception as e:
            self.logger.warning(f"Failed to load preferences: {e}")
            return defaults.copy()
    
    def _load_usage_statistics(self) -> UsageStatistics:
        """Load usage statistics with error handling"""
        if self.usage_file.exists():
            try:
                with open(self.usage_file) as f:
                    data = json.load(f)
                    return UsageStatistics(**data)
            except Exception as e:
                self.logger.warning(f"Failed to load usage statistics: {e}")
        
        return UsageStatistics()
    
    def _load_profiles(self):
        """Load user connection profiles"""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file) as f:
                    data = json.load(f)
                    for name, profile_data in data.items():
                        self.user_profiles[name] = ConnectionProfile(**profile_data)
                self.logger.info(f"Loaded {len(self.user_profiles)} user profiles")
            except Exception as e:
                self.logger.error(f"Failed to load profiles: {e}")
    
    def save_profiles(self):
        """Save user connection profiles atomically"""
        try:
            data = {name: asdict(profile) for name, profile in self.user_profiles.items()}
            
            # Atomic write
            temp_file = self.profiles_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            temp_file.replace(self.profiles_file)
            
            self.logger.debug(f"Saved {len(self.user_profiles)} profiles")
        except Exception as e:
            self.logger.error(f"Failed to save profiles: {e}")
    
    def save_preferences(self):
        """Save user preferences atomically"""
        try:
            temp_file = self.preferences_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
            temp_file.replace(self.preferences_file)
        except Exception as e:
            self.logger.error(f"Failed to save preferences: {e}")
    
    def save_usage_statistics(self):
        """Save usage statistics atomically"""
        try:
            temp_file = self.usage_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(asdict(self.usage_stats), f, indent=2)
            temp_file.replace(self.usage_file)
        except Exception as e:
            self.logger.error(f"Failed to save usage statistics: {e}")
    
    # Profile Management
    def create_profile(self, name: str, mode: str, **kwargs) -> bool:
        """Create a new connection profile"""
        if name in self.user_profiles:
            return False
            
        profile = ConnectionProfile(name=name, mode=mode, **kwargs)
        self.user_profiles[name] = profile
        self.save_profiles()
        
        self.logger.info(f"Created profile: {name} ({mode})")
        return True
    
    def update_profile(self, name: str, **updates) -> bool:
        """Update an existing profile"""
        if name not in self.user_profiles:
            return False
            
        profile = self.user_profiles[name]
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        self.save_profiles()
        return True
    
    def delete_profile(self, name: str) -> bool:
        """Delete a connection profile"""
        if name in self.user_profiles:
            del self.user_profiles[name]
            self.save_profiles()
            self.logger.info(f"Deleted profile: {name}")
            return True
        return False
    
    def get_profile(self, name: str) -> Optional[ConnectionProfile]:
        """Get a specific profile"""
        return self.user_profiles.get(name)
    
    def list_profiles(self) -> List[ConnectionProfile]:
        """Get all profiles sorted by usage"""
        profiles = list(self.user_profiles.values())
        profiles.sort(key=lambda p: (p.use_count, p.last_used or ""), reverse=True)
        return profiles
    
    def use_profile(self, name: str) -> Optional[ConnectionProfile]:
        """Mark profile as used and return it"""
        if name in self.user_profiles:
            profile = self.user_profiles[name]
            profile.last_used = datetime.now().isoformat()
            profile.use_count += 1
            self.save_profiles()
            return profile
        return None
    
    def get_suggested_profiles(self, current_context: Dict[str, Any]) -> List[ConnectionProfile]:
        """Get AI-suggested profiles based on context"""
        if not self.user_preferences.get("auto_profile_suggestions", True):
            return []
        
        suggestions = []
        current_hour = datetime.now().hour
        
        for profile in self.user_profiles.values():
            score = 0
            
            # Time-based suggestions
            if profile.last_used:
                try:
                    last_used_time = datetime.fromisoformat(profile.last_used)
                    if abs(last_used_time.hour - current_hour) <= 1:
                        score += 20  # Same time of day
                except (ValueError, TypeError):
                    pass  # Invalid timestamp format
            
            # Usage frequency
            score += min(profile.use_count * 2, 30)
            
            # Context matching
            if current_context.get("preferred_mode") == profile.mode:
                score += 25
            
            if score > 30:  # Threshold for suggestions
                suggestions.append((profile, score))
        
        # Sort by score and return top 3
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [profile for profile, score in suggestions[:3]]
    
    # Quality Monitoring
    def _start_quality_monitoring(self):
        """Start background quality monitoring"""
        if not self.quality_monitoring_enabled:
            return
            
        def quality_monitor():
            while self.quality_monitoring_enabled:
                try:
                    interval = self.user_preferences.get("quality_monitoring_interval", 30)
                    time.sleep(interval)
                    
                    # This would integrate with connection_manager to get actual metrics
                    # For now, we'll create a placeholder
                    self._collect_quality_metrics()
                    
                except Exception as e:
                    self.logger.error(f"Quality monitoring error: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=quality_monitor, daemon=True)
        monitor_thread.start()
    
    def _collect_quality_metrics(self):
        """Collect network quality metrics (placeholder)"""
        # This would integrate with actual network monitoring
        # For now, create mock metrics
        if len(self.quality_history) > 100:
            self.quality_history = self.quality_history[-50:]  # Keep last 50 samples
    
    @cached_method(ttl=60, max_size=20)
    def get_quality_assessment(self) -> Dict[str, Any]:
        """Get current network quality assessment"""
        if not self.quality_history:
            return {
                "status": "no_data",
                "score": 0,
                "recommendations": ["Connect to start quality monitoring"]
            }
        
        recent_metrics = self.quality_history[-10:]  # Last 10 samples
        
        if not recent_metrics:
            return {"status": "no_data", "score": 0}
        
        avg_latency = sum(m.latency_ms for m in recent_metrics) / len(recent_metrics)
        avg_quality = sum(m.quality_score for m in recent_metrics) / len(recent_metrics)
        
        recommendations = []
        if avg_latency > 200:
            recommendations.append("High latency detected - consider switching connection method")
        if avg_quality < 50:
            recommendations.append("Poor connection quality - check network settings")
        
        return {
            "status": "active",
            "average_latency_ms": avg_latency,
            "average_quality_score": avg_quality,
            "recommendations": recommendations,
            "sample_count": len(recent_metrics)
        }
    
    # Usage Analytics
    def record_connection_session(self, mode: str, duration_seconds: float, data_bytes: int, success: bool):
        """Record a connection session for analytics"""
        self.usage_stats.total_sessions += 1
        self.usage_stats.total_uptime_hours += duration_seconds / 3600
        self.usage_stats.total_data_gb += data_bytes / (1024 ** 3)
        
        # Update favorite mode based on most usage
        mode_counts = getattr(self, '_mode_counts', {})
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
        self._mode_counts = mode_counts
        
        # Find most used mode
        if mode_counts:
            self.usage_stats.favorite_mode = max(mode_counts.items(), key=lambda x: x[1])[0]
        
        # Update average session duration properly
        if self.usage_stats.total_sessions > 1:
            total_duration = (self.usage_stats.average_session_duration * (self.usage_stats.total_sessions - 1) + 
                            duration_seconds)
            self.usage_stats.average_session_duration = total_duration / self.usage_stats.total_sessions
        else:
            self.usage_stats.average_session_duration = duration_seconds
        
        # Update success rate properly 
        if self.usage_stats.total_sessions > 1:
            previous_successes = (self.usage_stats.success_rate_percent / 100) * (self.usage_stats.total_sessions - 1)
            current_successes = previous_successes + (1 if success else 0)
            self.usage_stats.success_rate_percent = (current_successes / self.usage_stats.total_sessions) * 100
        else:
            self.usage_stats.success_rate_percent = 100.0 if success else 0.0
        
        # Update weekly usage tracking
        today = datetime.now().strftime("%Y-%m-%d")
        if not self.usage_stats.last_week_usage:
            self.usage_stats.last_week_usage = {}
            
        self.usage_stats.last_week_usage[today] = (
            self.usage_stats.last_week_usage.get(today, 0) + duration_seconds / 3600
        )
        
        # Keep only last 14 days  
        cutoff_date = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
        self.usage_stats.last_week_usage = {
            date: hours for date, hours in self.usage_stats.last_week_usage.items() 
            if date >= cutoff_date
        }
        
        self.save_usage_statistics()
    
    def get_usage_insights(self) -> Dict[str, Any]:
        """Generate usage insights and recommendations"""
        insights = {
            "summary": {
                "total_sessions": self.usage_stats.total_sessions,
                "total_uptime_hours": round(self.usage_stats.total_uptime_hours, 1),
                "total_data_gb": round(self.usage_stats.total_data_gb, 2),
                "success_rate": round(self.usage_stats.success_rate_percent, 1)
            },
            "patterns": [],
            "recommendations": []
        }
        
        # Usage patterns
        if self.usage_stats.total_sessions > 10:
            avg_session = self.usage_stats.average_session_duration / 60  # minutes
            if avg_session > 60:
                insights["patterns"].append(f"Long sessions (avg {avg_session:.0f} min)")
            elif avg_session < 10:
                insights["patterns"].append(f"Short sessions (avg {avg_session:.0f} min)")
        
        # Recommendations
        if self.usage_stats.success_rate_percent < 90:
            insights["recommendations"].append("Consider creating connection profiles to improve reliability")
        
        if self.usage_stats.total_data_gb > 50:
            insights["recommendations"].append("Enable data usage warnings to monitor consumption")
        
        return insights
    
    # Smart Notifications
    def get_smart_notifications(self, connection_state: str, current_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate contextual notifications"""
        if not self.user_preferences.get("notifications_enabled", True):
            return []
        
        notifications = []
        
        # Data usage notifications
        if self.user_preferences.get("data_usage_warnings", True):
            threshold_gb = self.user_preferences.get("warning_threshold_gb", 10.0)
            if current_metrics.get("session_data_gb", 0) > threshold_gb * 0.8:
                notifications.append({
                    "type": "warning",
                    "title": "Data Usage Alert",
                    "message": f"Approaching {threshold_gb}GB threshold",
                    "action": "show_data_usage"
                })
        
        # Connection quality notifications
        quality = current_metrics.get("connection_quality", 100)
        if quality < 50 and connection_state == "connected":
            notifications.append({
                "type": "info",
                "title": "Poor Connection Quality",
                "message": "Consider switching connection method",
                "action": "show_profiles"
            })
        
        return notifications
    
    # User Preferences
    def update_preference(self, key: str, value: Any):
        """Update a user preference"""
        self.user_preferences[key] = value
        self.save_preferences()
        self.logger.debug(f"Updated preference: {key} = {value}")
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        return self.user_preferences.get(key, default)
    
    def reset_preferences(self):
        """Reset preferences to defaults"""
        self.user_preferences = self._load_user_preferences()
        self.save_preferences()
    
    # Quick Actions
    def execute_quick_action(self, action: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a quick action"""
        if context is None:
            context = {}
            
        result = {"success": False, "message": "Unknown action"}
        
        if action == "connect_last_used":
            # Find most recently used profile
            profiles = self.list_profiles()
            if profiles:
                profile = profiles[0]
                result = {
                    "success": True, 
                    "message": f"Connecting with {profile.name}",
                    "profile": profile
                }
        
        elif action == "toggle_stealth":
            result = {
                "success": True,
                "message": "Stealth mode toggled",
                "action_required": "toggle_stealth_mode"
            }
        
        elif action == "show_profile_menu":
            result = {
                "success": True,
                "message": "Profile menu requested",
                "profiles": self.list_profiles()
            }
        
        elif action == "run_speed_test":
            result = {
                "success": True,
                "message": "Speed test initiated",
                "action_required": "start_speed_test"
            }
        
        return result
    
    def export_user_data(self, export_path: Path) -> bool:
        """Export all user data for backup"""
        try:
            export_data = {
                "profiles": {name: asdict(profile) for name, profile in self.user_profiles.items()},
                "preferences": self.user_preferences,
                "usage_statistics": asdict(self.usage_stats),
                "export_timestamp": datetime.now().isoformat(),
                "version": "2.0"
            }
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"User data exported to {export_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export user data: {e}")
            return False
    
    def import_user_data(self, import_path: Path) -> bool:
        """Import user data from backup"""
        try:
            with open(import_path) as f:
                data = json.load(f)
            
            # Import profiles
            if "profiles" in data:
                for name, profile_data in data["profiles"].items():
                    self.user_profiles[name] = ConnectionProfile(**profile_data)
                self.save_profiles()
            
            # Import preferences
            if "preferences" in data:
                self.user_preferences.update(data["preferences"])
                self.save_preferences()
            
            # Import usage statistics
            if "usage_statistics" in data:
                self.usage_stats = UsageStatistics(**data["usage_statistics"])
                self.save_usage_statistics()
            
            self.logger.info(f"User data imported from {import_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to import user data: {e}")
            return False


# Global instance
_ux_manager = None

def get_ux_manager() -> UserExperienceManager:
    """Get global user experience manager instance"""
    global _ux_manager
    if _ux_manager is None:
        _ux_manager = UserExperienceManager()
    return _ux_manager