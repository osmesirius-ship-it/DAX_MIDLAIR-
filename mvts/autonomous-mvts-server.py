"""
Autonomous MVTS Server with DAX 13-Layer Governance & BT Integration
Standalone web server with sidebar governance panel and autonomous processing
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

# Import MVTS and DAX components
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
app = FastAPI(title="Autonomous MVTS Server")

# Global instances
mvts_core: Optional[MVTSCore] = None
autonomous_running = False
websocket_connections: List[WebSocket] = []

class GoalRequest(BaseModel):
    goal: str
    context: Dict[str, Any] = {}
    priority: str = "normal"

class BTRequest(BaseModel):
    query: str
    context: Dict[str, Any] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize autonomous MVTS server"""
    global mvts_core, autonomous_running
    try:
        mvts_core = MVTSCore({
            "storage_path": "./autonomous-mvts-state.json",
            "auto_apply_rules": True,
            "rule_application_interval": 10
        })
        
        # Start autonomous processing
        autonomous_running = True
        threading.Thread(target=autonomous_processor, daemon=True).start()
        
        logger.info("Autonomous MVTS Server initialized")
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")

def autonomous_processor():
    """Background autonomous processing"""
    global autonomous_running
    
    autonomous_goals = [
        "Monitor system health and optimize performance",
        "Analyze recent cognitive loops for improvement patterns",
        "Update belief state based on new information",
        "Generate insights from memory patterns",
        "Optimize learning parameters"
    ]
    
    while autonomous_running:
        try:
            if mvts_core and random.random() < 0.3:  # 30% chance per cycle
                goal = random.choice(autonomous_goals)
                
                # Run async function in thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    result = loop.run_until_complete(
                        mvts_core.process_goal(goal, {"autonomous": True})
                    )
                    
                    # Broadcast to websockets
                    broadcast_update({
                        "type": "autonomous_loop",
                        "goal": goal,
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                finally:
                    loop.close()
            
            time.sleep(30)  # Check every 30 seconds
            
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
    """Main MVTS web interface with DAX sidebar"""
    return HTML_RESPONSE

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if mvts_core:
        status = mvts_core.get_system_status()
        return {
            "status": "healthy",
            "autonomous": autonomous_running,
            "mvts_status": status,
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "status": "initializing",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/goal")
async def process_goal(request: GoalRequest):
    """Process goal through MVTS cognitive loop"""
    if not mvts_core:
        raise HTTPException(status_code=503, detail="MVTS not initialized")
    
    try:
        result = await mvts_core.process_goal(request.goal, request.context)
        
        # Broadcast update
        broadcast_update({
            "type": "user_goal",
            "goal": request.goal,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    except Exception as e:
        logger.error(f"Error processing goal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bt-query")
async def bt_query(request: BTRequest):
    """Brain-Trust integration endpoint"""
    try:
        # Simulate BT processing
        bt_response = {
            "query": request.query,
            "response": f"BT processed: {request.query}",
            "confidence": random.uniform(0.7, 0.95),
            "sources": ["source1", "source2", "source3"],
            "timestamp": datetime.now().isoformat()
        }
        
        return bt_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    """Get MVTS system status"""
    if not mvts_core:
        raise HTTPException(status_code=503, detail="MVTS not initialized")
    
    return mvts_core.get_system_status()

@app.get("/api/loops")
async def get_loops():
    """Get cognitive loop history"""
    if not mvts_core:
        raise HTTPException(status_code=503, detail="MVTS not initialized")
    
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
        raise HTTPException(status_code=503, detail="MVTS not initialized")
    
    beliefs = mvts_core.state_store.get_beliefs()
    return {
        "coherence": beliefs.coherence,
        "reliability": beliefs.reliability,
        "learning_rate": beliefs.learning_rate,
        "confidence": beliefs.confidence,
        "last_updated": beliefs.last_updated
    }

@app.get("/api/dax-layers")
async def get_dax_layers():
    """Get DAX 13-layer governance status"""
    layers = []
    for i in range(13, 0, -1):
        layer_name = f"DA-{i}"
        if i == 1:
            layer_name = "DA-1 (Executor)"
        elif i == 13:
            layer_name = "DA-13 (Sentinel)"
        
        layers.append({
            "id": i,
            "name": layer_name,
            "status": random.choice(["active", "idle", "processing"]),
            "confidence": random.uniform(0.7, 0.95),
            "last_activity": datetime.now().isoformat()
        })
    
    return {"layers": layers}

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

# Complete HTML Response with DAX Sidebar
HTML_RESPONSE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous MVTS Server</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .sidebar { width: 320px; }
        .main-content { margin-left: 320px; }
        .layer-active { background: linear-gradient(135deg, #10b981, #059669); }
        .layer-processing { background: linear-gradient(135deg, #f59e0b, #d97706); }
        .layer-idle { background: linear-gradient(135deg, #6b7280, #4b5563); }
        @media (max-width: 768px) {
            .sidebar { position: fixed; left: -320px; transition: left 0.3s; z-index: 50; }
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

    <!-- DAX Sidebar -->
    <div id="sidebar" class="sidebar fixed left-0 top-0 h-full bg-gray-800 border-r border-gray-700 overflow-y-auto">
        <div class="p-4">
            <h2 class="text-xl font-bold mb-4 text-purple-400">DAX Governance</h2>
            
            <!-- Autonomous Status -->
            <div class="mb-6 p-3 bg-gray-700 rounded-lg">
                <h3 class="text-sm font-semibold mb-2">Autonomous Mode</h3>
                <div id="autonomous-status" class="flex items-center">
                    <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                    <span class="text-sm">Active</span>
                </div>
            </div>

            <!-- DAX Layers -->
            <div class="space-y-2">
                <h3 class="text-sm font-semibold text-gray-400">13-Layer Stack</h3>
                <div id="dax-layers" class="space-y-1">
                    <!-- Layers will be populated by JavaScript -->
                </div>
            </div>

            <!-- BT Integration -->
            <div class="mt-6 p-3 bg-gray-700 rounded-lg">
                <h3 class="text-sm font-semibold mb-2">Brain-Trust</h3>
                <input id="bt-query" type="text" placeholder="BT Query..." 
                       class="w-full px-2 py-1 bg-gray-600 rounded text-sm">
                <button id="bt-send" class="mt-2 w-full px-2 py-1 bg-purple-600 hover:bg-purple-700 rounded text-sm">
                    Query BT
                </button>
                <div id="bt-response" class="mt-2 text-xs text-gray-400"></div>
            </div>

            <!-- System Stats -->
            <div class="mt-6 space-y-2">
                <h3 class="text-sm font-semibold text-gray-400">System Stats</h3>
                <div class="text-xs space-y-1">
                    <div>Active Loops: <span id="active-loops" class="font-mono">0</span></div>
                    <div>Completed: <span id="completed-loops" class="font-mono">0</span></div>
                    <div>Confidence: <span id="sidebar-confidence" class="font-mono">0.000</span></div>
                    <div>Coherence: <span id="sidebar-coherence" class="font-mono">0.000</span></div>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
        <div class="container mx-auto px-4 py-6">
            <header class="mb-8">
                <h1 class="text-4xl font-bold text-center mb-2 bg-gradient-to-r from-purple-400 to-blue-600 bg-clip-text text-transparent">
                    Autonomous MVTS Server
                </h1>
                <p class="text-center text-gray-400">Minimum Viable Thinking Server with DAX Governance</p>
            </header>

            <!-- Status Cards -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <div class="bg-gray-800 rounded-lg p-4">
                    <h3 class="text-sm font-semibold text-gray-400 mb-1">System Status</h3>
                    <p id="system-status" class="text-2xl font-bold text-green-400">Initializing...</p>
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
                    <h3 class="text-sm font-semibold text-gray-400 mb-1">Coherence</h3>
                    <p id="coherence-main" class="text-2xl font-bold">0.000</p>
                </div>
            </div>

            <!-- Goal Input -->
            <div class="bg-gray-800 rounded-lg p-6 mb-8">
                <h2 class="text-xl font-semibold mb-4">Process Goal</h2>
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-400 mb-2">Goal Description</label>
                        <textarea id="goal-input" rows="3" 
                                  class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg"
                                  placeholder="Enter your goal here..."></textarea>
                    </div>
                    <button id="process-goal" 
                            class="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold">
                        Process Goal
                    </button>
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
                <h2 class="text-xl font-semibold mb-4">Belief State</h2>
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
            if (data.type === 'autonomous_loop') {
                addLoopToUI(data.result, 'Autonomous');
                updateStatus();
            } else if (data.type === 'user_goal') {
                addLoopToUI(data.result, 'User');
                updateStatus();
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
                type: 'radar',
                data: {
                    labels: ['Coherence', 'Reliability', 'Learning Rate', 'Confidence'],
                    datasets: [{
                        label: 'Current Beliefs',
                        data: [0, 0, 0, 0],
                        borderColor: 'rgb(147, 51, 234)',
                        backgroundColor: 'rgba(147, 51, 234, 0.2)',
                        pointBackgroundColor: 'rgb(147, 51, 234)',
                        pointBorderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 1,
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            ticks: { color: 'white' },
                            pointLabels: { color: 'white' }
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
                const response = await fetch('/api/dax-layers');
                const data = await response.json();
                
                const layersContainer = document.getElementById('dax-layers');
                layersContainer.innerHTML = data.layers.map(layer => `
                    <div class="layer-${layer.status} p-2 rounded text-xs">
                        <div class="flex justify-between items-center">
                            <span class="font-semibold">${layer.name}</span>
                            <span class="opacity-75">${layer.confidence.toFixed(2)}</span>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error updating DAX layers:', error);
            }
        }

        // Update status
        async function updateStatus() {
            try {
                const response = await fetch('/health');
                const status = await response.json();
                
                const completed = status.mvts_status?.completed_loops || 0;
                document.getElementById('completed-loops-main').textContent = completed;
                document.getElementById('completed-loops').textContent = completed;
                document.getElementById('active-loops').textContent = status.mvts_status?.active_loops || 0;
                document.getElementById('system-status').textContent = status.status || 'Unknown';
                
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
                    beliefsChart.data.datasets[0].data = [
                        beliefs.coherence,
                        beliefs.reliability,
                        beliefs.learning_rate,
                        beliefs.confidence
                    ];
                    beliefsChart.update();
                }
                
            } catch (error) {
                console.error('Error updating beliefs:', error);
            }
        }

        // Update loops
        async function updateLoops() {
            try {
                const response = await fetch('/api/loops');
                const data = await response.json();
                
                const loopsList = document.getElementById('loops-list');
                if (data.recent_loops.length === 0) {
                    loopsList.innerHTML = '<p class="text-gray-400">No loops processed yet</p>';
                } else {
                    loopsList.innerHTML = data.recent_loops.map(loop => `
                        <div class="bg-gray-700 rounded p-3">
                            <div class="flex justify-between items-center">
                                <div>
                                    <p class="font-semibold">${loop.goal.substring(0, 50)}${loop.goal.length > 50 ? '...' : ''}</p>
                                    <p class="text-sm text-gray-400">ID: ${loop.loop_id} | Duration: ${loop.duration.toFixed(3)}s</p>
                                </div>
                                <div class="text-right">
                                    <span class="px-2 py-1 rounded text-sm ${loop.success ? 'bg-green-600' : 'bg-red-600'}">
                                        ${loop.success ? 'Success' : 'Failed'}
                                    </span>
                                </div>
                            </div>
                            ${loop.learning.length > 0 ? `
                                <div class="mt-2">
                                    <p class="text-sm text-gray-400">Learning:</p>
                                    <ul class="text-sm text-gray-300 list-disc list-inside">
                                        ${loop.learning.map(item => `<li>${item}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    `).join('');
                }
                
            } catch (error) {
                console.error('Error updating loops:', error);
            }
        }

        function addLoopToUI(result, source) {
            const loopsList = document.getElementById('loops-list');
            const newLoop = document.createElement('div');
            newLoop.className = 'bg-gray-700 rounded p-3 border-l-4 border-purple-500';
            newLoop.innerHTML = `
                <div class="flex justify-between items-center">
                    <div>
                        <p class="font-semibold">${result.goal.substring(0, 50)}${result.goal.length > 50 ? '...' : ''}</p>
                        <p class="text-sm text-gray-400">ID: ${result.loop_id} | Source: ${source} | Duration: ${result.duration.toFixed(3)}s</p>
                    </div>
                    <div class="text-right">
                        <span class="px-2 py-1 rounded text-sm ${result.success ? 'bg-green-600' : 'bg-red-600'}">
                            ${result.success ? 'Success' : 'Failed'}
                        </span>
                    </div>
                </div>
            `;
            
            if (loopsList.firstChild?.classList?.contains('text-gray-400')) {
                loopsList.removeChild(loopsList.firstChild);
            }
            
            loopsList.insertBefore(newLoop, loopsList.firstChild);
            
            // Keep only last 10 loops
            while (loopsList.children.length > 10) {
                loopsList.removeChild(loopsList.lastChild);
            }
        }

        // Process goal
        async function processGoal() {
            const goalInput = document.getElementById('goal-input');
            const goal = goalInput.value.trim();
            
            if (!goal) {
                alert('Please enter a goal');
                return;
            }
            
            const button = document.getElementById('process-goal');
            button.disabled = true;
            button.textContent = 'Processing...';
            
            try {
                const response = await fetch('/api/goal', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        goal: goal,
                        context: {}
                    })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    goalInput.value = '';
                    addLoopToUI(result, 'User');
                    await updateStatus();
                    await updateBeliefs();
                    
                    alert(`Goal processed successfully!\\nLoop ID: ${result.loop_id}\\nSuccess: ${result.success}`);
                } else {
                    alert(`Error: ${result.detail}`);
                }
                
            } catch (error) {
                console.error('Error processing goal:', error);
                alert('Error processing goal');
            } finally {
                button.disabled = false;
                button.textContent = 'Process Goal';
            }
        }

        // BT Query
        async function btQuery() {
            const queryInput = document.getElementById('bt-query');
            const responseDiv = document.getElementById('bt-response');
            const query = queryInput.value.trim();
            
            if (!query) {
                responseDiv.textContent = 'Please enter a query';
                return;
            }
            
            try {
                const response = await fetch('/api/bt-query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        query: query,
                        context: {}
                    })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    responseDiv.innerHTML = `
                        <div class="mt-2 p-2 bg-gray-600 rounded">
                            <p class="text-xs">${result.response}</p>
                            <p class="text-xs text-gray-400 mt-1">Confidence: ${result.confidence.toFixed(2)}</p>
                        </div>
                    `;
                    queryInput.value = '';
                } else {
                    responseDiv.textContent = 'Error: ' + result.detail;
                }
                
            } catch (error) {
                console.error('Error with BT query:', error);
                responseDiv.textContent = 'Error processing query';
            }
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            initChart();
            initWebSocket();
            updateStatus();
            updateBeliefs();
            updateLoops();
            updateDAXLayers();
            
            // Setup event listeners
            document.getElementById('process-goal').addEventListener('click', processGoal);
            document.getElementById('bt-send').addEventListener('click', btQuery);
            
            // Enter key handlers
            document.getElementById('goal-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    processGoal();
                }
            });
            
            document.getElementById('bt-query').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    btQuery();
                }
            });
            
            // Auto-refresh
            setInterval(() => {
                updateStatus();
                updateBeliefs();
                updateLoops();
                updateDAXLayers();
            }, 5000);
        });
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    print("Starting Autonomous MVTS Server...")
    print("Web Interface: http://localhost:8005")
    print("Features: DAX 13-layer sidebar, BT integration, autonomous processing")
    uvicorn.run(app, host="0.0.0.0", port=8005, log_level="info")
