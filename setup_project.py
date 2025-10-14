#!/usr/bin/env python3
"""
Project Setup and Initialization Script

Creates the complete project structure with all necessary directories,
requirements files, and configuration templates for AI-Enhanced PDanet-Linux.
"""

import os
from pathlib import Path

def create_project_structure():
    """Create complete project directory structure"""
    
    directories = [
        "pdanet_ai",
        "pdanet_ai/core",
        "pdanet_ai/system", 
        "pdanet_ai/api",
        "pdanet_ai/utils",
        "pdanet_ai/data",
        "pdanet_ai/data/collectors",
        "pdanet_ai/data/storage",
        "pdanet_ai/ml_models",
        "pdanet_ai/ml_models/traffic_prediction",
        "pdanet_ai/ml_models/anomaly_detection",
        "pdanet_ai/ml_models/user_modeling",
        "pdanet_ai/ml_models/optimization_rl",
        "config",
        "logs",
        "data",
        "data/training",
        "data/models",
        "data/cache",
        "tests",
        "tests/unit",
        "tests/integration",
        "docs",
        "scripts",
        "docker",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files for Python packages
        if directory.startswith("pdanet_ai"):
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    print("✅ Created project directory structure")

def create_requirements_file():
    """Create requirements.txt with all dependencies"""
    
    requirements = [
        "# Core Framework",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "python-multipart>=0.0.6",
        "python-dotenv>=1.0.0",
        "",
        "# AI/ML Libraries",
        "torch>=2.1.0",
        "torchvision>=0.16.0",
        "scikit-learn>=1.3.0",
        "numpy>=1.24.0",
        "pandas>=2.1.0",
        "scipy>=1.11.0",
        "stable-baselines3>=2.2.1",
        "optuna>=3.4.0",
        "",
        "# Network and System",
        "psutil>=5.9.0",
        "scapy>=2.5.0",
        "netifaces>=0.11.0",
        "pyroute2>=0.7.0",
        "",
        "# Data Storage",
        "redis>=5.0.0",
        "asyncpg>=0.29.0",
        "sqlalchemy[asyncio]>=2.0.0",
        "databases[postgresql]>=0.8.0",
        "",
        "# HTTP and WebSockets",
        "httpx>=0.25.0",
        "aiohttp>=3.9.0",
        "websockets>=12.0",
        "",
        "# Configuration and Logging",
        "pyyaml>=6.0",
        "structlog>=23.2.0",
        "loguru>=0.7.0",
        "",
        "# Security",
        "cryptography>=41.0.0",
        "bcrypt>=4.1.0",
        "pyjwt>=2.8.0",
        "",
        "# Testing",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.1.0",
        "httpx>=0.25.0",
        "",
        "# Development Tools",
        "black>=23.0.0",
        "isort>=5.12.0",
        "flake8>=6.0.0",
        "mypy>=1.7.0",
        "",
        "# Monitoring and Metrics",
        "prometheus-client>=0.19.0",
        "grafana-client>=3.5.0",
    ]
    
    with open("requirements.txt", "w") as f:
        f.write("\n".join(requirements))
    
    print("✅ Created requirements.txt")

def create_config_files():
    """Create configuration file templates"""
    
    # Main configuration file
    config_yaml = """
# AI-Enhanced PDanet-Linux Configuration

environment: development

# Database Configuration
database:
  host: localhost
  port: 5432
  database: pdanet_ai
  username: pdanet_user
  password: your_secure_password_here
  pool_size: 10
  max_overflow: 20

# Redis Configuration
redis:
  host: localhost
  port: 6379
  database: 0
  password: null
  max_connections: 100

# Machine Learning Configuration
ml:
  models_dir: ml_models
  data_dir: data
  batch_size: 32
  learning_rate: 0.001
  max_epochs: 100
  device: auto  # auto, cpu, cuda
  enable_gpu: true

# Network Configuration
network:
  default_interface: tun0
  monitoring_interval: 5  # seconds
  optimization_interval: 30  # seconds
  max_connections: 1000
  connection_timeout: 30
  enable_ipv6: false

# Security Configuration
security:
  enable_monitoring: true
  threat_detection_threshold: 0.7
  auto_response_enabled: true
  max_threat_response_actions: 5
  security_log_retention_days: 30
  whitelist_ips: []
  blacklist_ips: []

# API Configuration
api:
  host: 0.0.0.0
  port: 8000
  workers: 4
  max_request_size: 16777216  # 16MB
  request_timeout: 300
  enable_cors: true
  cors_origins: ["*"]
  api_key_required: true
  rate_limit_requests: 1000
  rate_limit_window: 3600  # 1 hour

# Logging Configuration
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_path: logs/pdanet_ai.log
  max_file_size: 10485760  # 10MB
  backup_count: 5
  enable_json_logging: false
  log_to_console: true
  log_sql_queries: false

# Monitoring Configuration
monitoring:
  enable_prometheus: true
  prometheus_port: 9090
  metrics_retention_days: 7
  health_check_interval: 30
  enable_detailed_metrics: true
"""
    
    with open("config/config.yaml", "w") as f:
        f.write(config_yaml)
    
    # Docker environment file
    docker_env = """
# Docker Environment Configuration
PDANET_ENV=production
PDANET_DB_HOST=postgres
PDANET_DB_PORT=5432
PDANET_DB_NAME=pdanet_ai
PDANET_DB_USER=pdanet_user
PDANET_DB_PASSWORD=secure_password_change_me
PDANET_REDIS_HOST=redis
PDANET_REDIS_PORT=6379
PDANET_API_HOST=0.0.0.0
PDANET_API_PORT=8000
PDANET_LOG_LEVEL=INFO
"""
    
    with open(".env.docker", "w") as f:
        f.write(docker_env)
    
    # Development environment file
    dev_env = """
# Development Environment Configuration
PDANET_ENV=development
PDANET_DB_HOST=localhost
PDANET_DB_PORT=5432
PDANET_DB_NAME=pdanet_ai_dev
PDANET_DB_USER=pdanet_dev
PDANET_DB_PASSWORD=dev_password
PDANET_REDIS_HOST=localhost
PDANET_REDIS_PORT=6379
PDANET_API_HOST=127.0.0.1
PDANET_API_PORT=8000
PDANET_LOG_LEVEL=DEBUG
PDANET_ML_DEVICE=cpu
"""
    
    with open(".env.development", "w") as f:
        f.write(dev_env)
    
    print("✅ Created configuration files")

def create_docker_files():
    """Create Docker configuration files"""
    
    dockerfile = """
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    iproute2 \
    iptables \
    tcpdump \
    net-tools \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data/models ml_models

# Set permissions
RUN chmod +x scripts/*.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "pdanet_ai.api.fastapi_server:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    
    docker_compose = """
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
      - "9090:9090"  # Prometheus metrics
    environment:
      - PDANET_ENV=production
    env_file:
      - .env.docker
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
      - ./ml_models:/app/ml_models
    restart: unless-stopped
    cap_add:
      - NET_ADMIN  # Required for network management
    privileged: true  # Required for iptables and network configuration
    networks:
      - pdanet-network

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: pdanet_ai
      POSTGRES_USER: pdanet_user
      POSTGRES_PASSWORD: secure_password_change_me
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    networks:
      - pdanet-network

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - pdanet-network

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9091:9090"
    volumes:
      - ./docker/prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    networks:
      - pdanet-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana
      - ./docker/grafana:/etc/grafana/provisioning
    networks:
      - pdanet-network

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  pdanet-network:
    driver: bridge
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose)
    
    print("✅ Created Docker configuration files")

