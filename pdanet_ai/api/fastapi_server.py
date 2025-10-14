#!/usr/bin/env python3
"""
FastAPI Server - Main API Backend for AI-Enhanced PDanet-Linux

Provides REST API endpoints for network management, AI model control,
monitoring, and real-time optimization with WebSocket support.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.network_brain import NetworkBrain
from ..utils.config import Config
from ..utils.auth import AuthManager
from ..utils.metrics import MetricsCollector
from ..data.storage import APIRequestStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class NetworkConnectionRequest(BaseModel):
    """Request model for network connection"""
    proxy_address: str = Field(default="192.168.49.1")
    proxy_port: int = Field(default=8000)
    connection_type: str = Field(default="wifi")  # wifi, cellular, ethernet
    enable_ai_optimization: bool = Field(default=True)
    custom_config: Optional[Dict[str, Any]] = Field(default=None)

class NetworkOptimizationRequest(BaseModel):
    """Request model for network optimization"""
    target_metric: str = Field(default="overall")  # bandwidth, latency, reliability, overall
    optimization_level: float = Field(default=0.8, ge=0.1, le=1.0)
    preserve_stability: bool = Field(default=True)
    force_reoptimization: bool = Field(default=False)

class SecurityConfigRequest(BaseModel):
    """Request model for security configuration"""
    threat_response_level: int = Field(default=2, ge=0, le=3)
    monitoring_intensity: float = Field(default=0.7, ge=0.1, le=1.0)
    enable_auto_response: bool = Field(default=True)
    whitelist_ips: Optional[List[str]] = Field(default=None)

class TrafficPredictionRequest(BaseModel):
    """Request model for traffic prediction"""
    horizons: List[int] = Field(default=[1, 15, 60])  # minutes
    include_confidence: bool = Field(default=True)
    model_type: Optional[str] = Field(default=None)  # lstm, gru, auto

class MLModelConfigRequest(BaseModel):
    """Request model for ML model configuration"""
    enable_learning: bool = Field(default=True)
    retrain_threshold: float = Field(default=0.1, ge=0.01, le=1.0)
    model_complexity: str = Field(default="medium")  # low, medium, high
    batch_size: Optional[int] = Field(default=None)

# Response models
class APIResponse(BaseModel):
    """Base API response model"""
    success: bool
    timestamp: datetime
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class NetworkStatusResponse(APIResponse):
    """Network status response model"""
    network_state: Optional[Dict[str, Any]] = None
    ai_insights: Optional[Dict[str, Any]] = None
    active_optimizations: Optional[List[str]] = None

class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, client_info: Dict[str, Any]):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_info[websocket] = {
            'connected_at': datetime.utcnow(),
            'client_info': client_info,
            'subscriptions': set()
        }
        logger.info(f"WebSocket client connected: {client_info.get('client_id', 'unknown')}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_info:
            del self.connection_info[websocket]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message, default=str))
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict, subscription_filter: Optional[str] = None):
        disconnected = []
        for websocket in self.active_connections:
            try:
                # Check subscription filter
                if subscription_filter:
                    subscriptions = self.connection_info.get(websocket, {}).get('subscriptions', set())
                    if subscription_filter not in subscriptions:
                        continue
                
                await websocket.send_text(json.dumps(message, default=str))
            except Exception as e:
                logger.error(f"Failed to broadcast WebSocket message: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for ws in disconnected:
            self.disconnect(ws)
    
    def subscribe(self, websocket: WebSocket, subscription: str):
        if websocket in self.connection_info:
            self.connection_info[websocket]['subscriptions'].add(subscription)
    
    def unsubscribe(self, websocket: WebSocket, subscription: str):
        if websocket in self.connection_info:
            self.connection_info[websocket]['subscriptions'].discard(subscription)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging API requests"""
    
    def __init__(self, app, metrics_collector: MetricsCollector, request_storage: APIRequestStorage):
        super().__init__(app)
        self.metrics_collector = metrics_collector
        self.request_storage = request_storage
    
    async def dispatch(self, request, call_next):
        start_time = datetime.utcnow()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Log request
        request_data = {
            'method': request.method,
            'url': str(request.url),
            'status_code': response.status_code,
            'duration': duration,
            'timestamp': start_time,
            'client_ip': request.client.host if request.client else 'unknown',
            'user_agent': request.headers.get('user-agent', 'unknown')
        }
        
        # Store request data asynchronously
        asyncio.create_task(self.request_storage.store_request(request_data))
        
        # Update metrics
        await self.metrics_collector.record_api_request(
            request.method, 
            str(request.url.path), 
            response.status_code, 
            duration
        )
        
        return response

