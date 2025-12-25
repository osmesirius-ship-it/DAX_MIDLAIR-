"""
MVTS Core Server
Web interface for Minimum Viable Thinking Server
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Import MVTS components
import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import directly from the file
exec(open(os.path.join(os.path.dirname(__file__), 'mvts-core.py')).read())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="MVTS Core Server", description="Minimum Viable Thinking Server API")

# Global MVTS instance
mvts_core: Optional[MVTSCore] = None

class GoalRequest(BaseModel):
    goal: str
    context: Dict[str, Any] = {}

class GoalResponse(BaseModel):
    loop_id: str
    goal: str
    success: bool
    duration: float
    phases_completed: int
    learning: List[str]
    final_beliefs: Dict[str, Any]
    phase_summary: List[Dict[str, Any]]

@app.on_event("startup")
async def startup_event():
    """Initialize MVTS core"""
    global mvts_core
    try:
        mvts_core = MVTSCore({
            "storage_path": "./mvts-web-state.json",
            "auto_apply_rules": True,
            "rule_application_interval": 30
        })
        logger.info("MVTS Core Server initialized")
    except Exception as e:
        logger.error(f"Failed to initialize MVTS: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MVTS Core Server",
        "description": "Minimum Viable Thinking Server - Cognitive Loop Processing",
        "version": "1.0.0",
        "status": "operational" if mvts_core else "initializing"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if mvts_core:
        status = mvts_core.get_system_status()
        return {
            "status": "healthy",
            "mvts_status": status,
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "status": "initializing",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/goal", response_model=GoalResponse)
async def process_goal(request: GoalRequest):
    """Process goal through MVTS cognitive loop"""
    if not mvts_core:
        raise HTTPException(status_code=503, detail="MVTS not initialized")
    
    try:
        result = await mvts_core.process_goal(request.goal, request.context)
        return GoalResponse(**result)
    except Exception as e:
        logger.error(f"Error processing goal: {e}")
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
            for loop in mvts_core.loop_history[-10:]  # Last 10 loops
        ]
    }

@app.get("/api/beliefs")
async def get_beliefs():
    """Get current belief state"""
    if not mvts_core:
        raise HTTPException(status_code=503, detail="MVTS not initialized")
    
    beliefs = mvts_core.state_store.get_beliefs()
    return {
        "beliefs": {
            "coherence": beliefs.coherence,
            "reliability": beliefs.reliability,
            "learning_rate": beliefs.learning_rate,
            "confidence": beliefs.confidence,
            "last_updated": beliefs.last_updated
        }
    }

@app.get("/api/memory")
async def get_memory():
    """Get recent memories"""
    if not mvts_core:
        raise HTTPException(status_code=503, detail="MVTS not initialized")
    
    memories = mvts_core.state_store.get_recent_memories(20)
    return {
        "memories": memories,
        "count": len(memories)
    }

# HTML interface
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MVTS Core Server</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen">
    <div class="container mx-auto px-4 py-6">
        <header class="mb-8">
            <h1 class="text-4xl font-bold text-center mb-2 bg-gradient-to-r from-purple-400 to-blue-600 bg-clip-text text-transparent">
                MVTS Core Server
            </h1>
            <p class="text-center text-gray-400">Minimum Viable Thinking Server - Cognitive Loop Processing</p>
        </header>

        <!-- Status Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div class="bg-gray-800 rounded-lg p-4">
                <h3 class="text-sm font-semibold text-gray-400 mb-1">System Status</h3>
                <p id="system-status" class="text-2xl font-bold text-green-400">Healthy</p>
            </div>
            <div class="bg-gray-800 rounded-lg p-4">
                <h3 class="text-sm font-semibold text-gray-400 mb-1">Completed Loops</h3>
                <p id="completed-loops" class="text-2xl font-bold">0</p>
            </div>
            <div class="bg-gray-800 rounded-lg p-4">
                <h3 class="text-sm font-semibold text-gray-400 mb-1">Confidence</h3>
                <p id="confidence" class="text-2xl font-bold">0.000</p>
            </div>
            <div class="bg-gray-800 rounded-lg p-4">
                <h3 class="text-sm font-semibold text-gray-400 mb-1">Coherence</h3>
                <p id="coherence" class="text-2xl font-bold">0.000</p>
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

    <script>
        let beliefsChart = null;

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
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgb(147, 51, 234)'
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

        // Update status
        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const status = await response.json();
                
                document.getElementById('completed-loops').textContent = status.completed_loops;
                document.getElementById('system-status').textContent = 'Healthy';
                document.getElementById('system-status').className = 'text-2xl font-bold text-green-400';
                
            } catch (error) {
                console.error('Error updating status:', error);
                document.getElementById('system-status').textContent = 'Error';
                document.getElementById('system-status').className = 'text-2xl font-bold text-red-400';
            }
        }

        // Update beliefs
        async function updateBeliefs() {
            try {
                const response = await fetch('/api/beliefs');
                const data = await response.json();
                const beliefs = data.beliefs;
                
                document.getElementById('confidence').textContent = beliefs.confidence.toFixed(3);
                document.getElementById('coherence').textContent = beliefs.coherence.toFixed(3);
                
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
                    await updateStatus();
                    await updateBeliefs();
                    await updateLoops();
                    
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

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            initChart();
            updateStatus();
            updateBeliefs();
            updateLoops();
            
            // Setup event listeners
            document.getElementById('process-goal').addEventListener('click', processGoal);
            
            // Auto-refresh every 5 seconds
            setInterval(() => {
                updateStatus();
                updateBeliefs();
                updateLoops();
            }, 5000);
        });
    </script>
</body>
</html>
"""

@app.get("/web")
async def web_interface():
    """MVTS web interface"""
    return HTML_INTERFACE

if __name__ == "__main__":
    print("Starting MVTS Core Server...")
    print("Web Interface: http://localhost:8003/web")
    print("API Health: http://localhost:8003/health")
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