def create_scripts():
    """Create utility scripts"""
    
    # Startup script
    startup_script = """
#!/bin/bash

# AI-Enhanced PDanet-Linux Startup Script

echo "🚀 Starting AI-Enhanced PDanet-Linux..."

# Check if running as root (required for network operations)
if [ "$EUID" -ne 0 ]; then
  echo "❌ This script must be run as root for network operations"
  echo "   Please run: sudo $0"
  exit 1
fi

# Check dependencies
echo "🔍 Checking system dependencies..."

command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
command -v pip3 >/dev/null 2>&1 || { echo "❌ pip3 is required but not installed."; exit 1; }
command -v ip >/dev/null 2>&1 || { echo "❌ iproute2 (ip command) is required but not installed."; exit 1; }
command -v iptables >/dev/null 2>&1 || { echo "❌ iptables is required but not installed."; exit 1; }

echo "✅ All dependencies found"

# Install Python dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "📦 Using existing virtual environment..."
    source venv/bin/activate
fi

# Create necessary directories
mkdir -p logs data/models ml_models config

# Set appropriate permissions
chmod +x scripts/*.sh

# Start the application
echo "🎯 Starting AI-Enhanced PDanet-Linux API..."
exec python -m uvicorn pdanet_ai.api.fastapi_server:app --host 0.0.0.0 --port 8000 --reload
"""
    
    with open("scripts/start.sh", "w") as f:
        f.write(startup_script)
    
    # Install script
    install_script = """
#!/bin/bash

# AI-Enhanced PDanet-Linux Installation Script

echo "📦 Installing AI-Enhanced PDanet-Linux..."

# Update system packages
echo "🔄 Updating system packages..."
apt-get update

# Install system dependencies
echo "📥 Installing system dependencies..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    iproute2 \
    iptables \
    tcpdump \
    net-tools \
    iputils-ping \
    curl \
    wget \
    git

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p logs data/models ml_models config

# Set permissions
echo "🔒 Setting permissions..."
chmod +x scripts/*.sh

echo "✅ Installation complete!"
echo "📖 Next steps:"
echo "   1. Edit config/config.yaml with your settings"
echo "   2. Run: sudo ./scripts/start.sh"
echo "   3. Access the API at http://localhost:8000"
"""
    
    with open("scripts/install.sh", "w") as f:
        f.write(install_script)
    
    # Make scripts executable
    os.chmod("scripts/start.sh", 0o755)
    os.chmod("scripts/install.sh", 0o755)
    
    print("✅ Created utility scripts")

