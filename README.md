
# AI-Enhanced PDanet-Linux 🚀

**Deep AI/ML Integration for Intelligent Mobile Connectivity Management**

A comprehensive, AI-powered enhancement of pdanet-linux that transforms basic tethering into an intelligent, self-optimizing network management system. This project integrates cutting-edge machine learning capabilities at every level of the networking stack.

## 🌟 Key Features

### 🧠 AI-Powered Network Optimization
- **Real-time Traffic Prediction**: LSTM/GRU networks for bandwidth forecasting (1min to 1hour horizons)
- **Reinforcement Learning**: PPO agent for dynamic routing and connection optimization
- **Intelligent Bandwidth Management**: ML-driven QoS allocation and traffic shaping
- **Adaptive Tunnel Optimization**: AI-optimized MTU, buffer sizes, and congestion control

### 🔒 Advanced Security & Monitoring
- **Behavioral Anomaly Detection**: Real-time user and network behavior analysis
- **Threat Classification**: ML-based threat assessment and automated response
- **Forensic Capabilities**: Comprehensive data capture and analysis
- **Zero-Day Detection**: Unsupervised learning for unknown threat patterns

### 🔄 Intelligent Connection Management
- **Automatic Network Switching**: Seamless failover between connections
- **Predictive Connectivity**: Anticipate and prevent connection issues
- **Load Balancing**: Multi-path optimization with intelligent routing
- **Compression & Encryption**: Dynamic optimization based on network conditions

### 🎯 User Experience
- **Natural Language Interface**: Configure networks with plain English commands
- **Personalized Optimization**: Learn and adapt to individual usage patterns
- **Real-time Dashboard**: WebSocket-powered monitoring and control
- **Mobile Companion**: Seamless integration with mobile devices

## 🏗️ Architecture Overview

```
AI-Enhanced PDanet-Linux Architecture

┌─────────────────────────────────────────────────────────────┐
│                    FastAPI REST API                        │
│              WebSocket Real-time Updates                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 NetworkBrain (Central AI Coordinator)      │
├─────────────────────────────────────────────────────────────┤
│  TrafficPredictor  │  ConnectionOptimizer  │  SecurityMonitor │
│     (LSTM/GRU)     │        (PPO RL)       │   (Anomaly ML)   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Enhanced System Components                     │
├─────────────────────────────────────────────────────────────┤
│  AIEnhancedTunnel  │  IntelligentBandwidth │  UserProfiler   │
│                    │      Manager          │                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Linux Network Stack                         │
│            (iptables, tc, ip, tun2socks)                   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Linux system (Ubuntu 20.04+ / Debian 11+ / Arch Linux)
- Python 3.9+
- Root privileges (for network management)
- PDANet Android app

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/pdanet-linux-ai.git
   cd pdanet-linux-ai
   ```

2. **Run the installation script:**
   ```bash
   sudo ./scripts/install.sh
   ```

3. **Configure your settings:**
   ```bash
   cp config/config.yaml config/config.yaml.local
   nano config/config.yaml.local
   ```

4. **Start the system:**
   ```bash
   sudo ./scripts/start.sh
   ```

5. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Real-time Dashboard: http://localhost:8000/dashboard (coming soon)

### Docker Deployment

```bash
# Clone and configure
git clone https://github.com/your-username/pdanet-linux-ai.git
cd pdanet-linux-ai
cp .env.docker .env.local

# Edit configuration
nano .env.local

# Deploy with Docker Compose
docker-compose up -d
```

## 📖 Usage Examples

### Basic Network Connection
```python
import httpx

# Connect to PDANet with AI optimization
response = httpx.post("http://localhost:8000/network/connect", json={
    "proxy_address": "192.168.49.1",
    "proxy_port": 8000,
    "connection_type": "wifi",
    "enable_ai_optimization": True
})

print(f"Connection Status: {response.json()}")
```

### AI-Powered Traffic Prediction
```python
# Get traffic predictions for next hour
response = httpx.post("http://localhost:8000/ai/predict-traffic", json={
    "horizons": [1, 15, 60],  # 1min, 15min, 1hour
    "include_confidence": True
})

predictions = response.json()
print(f"Predicted bandwidth in 15min: {predictions['data']['predictions']['15min']}")
```

### Natural Language Configuration
```python
# Configure network using natural language (coming soon)
response = httpx.post("http://localhost:8000/nlp/configure", json={
    "command": "Optimize my connection for video calls and prioritize low latency"
})
```

### Real-time Monitoring with WebSockets
```python
import asyncio
import websockets
import json

async def monitor_network():
    uri = "ws://localhost:8000/ws/monitor"
    async with websockets.connect(uri) as websocket:
        # Subscribe to network metrics
        await websocket.send(json.dumps({
            "type": "subscribe",
            "subscription": "metrics"
        }))
        
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "network_metrics":
                print(f"Network Status: {data['data']['ai_insights']}")

asyncio.run(monitor_network())
```

## 🔧 Configuration

### Core Configuration (config/config.yaml)

```yaml
# AI/ML Configuration
ml:
  models_dir: ml_models
  batch_size: 32
  learning_rate: 0.001
  device: auto  # auto, cpu, cuda
  enable_gpu: true

# Network Optimization
network:
  monitoring_interval: 5  # seconds
  optimization_interval: 30  # seconds
  max_connections: 1000

# Security Settings
security:
  enable_monitoring: true
  threat_detection_threshold: 0.7
  auto_response_enabled: true
```

### Environment Variables

```bash
# API Configuration
export PDANET_API_PORT=8000
export PDANET_API_HOST=0.0.0.0

# ML Configuration
export PDANET_ML_DEVICE=cuda  # or cpu
export PDANET_ML_BATCH_SIZE=32

# Security
export PDANET_SECURITY_ENABLED=true
export PDANET_AUTO_RESPONSE=true
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pdanet_ai --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests
```

## 📊 Monitoring & Metrics

- **Prometheus Metrics**: http://localhost:9090
- **Grafana Dashboard**: http://localhost:3000 (admin/admin123)
- **API Health**: http://localhost:8000/health
- **System Metrics**: http://localhost:8000/metrics/system

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/your-username/pdanet-linux-ai.git
cd pdanet-linux-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original PDanet-Linux project contributors
- OpenAI for GPT models used in development
- The entire open-source ML/AI community

## 🔮 Roadmap

- [ ] **v1.1**: Natural Language Interface with LLM integration
- [ ] **v1.2**: Mobile companion app (Android/iOS)
- [ ] **v1.3**: Federated learning across multiple devices
- [ ] **v1.4**: 5G optimization and network slicing
- [ ] **v1.5**: Edge computing integration

---

**Made with ❤️ and 🤖 AI by the PDanet-Linux-AI Team**

*Transforming mobile connectivity through artificial intelligence*