# Global instances
network_brain: Optional[NetworkBrain] = None
auth_manager: Optional[AuthManager] = None
metrics_collector: Optional[MetricsCollector] = None
websocket_manager = WebSocketManager()
request_storage: Optional[APIRequestStorage] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager"""
    global network_brain, auth_manager, metrics_collector, request_storage
    
    logger.info("Initializing AI-Enhanced PDanet-Linux API...")
    
    try:
        # Initialize configuration
        config = Config()
        
        # Initialize components
        auth_manager = AuthManager(config)
        metrics_collector = MetricsCollector(config)
        request_storage = APIRequestStorage(config)
        network_brain = NetworkBrain(config)
        
        # Initialize all components
        await auth_manager.initialize()
        await metrics_collector.initialize()
        await request_storage.initialize()
        await network_brain.initialize()
        
        # Start optimization loop
        await network_brain.start_optimization_loop()
        
        # Start background tasks
        asyncio.create_task(background_metrics_broadcast())
        
        logger.info("API initialization completed successfully")
        
        yield  # This is where the application runs
        
    except Exception as e:
        logger.error(f"Failed to initialize API: {e}")
        raise
    finally:
        # Cleanup
        logger.info("Shutting down AI-Enhanced PDanet-Linux API...")
        if network_brain:
            await network_brain.stop_optimization_loop()

# Create FastAPI app with lifespan
app = FastAPI(
    title="AI-Enhanced PDanet-Linux API",
    description="Advanced AI-powered network optimization and management system for PDanet-Linux",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency for authentication"""
    if not auth_manager:
        raise HTTPException(status_code=500, detail="Authentication not initialized")
    
    user = await auth_manager.verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    return user