def create_test_files():
    """Create basic test structure"""
    
    test_config = """
# Test Configuration
pytest_plugins = ["pytest_asyncio"]

[tool:pytest]
addopts = --strict-markers --cov=pdanet_ai --cov-report=html --cov-report=term-missing
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
"""
    
    with open("pytest.ini", "w") as f:
        f.write(test_config)
    
    # Basic test file
    basic_test = '''#!/usr/bin/env python3
"""
Basic tests for AI-Enhanced PDanet-Linux
"""

import pytest
from fastapi.testclient import TestClient

# Import your app when ready
# from pdanet_ai.api.fastapi_server import app

def test_placeholder():
    """Placeholder test - replace with actual tests"""
    assert True

# @pytest.fixture
# def client():
#     return TestClient(app)

# def test_health_endpoint(client):
#     response = client.get("/health")
#     assert response.status_code == 200
'''
    
    with open("tests/test_basic.py", "w") as f:
        f.write(basic_test)
    
    print("✅ Created test files")

def create_readme():
    """Create comprehensive README"""
    
    readme = """
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
"""
    
    with open("README.md", "w") as f:
        f.write(readme)
    
    print("✅ Created comprehensive README.md")

def create_gitignore():
    """Create .gitignore file"""
    
    gitignore = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
PYTHON*

# Virtual Environment
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Jupyter Notebook
.ipynb_checkpoints

# Environment variables
.env
.env.local
.env.development
.env.production

# Logs
logs/
*.log

# Data and Models
data/models/
data/cache/
ml_models/*.pth
ml_models/*.onnx
ml_models/*.pkl

# Database
*.db
*.sqlite

# OS
.DS_Store
Thumbs.db

# Docker
docker-compose.override.yml

# Coverage
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Config overrides
config/*.local.*

# Temporary files
*.tmp
*.temp
.cache/

# Security
*.key
*.pem
*.crt
secrets/
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore)
    
    print("✅ Created .gitignore")

def main():
    """Main setup function"""
    print("🔧 Setting up AI-Enhanced PDanet-Linux project...\n")
    
    create_project_structure()
    create_requirements_file()
    create_config_files()
    create_docker_files()
    create_scripts()
    create_test_files()
    create_readme()
    create_gitignore()
    
    print("\n🎉 Project setup complete!")
    print("\n📋 Next Steps:")
    print("   1. Review and edit config/config.yaml")
    print("   2. Install dependencies: sudo ./scripts/install.sh")
    print("   3. Start the system: sudo ./scripts/start.sh")
    print("   4. Access API docs: http://localhost:8000/docs")
    print("\n🚀 Ready to revolutionize mobile connectivity with AI!")

if __name__ == "__main__":
    main()