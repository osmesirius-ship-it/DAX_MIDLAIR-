"""
MVTS-EDI Integrated Server
Combines MVTS cognitive loops with EDI real-time anomaly detection
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))
sys.path.append(os.path.dirname(__file__))  # Add current directory for mvts_core

from edi import DAXEDIIntegration
from mvts_core import MVTSCore, CognitiveLoop, CognitivePhase
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dataclasses import asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="MVTS-EDI Integrated Server")

# Global instances
mvts_core: Optional[MVTSCore] = None
edi_integration: Optional[DAXEDIIntegration] = None

class MVTSEDIRequest(BaseModel):
    goal: str
    context: Dict[str, Any] = {}
    sensor_data: Optional[List[List[float]]] = None
    residual_data: Optional[List[List[float]]] = None

class MVTSEDIResponse(BaseModel):
    loop_id: str
    goal: str
    success: bool
    duration: float
    phases_completed: int
    learning: List[str]
    final_beliefs: Dict[str, Any]
    edi_outputs: Optional[Dict[str, Any]] = None
    governance_bias: Optional[Dict[str, Any]] = None
    phase_summary: List[Dict[str, Any]]

@app.on_event("startup")
async def startup_event():
    """Initialize MVTS and EDI integration"""
    global mvts_core, edi_integration
    
    try:
        # Initialize EDI
        edi_integration = DAXEDIIntegration(fs=200, window_s=2.0)
        logger.info("EDI integration initialized")
        
        # Initialize MVTS with EDI integration
        mvts_core = MVTSCore({
            "storage_path": "./mvts-edi-state.json",
            "auto_apply_rules": True,
            "rule_application_interval": 30,  # 30 seconds
            "edi_integration": edi_integration
        })
        
        logger.info("MVTS-EDI integrated server initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize MVTS-EDI server: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MVTS-EDI Integrated Server",
        "status": "operational",
        "components": {
            "mvts": mvts_core is not None,
            "edi": edi_integration is not None
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    mvts_status = mvts_core.get_system_status() if mvts_core else {}
    edi_health = edi_integration.edi.get_system_health() if edi_integration else {}
    
    return {
        "status": "healthy",
        "mvts": mvts_status,
        "edi": edi_health,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/mvts-edi/process", response_model=MVTSEDIResponse)
async def process_goal_with_edi(request: MVTSEDIRequest):
    """Process goal through MVTS with EDI integration"""
    if not mvts_core or not edi_integration:
        raise HTTPException(status_code=503, detail="MVTS-EDI integration not available")
    
    try:
        # Process sensor data through EDI if provided
        edi_outputs = None
        governance_bias = None
        
        if request.sensor_data and request.residual_data:
            edi_result = edi_integration.process_sensor_data(
                request.sensor_data,
                request.residual_data
            )
            edi_outputs = edi_result
            governance_bias = edi_integration.get_governance_bias()
            
            logger.info(f"EDI processing complete: coherence={edi_result.get('coherence', 0):.3f}")
        
        # Process goal through MVTS with EDI context
        enhanced_context = {
            **request.context,
            "edi_outputs": edi_outputs,
            "governance_bias": governance_bias,
            "cognitive_load": edi_outputs.get("risk_assessment", {}).get("score", 0) if edi_outputs else 0
        }
        
        # Convert goal to string if it's a dict
        goal_str = json.dumps(request.goal) if isinstance(request.goal, dict) else request.goal
        
        result = await mvts_core.process_goal(goal_str, enhanced_context)
        
        # Add EDI information to result
        if edi_outputs:
            result["edi_outputs"] = edi_outputs
            result["governance_bias"] = governance_bias
        
        return MVTSEDIResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing goal with EDI: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mvts/status")
async def get_mvts_status():
    """Get MVTS system status"""
    if not mvts_core:
        raise HTTPException(status_code=503, detail="MVTS not available")
    
    return mvts_core.get_system_status()

@app.get("/api/edi/status")
async def get_edi_status():
    """Get EDI system status"""
    if not edi_integration:
        raise HTTPException(status_code=503, detail="EDI not available")
    
    return {
        "system_health": edi_integration.edi.get_system_health(),
        "governance_bias": edi_integration.get_governance_bias(),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/mvts-edi/simulation")
async def run_integrated_simulation(scenario: str = "solar_storm", duration: float = 20.0):
    """Run integrated MVTS-EDI simulation"""
    if not mvts_core or not edi_integration:
        raise HTTPException(status_code=503, detail="MVTS-EDI integration not available")
    
    try:
        # Generate synthetic sensor data
        from phase10_edi_sim import simulate_scenario
        
        t, X, R = simulate_scenario(fs=200, T_s=duration, scenario=scenario)
        
        # Process through EDI
        edi_result = edi_integration.process_sensor_data(X.tolist(), R.tolist())
        
        # Process cognitive goal based on scenario
        scenario_goals = {
            "solar_storm": "Respond to solar storm anomaly and protect systems",
            "micrometeoroid": "Handle micrometeoroid impact damage assessment",
            "sensor_spoof": "Detect and mitigate sensor spoofing attack"
        }
        
        goal = scenario_goals.get(scenario, "Process system anomaly")
        
        # Process through MVTS with EDI context
        mvts_result = await mvts_core.process_goal(goal, {
            "scenario": scenario,
            "edi_outputs": edi_result,
            "sensor_data_shape": X.shape,
            "duration": duration
        })
        
        return {
            "scenario": scenario,
            "duration": duration,
            "edi_outputs": edi_result,
            "mvts_result": mvts_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in integrated simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mvts-edi/loops")
async def get_cognitive_loops():
    """Get recent cognitive loops"""
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
                "timestamp": loop.start_time
            }
            for loop in mvts_core.loop_history[-5:]  # Last 5 loops
        ]
    }

# Enhanced MVTS Core with EDI Integration
class EDIEnhancedMVTSCore(MVTSCore):
    """MVTS Core enhanced with EDI integration"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.edi_integration = config.get("edi_integration") if config else None
    
    async def execute_plan_phase(self, goal: str, context: Dict[str, Any]) -> CognitivePhase:
        """Enhanced planning phase with EDI awareness"""
        phase_id = f"plan_{datetime.now().timestamp()}"
        start_time = datetime.now().isoformat()
        
        try:
            # Get EDI context if available
            edi_context = context.get("edi_outputs", {})
            cognitive_load = context.get("cognitive_load", 0)
            
            # Adjust planning based on EDI inputs
            base_plan = await self.planner.create_plan(goal, context)
            
            # Enhance plan with EDI insights
            if edi_context:
                base_plan["edi_enhanced"] = True
                base_plan["risk_considerations"] = edi_context.get("risk_assessment", {})
                base_plan["coherence_adjustment"] = edi_context.get("coherence", 0.8)
                base_plan["adaptive_planning"] = cognitive_load > 0.5
            
            return CognitivePhase(
                phase_id=phase_id,
                phase_type="plan",
                start_time=start_time,
                end_time=datetime.now().isoformat(),
                success=True,
                output=base_plan
            )
        except Exception as e:
            return CognitivePhase(
                phase_id=phase_id,
                phase_type="plan",
                start_time=start_time,
                end_time=datetime.now().isoformat(),
                success=False,
                output={"error": str(e)}
            )

# Override MVTS core with enhanced version
async def create_mvts_edi_core(config: Dict[str, Any] = None) -> EDIEnhancedMVTSCore:
    """Create EDI-enhanced MVTS core"""
    return EDIEnhancedMVTSCore(config)

if __name__ == "__main__":
    import uvicorn
    print("Starting MVTS-EDI Integrated Server...")
    print("Access at: http://localhost:8002")
    print("Health check: http://localhost:8002/health")
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