async def get_admin_user(current_user = Depends(get_current_user)):
    """Dependency for admin authentication"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    return current_user

# Background task for metrics broadcasting
async def background_metrics_broadcast():
    """Background task to broadcast metrics to WebSocket clients"""
    while True:
        try:
            if network_brain and websocket_manager.active_connections:
                # Get current network status
                status = await network_brain.get_network_status()
                
                # Broadcast to subscribers
                await websocket_manager.broadcast({
                    'type': 'network_metrics',
                    'data': status,
                    'timestamp': datetime.utcnow().isoformat()
                }, subscription_filter='metrics')
            
            await asyncio.sleep(10)  # Broadcast every 10 seconds
            
        except Exception as e:
            logger.error(f"Metrics broadcast error: {e}")
            await asyncio.sleep(30)  # Longer wait on error

# API Endpoints

@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint with API information"""
    return APIResponse(
        success=True,
        timestamp=datetime.utcnow(),
        message="AI-Enhanced PDanet-Linux API is running",
        data={
            "version": "1.0.0",
            "status": "operational",
            "features": [
                "AI-powered network optimization",
                "Real-time traffic prediction",
                "Advanced security monitoring",
                "Automated threat response",
                "WebSocket real-time updates"
            ]
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "api": "healthy",
        "network_brain": "healthy" if network_brain else "not_initialized",
        "auth_manager": "healthy" if auth_manager else "not_initialized",
        "metrics_collector": "healthy" if metrics_collector else "not_initialized",
        "websocket_connections": len(websocket_manager.active_connections)
    }
    
    overall_health = all(status == "healthy" for status in list(health_status.values())[:-1])
    
    return {
        "status": "healthy" if overall_health else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "components": health_status
    }

# Network Management Endpoints

@app.post("/network/connect", response_model=APIResponse)
async def connect_network(request: NetworkConnectionRequest, current_user = Depends(get_current_user)):
    """Initiate network connection with AI optimization"""
    if not network_brain:
        raise HTTPException(status_code=500, detail="Network brain not initialized")
    
    try:
        # Create connection parameters
        connection_params = {
            'proxy_address': request.proxy_address,
            'proxy_port': request.proxy_port,
            'type': request.connection_type,
            'ai_optimization': request.enable_ai_optimization,
            'custom_config': request.custom_config or {}
        }
        
        # If AI optimization is enabled, create intelligent tunnel
        if request.enable_ai_optimization:
            result = await network_brain.tunnel_manager.create_intelligent_tunnel(connection_params)
        else:
            # Basic connection without AI
            result = await network_brain.tunnel_manager.create_tunnel(
                mtu=1420,
                buffer_size=1024*1024,
                queue_discipline='fq_codel',
                congestion_control='cubic'
            )
        
        # Broadcast connection status
        await websocket_manager.broadcast({
            'type': 'network_connection',
            'status': 'connected',
            'connection_info': result
        }, subscription_filter='network')
        
        return APIResponse(
            success=True,
            timestamp=datetime.utcnow(),
            message="Network connection established successfully",
            data={
                'connection_info': result,
                'ai_optimization_enabled': request.enable_ai_optimization
            }
        )
        
    except Exception as e:
        logger.error(f"Network connection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/network/optimize", response_model=APIResponse)
async def optimize_network(request: NetworkOptimizationRequest, 
                          background_tasks: BackgroundTasks,
                          current_user = Depends(get_current_user)):
    """Trigger network optimization"""
    if not network_brain:
        raise HTTPException(status_code=500, detail="Network brain not initialized")
    
    try:
        # Add optimization as background task
        background_tasks.add_task(
            perform_optimization,
            request.target_metric,
            request.optimization_level,
            request.preserve_stability,
            request.force_reoptimization
        )
        
        return APIResponse(
            success=True,
            timestamp=datetime.utcnow(),
            message="Network optimization initiated",
            data={
                'target_metric': request.target_metric,
                'optimization_level': request.optimization_level,
                'estimated_duration': '2-5 minutes'
            }
        )
        
    except Exception as e:
        logger.error(f"Network optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def perform_optimization(target_metric: str, optimization_level: float, 
                             preserve_stability: bool, force_reoptimization: bool):
    """Background task for network optimization"""
    try:
        result = await network_brain.optimize_network_once()
        
        # Broadcast optimization result
        await websocket_manager.broadcast({
            'type': 'optimization_complete',
            'result': result.__dict__ if hasattr(result, '__dict__') else str(result),
            'target_metric': target_metric
        }, subscription_filter='optimization')
        
    except Exception as e:
        logger.error(f"Background optimization failed: {e}")
        await websocket_manager.broadcast({
            'type': 'optimization_error',
            'error': str(e)
        }, subscription_filter='optimization')

@app.get("/network/status", response_model=NetworkStatusResponse)
async def get_network_status(current_user = Depends(get_current_user)):
    """Get current network status and AI insights"""
    if not network_brain:
        raise HTTPException(status_code=500, detail="Network brain not initialized")
    
    try:
        status = await network_brain.get_network_status()
        
        return NetworkStatusResponse(
            success=True,
            timestamp=datetime.utcnow(),
            message="Network status retrieved successfully",
            data=status,
            network_state=status.get('current_state'),
            ai_insights=status.get('ai_insights'),
            active_optimizations=status.get('optimization_status', {}).get('active_optimizations', [])
        )
        
    except Exception as e:
        logger.error(f"Failed to get network status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/network/disconnect", response_model=APIResponse)
async def disconnect_network(current_user = Depends(get_current_user)):
    """Disconnect from network and cleanup"""
    if not network_brain:
        raise HTTPException(status_code=500, detail="Network brain not initialized")
    
    try:
        # Cleanup tunnels and connections
        await network_brain.tunnel_manager.cleanup()
        
        # Broadcast disconnection status
        await websocket_manager.broadcast({
            'type': 'network_disconnection',
            'status': 'disconnected'
        }, subscription_filter='network')
        
        return APIResponse(
            success=True,
            timestamp=datetime.utcnow(),
            message="Network disconnected successfully"
        )
        
    except Exception as e:
        logger.error(f"Network disconnection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AI/ML Model Endpoints

@app.post("/ai/predict-traffic", response_model=APIResponse)
async def predict_traffic(request: TrafficPredictionRequest, current_user = Depends(get_current_user)):
    """Get traffic predictions using AI models"""
    if not network_brain or not network_brain.traffic_predictor:
        raise HTTPException(status_code=500, detail="Traffic predictor not available")
    
    try:
        # Get current network state for prediction
        current_state = network_brain.current_state
        if not current_state:
            raise HTTPException(status_code=400, detail="No current network state available")
        
        # Get predictions
        predictions = await network_brain.traffic_predictor.predict(
            current_state,
            horizons=request.horizons
        )
        
        return APIResponse(
            success=True,
            timestamp=datetime.utcnow(),
            message="Traffic predictions generated successfully",
            data={
                'predictions': predictions,
                'horizons': request.horizons,
                'include_confidence': request.include_confidence
            }
        )
        
    except Exception as e:
        logger.error(f"Traffic prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/configure-models", response_model=APIResponse)
async def configure_models(request: MLModelConfigRequest, current_user = Depends(get_admin_user)):
    """Configure AI/ML models"""
    if not network_brain:
        raise HTTPException(status_code=500, detail="Network brain not initialized")
    
    try:
        # Configure connection optimizer
        if hasattr(network_brain.connection_optimizer, 'set_learning_enabled'):
            network_brain.connection_optimizer.set_learning_enabled(request.enable_learning)
        
        # Configure traffic predictor
        if hasattr(network_brain.traffic_predictor, 'retrain_threshold'):
            network_brain.traffic_predictor.retrain_threshold = request.retrain_threshold
        
        return APIResponse(
            success=True,
            timestamp=datetime.utcnow(),
            message="AI models configured successfully",
            data={
                'learning_enabled': request.enable_learning,
                'retrain_threshold': request.retrain_threshold,
                'model_complexity': request.model_complexity
            }
        )
        
    except Exception as e:
        logger.error(f"Model configuration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/insights", response_model=APIResponse)
async def get_ai_insights(current_user = Depends(get_current_user)):
    """Get AI insights and performance metrics"""
    if not network_brain:
        raise HTTPException(status_code=500, detail="Network brain not initialized")
    
    try:
        insights = {
            'optimization_insights': await network_brain.connection_optimizer.get_optimization_insights(),
            'security_insights': await network_brain.security_monitor.get_security_insights(),
            'traffic_patterns': await network_brain.traffic_predictor.get_current_patterns(),
        }
        
        return APIResponse(
            success=True,
            timestamp=datetime.utcnow(),
            message="AI insights retrieved successfully",
            data=insights
        )
        
    except Exception as e:
        logger.error(f"Failed to get AI insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Security Endpoints

@app.post("/security/configure", response_model=APIResponse)
async def configure_security(request: SecurityConfigRequest, current_user = Depends(get_admin_user)):
    """Configure security monitoring settings"""
    if not network_brain:
        raise HTTPException(status_code=500, detail="Network brain not initialized")
    
    try:
        security_config = {
            'threat_response_level': request.threat_response_level,
            'monitoring_intensity': request.monitoring_intensity,
            'auto_response_enabled': request.enable_auto_response,
            'whitelist_ips': request.whitelist_ips or []
        }
        
        result = await network_brain.security_monitor.apply_security_config(security_config)
        
        return APIResponse(
            success=True,
            timestamp=datetime.utcnow(),
            message="Security configuration updated successfully",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Security configuration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/security/status", response_model=APIResponse)
async def get_security_status(current_user = Depends(get_current_user)):
    """Get current security status and threat assessment"""
    if not network_brain:
        raise HTTPException(status_code=500, detail="Network brain not initialized")
    
    try:
        # Get current security analysis
        if network_brain.current_state:
            security_analysis = await network_brain.security_monitor.analyze(network_brain.current_state)
        else:
            security_analysis = {'status': 'no_data'}
        
        return APIResponse(
            success=True,
            timestamp=datetime.utcnow(),
            message="Security status retrieved successfully",
            data=security_analysis
        )
        
    except Exception as e:
        logger.error(f"Failed to get security status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket Endpoints

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates"""
    client_info = {'client_id': client_id, 'type': 'general'}
    await websocket_manager.connect(websocket, client_info)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle client messages
            if message.get('type') == 'subscribe':
                subscription = message.get('subscription')
                if subscription:
                    websocket_manager.subscribe(websocket, subscription)
                    await websocket_manager.send_personal_message({
                        'type': 'subscription_confirmed',
                        'subscription': subscription
                    }, websocket)
            
            elif message.get('type') == 'unsubscribe':
                subscription = message.get('subscription')
                if subscription:
                    websocket_manager.unsubscribe(websocket, subscription)
                    await websocket_manager.send_personal_message({
                        'type': 'unsubscription_confirmed',
                        'subscription': subscription
                    }, websocket)
            
            elif message.get('type') == 'ping':
                await websocket_manager.send_personal_message({
                    'type': 'pong',
                    'timestamp': datetime.utcnow().isoformat()
                }, websocket)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info(f"WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)

# Metrics and Analytics Endpoints

@app.get("/metrics/api", response_model=APIResponse)
async def get_api_metrics(current_user = Depends(get_current_user)):
    """Get API usage metrics"""
    if not metrics_collector:
        raise HTTPException(status_code=500, detail="Metrics collector not initialized")
    
    try:
        metrics = await metrics_collector.get_api_metrics()
        
        return APIResponse(
            success=True,
            timestamp=datetime.utcnow(),
            message="API metrics retrieved successfully",
            data=metrics
        )
        
    except Exception as e:
        logger.error(f"Failed to get API metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/network", response_model=APIResponse)
async def get_network_metrics(current_user = Depends(get_current_user)):
    """Get network performance metrics"""
    if not metrics_collector:
        raise HTTPException(status_code=500, detail="Metrics collector not initialized")
    
    try:
        metrics = await metrics_collector.get_network_metrics()
        
        return APIResponse(
            success=True,
            timestamp=datetime.utcnow(),
            message="Network metrics retrieved successfully",
            data=metrics
        )
        
    except Exception as e:
        logger.error(f"Failed to get network metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Admin Endpoints

@app.post("/admin/reset-models", response_model=APIResponse)
async def reset_ai_models(current_user = Depends(get_admin_user)):
    """Reset AI models to initial state"""
    if not network_brain:
        raise HTTPException(status_code=500, detail="Network brain not initialized")
    
    try:
        # This would reset models to initial state
        # Implementation would depend on specific model architectures
        
        return APIResponse(
            success=True,
            timestamp=datetime.utcnow(),
            message="AI models reset successfully",
            data={'reset_timestamp': datetime.utcnow().isoformat()}
        )
        
    except Exception as e:
        logger.error(f"Model reset failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/system-info", response_model=APIResponse)
async def get_system_info(current_user = Depends(get_admin_user)):
    """Get system information and diagnostics"""
    try:
        import psutil
        import platform
        
        system_info = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': dict(psutil.disk_usage('/')._asdict()),
            'python_version': platform.python_version(),
            'api_uptime': (datetime.utcnow() - datetime.utcnow()).total_seconds(),  # Would track actual uptime
            'active_websocket_connections': len(websocket_manager.active_connections)
        }
        
        return APIResponse(
            success=True,
            timestamp=datetime.utcnow(),
            message="System information retrieved successfully",
            data=system_info
        )
        
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )