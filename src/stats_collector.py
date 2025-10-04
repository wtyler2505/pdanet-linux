"""
PdaNet Linux - Statistics Collector
Tracks bandwidth, connection quality, and usage metrics
"""

import time
import subprocess
from collections import deque
from datetime import datetime
from pathlib import Path

class StatsCollector:
    def __init__(self):
        self.start_time = None
        self.bytes_sent = 0
        self.bytes_received = 0

        # Rolling windows for rate calculation
        self.rx_history = deque(maxlen=60)  # 60 seconds
        self.tx_history = deque(maxlen=60)

        # Connection quality metrics
        self.latency_history = deque(maxlen=30)
        self.packet_loss_history = deque(maxlen=10)

        # Interface tracking
        self.current_interface = None
        self.last_rx_bytes = 0
        self.last_tx_bytes = 0
        self.last_update_time = 0

    def start_session(self):
        """Start a new connection session"""
        self.start_time = time.time()
        self.bytes_sent = 0
        self.bytes_received = 0
        self.rx_history.clear()
        self.tx_history.clear()
        self.latency_history.clear()
        self.packet_loss_history.clear()

    def stop_session(self):
        """End current connection session"""
        self.start_time = None

    def update_bandwidth(self, interface="usb0"):
        """Update bandwidth statistics from network interface"""
        try:
            # Read interface statistics from /sys
            rx_bytes_path = f"/sys/class/net/{interface}/statistics/rx_bytes"
            tx_bytes_path = f"/sys/class/net/{interface}/statistics/tx_bytes"

            if not Path(rx_bytes_path).exists():
                return

            with open(rx_bytes_path) as f:
                rx_bytes = int(f.read().strip())
            with open(tx_bytes_path) as f:
                tx_bytes = int(f.read().strip())

            current_time = time.time()

            if self.last_update_time > 0:
                time_delta = current_time - self.last_update_time

                # Calculate rates
                rx_rate = (rx_bytes - self.last_rx_bytes) / time_delta if time_delta > 0 else 0
                tx_rate = (tx_bytes - self.last_tx_bytes) / time_delta if time_delta > 0 else 0

                self.rx_history.append((current_time, rx_rate))
                self.tx_history.append((current_time, tx_rate))

                # Update totals
                self.bytes_received += (rx_bytes - self.last_rx_bytes)
                self.bytes_sent += (tx_bytes - self.last_tx_bytes)

            self.last_rx_bytes = rx_bytes
            self.last_tx_bytes = tx_bytes
            self.last_update_time = current_time
            self.current_interface = interface

        except Exception as e:
            print(f"Error updating bandwidth: {e}")

    def get_current_download_rate(self):
        """Get current download rate in bytes/second"""
        if not self.rx_history:
            return 0
        return self.rx_history[-1][1]

    def get_current_upload_rate(self):
        """Get current upload rate in bytes/second"""
        if not self.tx_history:
            return 0
        return self.tx_history[-1][1]

    def get_average_download_rate(self, seconds=10):
        """Get average download rate over last N seconds"""
        if not self.rx_history:
            return 0

        cutoff_time = time.time() - seconds
        recent = [rate for ts, rate in self.rx_history if ts >= cutoff_time]

        return sum(recent) / len(recent) if recent else 0

    def get_average_upload_rate(self, seconds=10):
        """Get average upload rate over last N seconds"""
        if not self.tx_history:
            return 0

        cutoff_time = time.time() - seconds
        recent = [rate for ts, rate in self.tx_history if ts >= cutoff_time]

        return sum(recent) / len(recent) if recent else 0

    def get_uptime(self):
        """Get connection uptime in seconds"""
        if self.start_time is None:
            return 0
        return time.time() - self.start_time

    def get_total_downloaded(self):
        """Get total bytes downloaded"""
        return self.bytes_received

    def get_total_uploaded(self):
        """Get total bytes uploaded"""
        return self.bytes_sent

    def ping_test(self, host="8.8.8.8", count=1):
        """Test latency with ping"""
        try:
            result = subprocess.run(
                ["ping", "-c", str(count), "-W", "2", host],
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.returncode == 0:
                # Parse latency from ping output
                for line in result.stdout.split('\n'):
                    if 'time=' in line:
                        latency_str = line.split('time=')[1].split()[0]
                        latency = float(latency_str)
                        self.latency_history.append(latency)
                        return latency
            return None
        except Exception as e:
            print(f"Ping test error: {e}")
            return None

    def get_current_latency(self):
        """Get most recent latency measurement"""
        if not self.latency_history:
            return None
        return self.latency_history[-1]

    def get_average_latency(self):
        """Get average latency"""
        if not self.latency_history:
            return None
        return sum(self.latency_history) / len(self.latency_history)

    def estimate_packet_loss(self, packets_sent=10):
        """Estimate packet loss percentage"""
        try:
            result = subprocess.run(
                ["ping", "-c", str(packets_sent), "-W", "1", "8.8.8.8"],
                capture_output=True,
                text=True,
                timeout=packets_sent + 2
            )

            for line in result.stdout.split('\n'):
                if 'packet loss' in line:
                    loss_str = line.split(',')[2].strip().split('%')[0]
                    loss_percent = float(loss_str)
                    self.packet_loss_history.append(loss_percent)
                    return loss_percent
            return 0.0
        except Exception as e:
            print(f"Packet loss test error: {e}")
            return None

    def get_current_packet_loss(self):
        """Get most recent packet loss measurement"""
        if not self.packet_loss_history:
            return 0.0
        return self.packet_loss_history[-1]

    def get_connection_quality(self):
        """Calculate connection quality score (0-100)"""
        quality = 100

        # Latency penalty (good < 50ms, poor > 200ms)
        latency = self.get_average_latency()
        if latency:
            if latency > 200:
                quality -= 30
            elif latency > 100:
                quality -= 15
            elif latency > 50:
                quality -= 5

        # Packet loss penalty
        packet_loss = self.get_current_packet_loss()
        if packet_loss:
            quality -= packet_loss * 2  # 2 points per 1% loss

        return max(0, min(100, quality))

    def get_bandwidth_graph_data(self, seconds=60):
        """Get data points for bandwidth graph"""
        cutoff_time = time.time() - seconds

        rx_data = [(ts, rate) for ts, rate in self.rx_history if ts >= cutoff_time]
        tx_data = [(ts, rate) for ts, rate in self.tx_history if ts >= cutoff_time]

        return rx_data, tx_data

    def get_stats_summary(self):
        """Get summary of all statistics"""
        return {
            "uptime": self.get_uptime(),
            "download_rate": self.get_current_download_rate(),
            "upload_rate": self.get_current_upload_rate(),
            "total_downloaded": self.get_total_downloaded(),
            "total_uploaded": self.get_total_uploaded(),
            "latency": self.get_current_latency(),
            "packet_loss": self.get_current_packet_loss(),
            "quality": self.get_connection_quality(),
            "interface": self.current_interface
        }

# Global stats instance
_stats_instance = None

def get_stats():
    """Get or create global stats instance"""
    global _stats_instance
    if _stats_instance is None:
        _stats_instance = StatsCollector()
    return _stats_instance
