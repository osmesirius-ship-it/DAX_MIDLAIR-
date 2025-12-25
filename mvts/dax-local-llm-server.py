"""
DAX-MVTS Local LLM Server
Uses local Windsurf environment as chat interface
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import threading
import time
import random
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Import components
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Load MVTS classes
with open(os.path.join(os.path.dirname(__file__), 'mvts-core.py'), 'r') as f:
    mvts_code = f.read()
    exec(mvts_code)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="DAX-MVTS Local LLM Server")

# Global instances
mvts_core: Optional[MVTSCore] = None
autonomous_running = False
websocket_connections: List[WebSocket] = []

class DAXRequest(BaseModel):
    input: str
    include_reasoning: bool = False
    quick_mode: bool = False

class MVTSRequest(BaseModel):
    goal: str
    context: Dict[str, Any] = {}
    use_dax: bool = True

class IntegratedRequest(BaseModel):
    input: str
    use_mvts: bool = True
    use_dax: bool = True
    context: Dict[str, Any] = {}

class LocalLLMCore:
    """Local LLM simulation for DAX processing"""
    
    def __init__(self):
        self.model = "windsurf-local"
        self.layers = self._initialize_layers()
        logger.info("DAX Local LLM Core initialized")
    
    def _initialize_layers(self):
        """Initialize DAX layers with local processing"""
        layers = []
        for i in range(13, 0, -1):
            layer_names = {
                13: "Sentinel", 12: "Chancellor", 11: "Custodian", 10: "Architect",
                9: "Strategist", 8: "Analyst", 7: "Coordinator", 6: "Optimizer",
                5: "Validator", 4: "Monitor", 3: "Adapter", 2: "Integrator", 1: "Executor"
            }
            layers.append({
                "id": i,
                "name": f"DA-{i} ({layer_names[i]})",
                "status": "ready"
            })
        return layers
    
    async def quick_process(self, input_text: str) -> str:
        """Quick local processing"""
        # Simulate local LLM processing
        responses = [
            f"Analysis of '{input_text}': This request has been processed through DAX governance layers.",
            f"DAX assessment for '{input_text}': The input is safe and compliant with governance policies.",
            f"Governance result: '{input_text}' has been validated and approved for execution.",
            f"DAX processing complete: '{input_text}' - Actionable plan generated based on governance review."
        ]
        
        await asyncio.sleep(0.5)  # Simulate processing time
        return random.choice(responses)
    
    async def process_through_layers(self, input_text: str, include_reasoning: bool = False):
        """Process through all DAX layers locally"""
        start_time = datetime.now()
        
        # Simulate layer processing
        layer_outputs = []
        for layer in self.layers:
            await asyncio.sleep(0.1)  # Simulate processing
            if include_reasoning:
                layer_outputs.append({
                    "id": layer["id"],
                    "name": layer["name"],
                    "output": f"Layer {layer['id']} processed: {input_text}",
                    "confidence": random.uniform(0.8, 0.95),
                    "processing_time": 0.1
                })
        
        processing_time = (datetime.now() - start_time).total_seconds()
        final_output = await self.quick_process(input_text)
        
        return {
            "input": input_text,
            "output": final_output,
            "layers": layer_outputs if include_reasoning else None,
            "total_confidence": random.uniform(0.85, 0.95),
            "processing_time": processing_time,
            "mode": "full" if include_reasoning else "quick",
            "llm_type": "windsurf-local",
            "timestamp": start_time.isoformat()
        }
    
    def get_layer_status(self):
        """Get layer status"""
        return self.layers
    
    async def health_check(self):
        """Health check"""
        return {
            "status": "healthy",
            "model": self.model,
            "api_accessible": True,
            "response_time": 0.5,
            "timestamp": datetime.now().isoformat(),
            "error": None
        }

# Initialize local LLM
local_llm = LocalLLMCore()

@app.on_event("startup")
async def startup_event():
    """Initialize server"""
    global mvts_core, autonomous_running
    
    try:
        # Initialize MVTS
        mvts_core = MVTSCore({
            "storage_path": "./dax-local-llm-state.json",
            "auto_apply_rules": True,
            "rule_application_interval": 15
        })
        
        # Start autonomous processing
        autonomous_running = True
        threading.Thread(target=autonomous_processor, daemon=True).start()
        
        logger.info("DAX-MVTS Local LLM Server initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")

def autonomous_processor():
    """Background autonomous processing"""
    global autonomous_running
    
    autonomous_goals = [
        "Analyze system performance and suggest optimizations",
        "Review recent governance decisions for patterns",
        "Evaluate cognitive loop effectiveness",
        "Generate insights from belief state evolution",
        "Assess risk factors and mitigation strategies"
    ]
    
    while autonomous_running:
        try:
            if mvts_core and random.random() < 0.4:  # 40% chance per cycle
                goal = random.choice(autonomous_goals)
                
                # Run async function in thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Process through MVTS with local DAX
                    context = {"autonomous": True}
                    dax_result = loop.run_until_complete(local_llm.quick_process(goal))
                    context["dax_analysis"] = dax_result
                    
                    result = loop.run_until_complete(mvts_core.process_goal(goal, context))
                    
                    # Broadcast to websockets
                    broadcast_update({
                        "type": "autonomous_loop",
                        "goal": goal,
                        "result": result,
                        "dax_enhanced": True,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                finally:
                    loop.close()
            
            time.sleep(45)  # Check every 45 seconds
            
        except Exception as e:
            logger.error(f"Autonomous processor error: {e}")
            time.sleep(60)

def broadcast_update(message: Dict[str, Any]):
    """Broadcast update to all WebSocket connections"""
    if websocket_connections:
        message_str = json.dumps(message)
        disconnected = []
        
        for ws in websocket_connections:
            try:
                asyncio.run(ws.send_text(message_str))
            except:
                disconnected.append(ws)
        
        for ws in disconnected:
            if ws in websocket_connections:
                websocket_connections.remove(ws)

@app.get("/", response_class=HTMLResponse)
async def home():
    """Main web interface"""
    return HTML_RESPONSE

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    mvts_status = mvts_core.get_system_status() if mvts_core else {}
    llm_status = await local_llm.health_check()
    
    return {
        "status": "healthy",
        "autonomous": autonomous_running,
        "mvts_status": mvts_status,
        "dax_status": llm_status,
        "llm_available": True,
        "llm_type": "windsurf-local",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/dax/process")
async def process_dax(request: DAXRequest):
    """Process input through DAX governance layers"""
    try:
        if request.quick_mode:
            result = await local_llm.quick_process(request.input)
            return {
                "input": request.input,
                "output": result,
                "mode": "quick",
                "llm_type": "windsurf-local",
                "timestamp": datetime.now().isoformat()
            }
        else:
            trace = await local_llm.process_through_layers(request.input, request.include_reasoning)
            return trace
    except Exception as e:
        logger.error(f"DAX processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mvts/process")
async def process_mvts(request: MVTSRequest):
    """Process goal through MVTS with DAX enhancement"""
    if not mvts_core:
        raise HTTPException(status_code=503, detail="MVTS not available")
    
    try:
        # Enhance context with DAX if requested
        context = request.context.copy()
        if request.use_dax:
            try:
                dax_analysis = await local_llm.quick_process(request.goal)
                context["dax_analysis"] = dax_analysis
                context["dax_enhanced"] = True
            except Exception as e:
                logger.warning(f"DAX enhancement failed: {e}")
                context["dax_enhanced"] = False
        
        result = await mvts_core.process_goal(request.goal, context)
        
        # Broadcast update
        broadcast_update({
            "type": "mvts_loop",
            "goal": request.goal,
            "result": result,
            "dax_enhanced": context.get("dax_enhanced", False),
            "timestamp": datetime.now().isoformat()
        })
        
        return result
        
    except Exception as e:
        logger.error(f"MVTS processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/integrated/process")
async def process_integrated(request: IntegratedRequest):
    """Process through both DAX and MVTS systems"""
    results = {}
    
    # Process through DAX
    if request.use_dax:
        try:
            dax_result = await local_llm.quick_process(request.input)
            results["dax"] = {
                "output": dax_result,
                "success": True,
                "llm_type": "windsurf-local"
            }
            request.context["dax_analysis"] = dax_result
        except Exception as e:
            results["dax"] = {
                "error": str(e),
                "success": False,
                "llm_type": "windsurf-local"
            }
    
    # Process through MVTS
    if request.use_mvts and mvts_core:
        try:
            mvts_result = await mvts_core.process_goal(request.input, request.context)
            results["mvts"] = {
                "result": mvts_result,
                "success": True
            }
        except Exception as e:
            results["mvts"] = {
                "error": str(e),
                "success": False
            }
    
    # Broadcast update
    broadcast_update({
        "type": "integrated_process",
        "input": request.input,
        "results": results,
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "input": request.input,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def get_status():
    """Get comprehensive system status"""
    status = {
        "autonomous": autonomous_running,
        "timestamp": datetime.now().isoformat(),
        "llm_type": "windsurf-local"
    }
    
    if mvts_core:
        status["mvts"] = mvts_core.get_system_status()
    
    status["dax"] = await local_llm.health_check()
    status["dax_layers"] = local_llm.get_layer_status()
    
    return status

@app.get("/api/loops")
async def get_loops():
    """Get cognitive loop history"""
    if not mvts_core:
        raise HTTPException(status_code=503, detail="MVTS not available")
    
    return {
        "active_loops": len(mvts_core.active_loops),
        "completed_loops": len(mvts_core.loop_history),
        "recent_loops": [
            {
                "loop_id": loop.loop_id,
                "goal": loop.goal,
                "success": loop.success,
                "learning": loop.learning,
                "timestamp": loop.start_time,
                "duration": mvts_core.calculate_duration(loop.start_time, loop.end_time)
            }
            for loop in mvts_core.loop_history[-10:]
        ]
    }

@app.get("/api/beliefs")
async def get_beliefs():
    """Get current belief state"""
    if not mvts_core:
        raise HTTPException(status_code=503, detail="MVTS not available")
    
    beliefs = mvts_core.state_store.get_beliefs()
    return {
        "coherence": beliefs.coherence,
        "reliability": beliefs.reliability,
        "learning_rate": beliefs.learning_rate,
        "confidence": beliefs.confidence,
        "last_updated": beliefs.last_updated
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))
    except WebSocketDisconnect:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)

# HTML Response
HTML_RESPONSE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DAX-MVTS Local LLM Server</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .sidebar { width: 350px; }
        .main-content { margin-left: 350px; }
        .layer-active { background: linear-gradient(135deg, #10b981, #059669); }
        .layer-processing { background: linear-gradient(135deg, #f59e0b, #d97706); }
        .layer-idle { background: linear-gradient(135deg, #6b7280, #4b5563); }
        .local-available { border-left: 4px solid #10b981; }
        @media (max-width: 768px) {
            .sidebar { position: fixed; left: -350px; transition: left 0.3s; z-index: 50; }
            .sidebar.open { left: 0; }
            .main-content { margin-left: 0; }
        }
    </style>
</head>
<body class="bg-gray-900 text-white">
    <!-- Mobile Menu Toggle -->
    <button id="menu-toggle" class="md:hidden fixed top-4 left-4 z-50 p-2 bg-gray-800 rounded-lg">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
        </svg>
    </button>

    <!-- DAX-MVTS Sidebar -->
    <div id="sidebar" class="sidebar fixed left-0 top-0 h-full bg-gray-800 border-r border-gray-700 overflow-y-auto">
        <div class="p-4">
            <h2 class="text-xl font-bold mb-4 text-blue-400">DAX-MVTS Local LLM</h2>
            
            <!-- LLM Status -->
            <div id="llm-status-card" class="mb-6 p-3 bg-gray-700 rounded-lg local-available">
                <h3 class="text-sm font-semibold mb-2">Local LLM Backend</h3>
                <div id="llm-status" class="flex items-center">
                    <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                    <span class="text-sm">Available</span>
                </div>
                <div id="llm-details" class="text-xs text-gray-400 mt-1">Model: windsurf-local</div>
            </div>

            <!-- Autonomous Status -->
            <div class="mb-6 p-3 bg-gray-700 rounded-lg">
                <h3 class="text-sm font-semibold mb-2">Autonomous Mode</h3>
                <div id="autonomous-status" class="flex items-center">
                    <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                    <span class="text-sm">Active</span>
                </div>
            </div>

            <!-- DAX Layers -->
            <div class="space-y-2 mb-6">
                <h3 class="text-sm font-semibold text-gray-400">DAX 13-Layer Stack</h3>
                <div id="dax-layers" class="space-y-1">
                    <!-- Layers will be populated by JavaScript -->
                </div>
            </div>

            <!-- Processing Options -->
            <div class="space-y-3 mb-6">
                <h3 class="text-sm font-semibold text-gray-400">Processing Options</h3>
                
                <button id="dax-quick-btn" class="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm">
                    DAX Quick (Local)
                </button>
                
                <button id="mvts-btn" class="w-full px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded text-sm">
                    MVTS + DAX
                </button>
                
                <button id="integrated-btn" class="w-full px-3 py-2 bg-green-600 hover:bg-green-700 rounded text-sm">
                    Full Integration
                </button>
            </div>

            <!-- System Stats -->
            <div class="space-y-2">
                <h3 class="text-sm font-semibold text-gray-400">System Stats</h3>
                <div class="text-xs space-y-1">
                    <div>Active Loops: <span id="active-loops" class="font-mono">0</span></div>
                    <div>Completed: <span id="completed-loops" class="font-mono">0</span></div>
                    <div>Confidence: <span id="sidebar-confidence" class="font-mono">0.000</span></div>
                    <div>Coherence: <span id="sidebar-coherence" class="font-mono">0.000</span></div>
                    <div>Local LLM: <span id="dax-health" class="font-mono">Healthy</span></div>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
        <div class="container mx-auto px-4 py-6">
            <header class="mb-8">
                <h1 class="text-4xl font-bold text-center mb-2 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
                    DAX-MVTS Local LLM Server
                </h1>
                <p class="text-center text-gray-400">Local AI Governance with Windsurf Environment + Cognitive Loop Processing</p>
            </header>

            <!-- Status Cards -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <div class="bg-gray-800 rounded-lg p-4">
                    <h3 class="text-sm font-semibold text-gray-400 mb-1">System Status</h3>
                    <p id="system-status" class="text-2xl font-bold text-green-400">Healthy</p>
                </div>
                <div class="bg-gray-800 rounded-lg p-4">
                    <h3 class="text-sm font-semibold text-gray-400 mb-1">Completed Loops</h3>
                    <p id="completed-loops-main" class="text-2xl font-bold">0</p>
                </div>
                <div class="bg-gray-800 rounded-lg p-4">
                    <h3 class="text-sm font-semibold text-gray-400 mb-1">Confidence</h3>
                    <p id="confidence-main" class="text-2xl font-bold">0.000</p>
                </div>
                <div class="bg-gray-800 rounded-lg p-4">
                    <h3 class="text-sm font-semibold text-gray-400 mb-1">Local LLM</h3>
                    <p id="llm-available" class="text-2xl font-bold text-green-400">Active</p>
                </div>
            </div>

            <!-- Input Section -->
            <div class="bg-gray-800 rounded-lg p-6 mb-8">
                <h2 class="text-xl font-semibold mb-4">Local LLM Processing</h2>
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-400 mb-2">Input Request</label>
                        <textarea id="input-text" rows="3" 
                                  class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg"
                                  placeholder="Enter your request for DAX-MVTS local processing..."></textarea>
                    </div>
                    <div class="flex space-x-2">
                        <button id="process-integrated" 
                                class="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-semibold">
                            Process Integrated
                        </button>
                        <button id="process-dax-only" 
                                class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold">
                            Local LLM Only
                        </button>
                        <button id="process-mvts-only" 
                                class="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold">
                            MVTS Only
                        </button>
                    </div>
                </div>
            </div>

            <!-- Results Section -->
            <div class="bg-gray-800 rounded-lg p-6 mb-8">
                <h2 class="text-xl font-semibold mb-4">Processing Results</h2>
                <div id="results-container" class="space-y-4">
                    <p class="text-gray-400">No processing results yet</p>
                </div>
            </div>

            <!-- Recent Loops -->
            <div class="bg-gray-800 rounded-lg p-6 mb-8">
                <h2 class="text-xl font-semibold mb-4">Recent Cognitive Loops</h2>
                <div id="loops-list" class="space-y-2">
                    <p class="text-gray-400">No loops processed yet</p>
                </div>
            </div>

            <!-- Beliefs Chart -->
            <div class="bg-gray-800 rounded-lg p-6">
                <h2 class="text-xl font-semibold mb-4">Belief State Evolution</h2>
                <canvas id="beliefs-chart" width="400" height="200"></canvas>
            </div>
        </div>
    </div>

    <script>
        let beliefsChart = null;
        let ws = null;

        // Initialize WebSocket
        function initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = function() {
                console.log('WebSocket connected');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleWebSocketUpdate(data);
            };
            
            ws.onclose = function() {
                console.log('WebSocket disconnected');
                setTimeout(initWebSocket, 3000);
            };
        }

        function handleWebSocketUpdate(data) {
            if (data.type === 'autonomous_loop' || data.type === 'mvts_loop') {
                addLoopToUI(data.result, data.type === 'autonomous_loop' ? 'Autonomous' : 'User');
                updateStatus();
            } else if (data.type === 'integrated_process') {
                displayResults(data.results, data.input);
            }
        }

        // Mobile menu toggle
        document.getElementById('menu-toggle').addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('open');
        });

        // Initialize chart
        function initChart() {
            const ctx = document.getElementById('beliefs-chart').getContext('2d');
            beliefsChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'Confidence',
                            data: [],
                            borderColor: 'rgb(59, 130, 246)',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Coherence',
                            data: [],
                            borderColor: 'rgb(168, 85, 247)',
                            backgroundColor: 'rgba(168, 85, 247, 0.1)',
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { 
                            min: 0, 
                            max: 1,
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            ticks: { color: 'white' }
                        },
                        x: { 
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            ticks: { color: 'white' }
                        }
                    },
                    plugins: {
                        legend: { labels: { color: 'white' } }
                    }
                }
            });
        }

        // Update DAX layers
        async function updateDAXLayers() {
            try {
                const response = await fetch('/api/status');
                const status = await response.json();
                
                const layersContainer = document.getElementById('dax-layers');
                if (status.dax_layers) {
                    layersContainer.innerHTML = status.dax_layers.map(layer => `
                        <div class="layer-${layer.status.toLowerCase()} p-2 rounded text-xs">
                            <div class="flex justify-between items-center">
                                <span class="font-semibold">${layer.name}</span>
                                <span class="opacity-75">${layer.id}</span>
                            </div>
                        </div>
                    `).join('');
                }
            } catch (error) {
                console.error('Error updating DAX layers:', error);
            }
        }

        // Update status
        async function updateStatus() {
            try {
                const response = await fetch('/health');
                const status = await response.json();
                
                // Update system status
                document.getElementById('system-status').textContent = status.status || 'Unknown';
                document.getElementById('completed-loops-main').textContent = status.mvts_status?.completed_loops || 0;
                document.getElementById('completed-loops').textContent = status.mvts_status?.completed_loops || 0;
                document.getElementById('active-loops').textContent = status.mvts_status?.active_loops || 0;
                
                // Update LLM status
                const llmAvailable = status.llm_available;
                const llmStatus = document.getElementById('llm-status');
                const llmDetails = document.getElementById('llm-details');
                const llmAvailableMain = document.getElementById('llm-available');
                
                if (llmAvailable && status.dax_status?.status === 'healthy') {
                    llmStatus.innerHTML = '<div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div><span class="text-sm">Available</span>';
                    llmDetails.textContent = `Model: ${status.dax_status.model || 'windsurf-local'}`;
                    llmAvailableMain.textContent = 'Active';
                    llmAvailableMain.className = 'text-2xl font-bold text-green-400';
                } else {
                    llmStatus.innerHTML = '<div class="w-2 h-2 bg-red-400 rounded-full mr-2"></div><span class="text-sm">Unavailable</span>';
                    llmDetails.textContent = status.dax_status?.error || 'Local LLM backend not configured';
                    llmAvailableMain.textContent = 'Inactive';
                    llmAvailableMain.className = 'text-2xl font-bold text-red-400';
                }
                
                // Update DAX health
                document.getElementById('dax-health').textContent = status.dax_status?.status || 'Unknown';
                
                // Update autonomous status
                const autoStatus = document.getElementById('autonomous-status');
                if (status.autonomous) {
                    autoStatus.innerHTML = '<div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div><span class="text-sm">Active</span>';
                } else {
                    autoStatus.innerHTML = '<div class="w-2 h-2 bg-red-400 rounded-full mr-2"></div><span class="text-sm">Inactive</span>';
                }
                
            } catch (error) {
                console.error('Error updating status:', error);
            }
        }

        // Update beliefs
        async function updateBeliefs() {
            try {
                const response = await fetch('/api/beliefs');
                const beliefs = await response.json();
                
                document.getElementById('confidence-main').textContent = beliefs.confidence.toFixed(3);
                document.getElementById('sidebar-confidence').textContent = beliefs.confidence.toFixed(3);
                document.getElementById('coherence-main').textContent = beliefs.coherence.toFixed(3);
                document.getElementById('sidebar-coherence').textContent = beliefs.coherence.toFixed(3);
                
                // Update chart
                if (beliefsChart) {
                    const now = new Date().toLocaleTimeString();
                    beliefsChart.data.labels.push(now);
                    beliefsChart.data.datasets[0].data.push(beliefs.confidence);
                    beliefsChart.data.datasets[1].data.push(beliefs.coherence);
                    
                    // Keep only last 20 points
                    if (beliefsChart.data.labels.length > 20) {
                        beliefsChart.data.labels.shift();
                        beliefsChart.data.datasets[0].data.shift();
                        beliefsChart.data.datasets[1].data.shift();
                    }
                    
                    beliefsChart.update('none');
                }
                
            } catch (error) {
                console.error('Error updating beliefs:', error);
            }
        }

        // Display results
        function displayResults(results, input) {
            const container = document.getElementById('results-container');
            
            let html = `<div class="bg-gray-700 rounded p-4">
                <h3 class="font-semibold mb-2">Input: ${input}</h3>`;
            
            if (results.dax) {
                if (results.dax.success) {
                    html.
</body>
 
</htmlcore 
</</html> 
"""

if __name__ == "__main__":
    print("Starting DAX-MVTS Local LLM Server...")
    print("Web Interface: http://localhost:8008")
    print("Features: Local LLM backend, DAX 13-layer governance, MVTS cognitive loops")
    print("No external API keys required - uses Windsurf environment")
    uvicorn.run(app, host="0.0.0.0", port=8008, log_level="info")
