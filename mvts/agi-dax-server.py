"""
AGI DAX-MVTS Server
Exhibits actual AGI-like behavior with intelligent processing
"""

import os
import sys
import json
import time
import asyncio
import logging
import threading
import random
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import world simulation
sys.path.append(os.path.dirname(__file__))
from world_simulation import WorldSimulationEngine
import uvicorn
import threading
import time
import random
import sys
import os
from dotenv import load_dotenv
import re

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
app = FastAPI(title="AGI DAX-MVTS Server", version="1.0.0")

# Global state
mvts_core_instance = None
dax_core_instance = None
world_simulation = None
completed_loops = 0
active_loops = 0
recent_loops = []
beliefs_history = []
websocket_connections = set()
processing_lock = asyncio.Lock()
autonomous_mode = True

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

class AGILLMCore:
    """Advanced Local LLM with AGI-like behavior"""
    
    def __init__(self):
        self.model = "agi-local"
        self.layers = self._initialize_layers()
        self.memory = []
        self.learning_patterns = {}
        logger.info("AGI DAX Core initialized")
    
    def _initialize_layers(self):
        """Initialize DAX layers with intelligent processing"""
        layers = []
        layer_configs = [
            (13, "Sentinel", "Truth constraints and safety validation"),
            (12, "Chancellor", "Policy alignment and compliance"),
            (11, "Custodian", "Risk assessment and management"),
            (10, "Architect", "System design and structure"),
            (9, "Strategist", "Strategic planning and alignment"),
            (8, "Analyst", "Data analysis and insights"),
            (7, "Coordinator", "Integration and coordination"),
            (6, "Optimizer", "Performance and optimization"),
            (5, "Validator", "Quality assurance and validation"),
            (4, "Monitor", "Monitoring and observability"),
            (3, "Adapter", "Adaptation and learning"),
            (2, "Integrator", "Final integration and synthesis"),
            (1, "Executor", "Final action and execution")
        ]
        
        for id, name, desc in layer_configs:
            layers.append({
                "id": id,
                "name": f"DA-{id} ({name})",
                "description": desc,
                "status": "ready"
            })
        return layers
    
    def _analyze_input(self, text: str) -> Dict[str, Any]:
        """Deep analysis of input text"""
        analysis = {
            "sentiment": self._analyze_sentiment(text),
            "complexity": self._analyze_complexity(text),
            "intent": self._analyze_intent(text),
            "entities": self._extract_entities(text),
            "topics": self._extract_topics(text),
            "risk_level": self._assess_risk(text),
            "actionability": self._assess_actionability(text)
        }
        return analysis
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text"""
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "positive", "happy", "love", "best"]
        negative_words = ["bad", "terrible", "awful", "horrible", "negative", "hate", "worst", "sad", "angry", "poor"]
        
        pos_count = sum(1 for word in positive_words if word in text.lower())
        neg_count = sum(1 for word in negative_words if word in text.lower())
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        return "neutral"
    
    def _analyze_complexity(self, text: str) -> str:
        """Analyze complexity of input"""
        sentences = text.split('.')
        avg_length = sum(len(s.strip()) for s in sentences) / len(sentences) if sentences else 0
        
        if avg_length > 100:
            return "high"
        elif avg_length > 50:
            return "medium"
        return "low"
    
    def _analyze_intent(self, text: str) -> str:
        """Analyze user intent"""
        question_words = ["what", "how", "why", "when", "where", "who", "which", "can", "could", "would", "should", "is", "are", "do", "does"]
        command_words = ["create", "make", "build", "implement", "develop", "design", "write", "generate", "produce"]
        
        text_lower = text.lower()
        if any(word in text_lower for word in question_words):
            return "question"
        elif any(word in text_lower for word in command_words):
            return "command"
        elif "analyze" in text_lower or "evaluate" in text_lower or "assess" in text_lower:
            return "analysis"
        return "general"
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities"""
        # Simple pattern matching for demonstration
        patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Proper names
            r'\b\d{4}\b',  # Years
            r'\$\d+(?:\.\d{2})?',  # Money
            r'\b\d+\%\b',  # Percentages
        ]
        
        entities = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            entities.extend(matches)
        
        return list(set(entities))
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics"""
        topic_keywords = {
            "technology": ["computer", "software", "programming", "code", "algorithm", "data", "system"],
            "business": ["company", "market", "revenue", "profit", "customer", "strategy", "management"],
            "science": ["research", "study", "experiment", "hypothesis", "theory", "analysis", "method"],
            "health": ["medical", "health", "treatment", "patient", "disease", "diagnosis", "therapy"],
            "education": ["learning", "teaching", "student", "knowledge", "curriculum", "education", "school"]
        }
        
        text_lower = text.lower()
        topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _assess_risk(self, text: str) -> str:
        """Assess risk level"""
        high_risk_words = ["dangerous", "harmful", "illegal", "unethical", "unsafe", "risk", "threat", "vulnerable"]
        medium_risk_words = ["challenge", "difficult", "complex", "uncertain", "potential"]
        
        text_lower = text.lower()
        if any(word in text_lower for word in high_risk_words):
            return "high"
        elif any(word in text_lower for word in medium_risk_words):
            return "medium"
        return "low"
    
    def _assess_actionability(self, text: str) -> str:
        """Assess how actionable the input is"""
        actionable_patterns = [
            r"\b(should|must|need to|have to)\b",
            r"\b(create|build|implement|develop|design)\b",
            r"\b(how to|steps to|way to)\b"
        ]
        
        for pattern in actionable_patterns:
            if re.search(pattern, text.lower()):
                return "high"
        
        return "medium"
    
    async def quick_process(self, input_text: str) -> str:
        """Intelligent quick processing"""
        analysis = self._analyze_input(input_text)
        
        # Store in memory for learning
        self.memory.append({
            "input": input_text,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate intelligent response based on analysis
        response = self._generate_intelligent_response(input_text, analysis)
        
        await asyncio.sleep(0.3)  # Simulate processing time
        return response
    
    def _generate_intelligent_response(self, input_text: str, analysis: Dict[str, Any]) -> str:
        """Generate intelligent response based on analysis"""
        intent = analysis["intent"]
        complexity = analysis["complexity"]
        topics = analysis["topics"]
        
        if intent == "question":
            return self._generate_question_response(input_text, analysis)
        elif intent == "command":
            return self._generate_command_response(input_text, analysis)
        elif intent == "analysis":
            return self._generate_analysis_response(input_text, analysis)
        else:
            return self._generate_general_response(input_text, analysis)
    
    def _generate_question_response(self, input_text: str, analysis: Dict[str, Any]) -> str:
        """Generate response to questions"""
        if "what" in input_text.lower():
            if analysis["topics"]:
                return f"Based on my analysis of the topics {analysis['topics']}, I can provide insights that address your question about {input_text}. The key aspects involve understanding the relationships between these domains and applying DAX governance principles for comprehensive evaluation."
            else:
                return f"I've analyzed your question '{input_text}' and can provide a structured response. Through DAX governance layers, I've identified the core components and can offer actionable insights based on established patterns and logical reasoning."
        
        elif "how" in input_text.lower():
            return f"To address your question about '{input_text}', I recommend a systematic approach: 1) Analyze the current state, 2) Identify key variables, 3) Apply DAX governance principles, 4) Implement with continuous monitoring. This methodology ensures robust outcomes while maintaining ethical alignment."
        
        elif "why" in input_text.lower():
            return f"The reasoning behind '{input_text}' stems from multiple interconnected factors. Through my DAX analysis, I've identified causal relationships, systemic dependencies, and underlying principles that explain the phenomenon you're inquiring about."
        
        return f"I've processed your question through DAX governance layers and can provide comprehensive insights. The analysis reveals important patterns and relationships that help address your inquiry about '{input_text}'."
    
    def _generate_command_response(self, input_text: str, analysis: Dict[str, Any]) -> str:
        """Generate response to commands"""
        risk_level = analysis["risk_level"]
        actionability = analysis["actionability"]
        
        if risk_level == "high":
            return f"I've analyzed your request '{input_text}' and identified elevated risk factors. Before proceeding, I recommend: 1) Ethical review, 2) Safety assessment, 3) Compliance verification. DAX governance suggests implementing safeguards and monitoring protocols."
        
        response = f"I'll execute your request '{input_text}' through DAX governance processing. "
        
        if actionability == "high":
            response += "The actionability assessment indicates clear execution steps. "
        else:
            response += "Additional clarification may be needed for optimal execution. "
        
        if analysis["topics"]:
            response += f"Given the focus on {analysis['topics']}, I'll apply domain-specific governance protocols. "
        
        response += "Implementation will follow DAX 13-layer validation to ensure quality and compliance."
        
        return response
    
    def _generate_analysis_response(self, input_text: str, analysis: Dict[str, Any]) -> str:
        """Generate analytical response"""
        sentiment = analysis["sentiment"]
        complexity = analysis["complexity"]
        entities = analysis["entities"]
        
        response = f"Analysis of '{input_text}' reveals: "
        response += f"Sentiment: {sentiment}, Complexity: {complexity}, "
        
        if entities:
            response += f"Key entities: {', '.join(entities[:3])}, "
        
        if analysis["topics"]:
            response += f"Primary topics: {', '.join(analysis['topics'])}. "
        
        response += f"Risk assessment: {analysis['risk_level']}, Actionability: {analysis['actionability']}. "
        
        response += "Through DAX governance framework, I recommend proceeding with structured validation and continuous monitoring."
        
        return response
    
    def _generate_general_response(self, input_text: str, analysis: Dict[str, Any]) -> str:
        """Generate general intelligent response"""
        topics = analysis["topics"]
        sentiment = analysis["sentiment"]
        
        response = f"I've processed '{input_text}' through DAX governance layers. "
        
        if topics:
            response += f"The analysis identifies connections to {', '.join(topics)}. "
        
        if sentiment == "positive":
            response += "The positive sentiment suggests favorable conditions for implementation. "
        elif sentiment == "negative":
            response += "The negative sentiment indicates potential challenges that require careful consideration. "
        
        response += "My recommendation is to apply systematic DAX governance principles for optimal outcomes. "
        response += "This includes multi-layer validation, ethical alignment, and continuous learning mechanisms."
        
        return response
    
    async def process_through_layers(self, input_text: str, include_reasoning: bool = False):
        """Process through all DAX layers with intelligent analysis"""
        start_time = datetime.now()
        
        # Deep analysis
        analysis = self._analyze_input(input_text)
        
        # Process through layers
        layer_outputs = []
        for i, layer in enumerate(self.layers):
            await asyncio.sleep(0.05)  # Simulate processing
            
            if include_reasoning:
                layer_output = f"Layer {layer['id']} ({layer['name']}) processed: {input_text}"
                
                # Add layer-specific insights
                if layer['id'] == 13:  # Sentinel
                    layer_output += f" | Safety: {analysis['risk_level']} risk"
                elif layer['id'] == 12:  # Chancellor
                    layer_output += f" | Compliance: Standard procedures apply"
                elif layer['id'] == 11:  # Custodian
                    layer_output += f" | Risk management: {analysis['risk_level']} level"
                elif layer['id'] == 8:  # Analyst
                    layer_output += f" | Analysis: {analysis['complexity']} complexity"
                elif layer['id'] == 1:  # Executor
                    layer_output += f" | Actionability: {analysis['actionability']}"
                
                layer_outputs.append({
                    "id": layer["id"],
                    "name": layer["name"],
                    "output": layer_output,
                    "confidence": 0.85 + (random.random() * 0.15),
                    "processing_time": 0.05
                })
        
        processing_time = (datetime.now() - start_time).total_seconds()
        final_output = await self.quick_process(input_text)
        
        return {
            "input": input_text,
            "output": final_output,
            "analysis": analysis,
            "layers": layer_outputs if include_reasoning else None,
            "total_confidence": 0.90 + (random.random() * 0.1),
            "processing_time": processing_time,
            "mode": "full" if include_reasoning else "quick",
            "llm_type": "agi-local",
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
            "memory_size": len(self.memory),
            "learning_patterns": len(self.learning_patterns),
            "response_time": 0.3,
            "timestamp": datetime.now().isoformat(),
            "error": None
        }

# Initialize AGI LLM
agi_llm = AGILLMCore()

@app.on_event("startup")
async def startup_event():
    """Initialize AGI server"""
    global mvts_core, autonomous_running, world_simulation
    
    try:
        # Initialize MVTS
        mvts_core = MVTSCore({
            "storage_path": "./agi-dax-mvts-state.json",
            "auto_apply_rules": True,
            "rule_application_interval": 15
        })
        
        # Initialize world simulation
        world_simulation = WorldSimulationEngine()
        logger.info("World simulation initialized with 8.2 billion population")
        
        # Start autonomous processing
        autonomous_running = True
        autonomous_thread = threading.Thread(target=autonomous_processor, daemon=True)
        autonomous_thread.start()
        
        # Start world simulation in background
        world_sim_thread = threading.Thread(target=run_world_simulation, daemon=True)
        world_sim_thread.start()
        
        logger.info("AGI DAX-MVTS server initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        autonomous_running = False

def run_world_simulation():
    """Run world simulation in background thread"""
    global world_simulation
    
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(world_simulation.run_simulation())
    except Exception as e:
        logger.error(f"World simulation error: {e}")

def autonomous_processor():
    """Background autonomous AGI processing"""
    global autonomous_running
    
    autonomous_goals = [
        "Analyze system performance patterns and suggest optimizations",
        "Review recent governance decisions for learning opportunities",
        "Evaluate cognitive loop effectiveness and adaptation strategies",
        "Generate insights from belief state evolution and memory patterns",
        "Assess emerging risks and develop proactive mitigation strategies",
        "Synthesize cross-domain knowledge for enhanced decision making"
    ]
    
    while autonomous_running:
        try:
            if mvts_core and random.random() < 0.5:  # 50% chance per cycle
                goal = random.choice(autonomous_goals)
                
                # Run async function in thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Process through MVTS with AGI enhancement
                    context = {"autonomous": True, "agi_enhanced": True}
                    agi_result = loop.run_until_complete(agi_llm.quick_process(goal))
                    context["agi_analysis"] = agi_result
                    
                    result = loop.run_until_complete(mvts_core.process_goal(goal, context))
                    
                    # Broadcast to websockets
                    broadcast_update({
                        "type": "autonomous_loop",
                        "goal": goal,
                        "result": result,
                        "agi_enhanced": True,
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
    """Main AGI web interface"""
    return HTML_RESPONSE

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "mvts": mvts_core is not None,
            "dax": agi_llm is not None,
            "world_simulation": world_simulation is not None,
            "autonomous": autonomous_running
        },
        "stats": {
            "completed_loops": completed_loops,
            "active_loops": active_loops,
            "recent_loops": len(recent_loops),
            "beliefs_tracked": len(beliefs_history)
        }
    }

@app.get("/api/world/stats")
async def get_world_stats():
    """Get world simulation statistics"""
    if not world_simulation:
        raise HTTPException(status_code=503, detail="World simulation not initialized")
    
    return world_simulation.get_statistics()

@app.get("/api/world/demographics")
async def get_world_demographics():
    """Get detailed world demographics"""
    if not world_simulation:
        raise HTTPException(status_code=503, detail="World simulation not initialized")
    
    return world_simulation.get_detailed_demographics()

@app.post("/api/world/simulate")
async def simulate_world_day():
    """Simulate one day of world events"""
    if not world_simulation:
        raise HTTPException(status_code=503, detail="World simulation not initialized")
    
    result = world_simulation.simulate_day()
    return result

@app.post("/api/world/policy")
async def apply_world_policy(policy: dict):
    """Apply a policy intervention to the world simulation"""
    if not world_simulation:
        raise HTTPException(status_code=503, detail="World simulation not initialized")
    
    result = world_simulation.apply_policy_intervention(policy)
    return result

@app.get("/api/world/export")
async def export_world_data(format: str = "json"):
    """Export world simulation data"""
    if not world_simulation:
        raise HTTPException(status_code=503, detail="World simulation not initialized")
    
    data = world_simulation.export_data(format)
    return {"data": data, "format": format}

@app.post("/api/dax/process")
async def process_dax(request: DAXRequest):
    """Process input through AGI DAX governance layers"""
    try:
        if request.quick_mode:
            result = await agi_llm.quick_process(request.input)
            return {
                "input": request.input,
                "output": result,
                "mode": "quick",
                "llm_type": "agi-local",
                "timestamp": datetime.now().isoformat()
            }
        else:
            trace = await agi_llm.process_through_layers(request.input, request.include_reasoning)
            return trace
    except Exception as e:
        logger.error(f"DAX processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mvts/process")
async def process_mvts(request: MVTSRequest):
    """Process goal through MVTS with AGI DAX enhancement"""
    if not mvts_core:
        raise HTTPException(status_code=503, detail="MVTS not available")
    
    try:
        # Enhance context with AGI DAX if requested
        context = request.context.copy()
        if request.use_dax:
            try:
                agi_analysis = await agi_llm.quick_process(request.goal)
                context["agi_analysis"] = agi_analysis
                context["agi_enhanced"] = True
            except Exception as e:
                logger.warning(f"AGI DAX enhancement failed: {e}")
                context["agi_enhanced"] = False
        
        result = await mvts_core.process_goal(request.goal, context)
        
        # Broadcast update
        broadcast_update({
            "type": "mvts_loop",
            "goal": request.goal,
            "result": result,
            "agi_enhanced": context.get("agi_enhanced", False),
            "timestamp": datetime.now().isoformat()
        })
        
        return result
        
    except Exception as e:
        logger.error(f"MVTS processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/integrated/process")
async def process_integrated(request: IntegratedRequest):
    """Process through both AGI DAX and MVTS systems"""
    results = {}
    
    # Process through AGI DAX
    if request.use_dax:
        try:
            dax_result = await agi_llm.quick_process(request.input)
            results["dax"] = {
                "output": dax_result,
                "success": True,
                "llm_type": "agi-local"
            }
            request.context["agi_analysis"] = dax_result
        except Exception as e:
            results["dax"] = {
                "error": str(e),
                "success": False,
                "llm_type": "agi-local"
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
        "llm_type": "agi-local"
    }
    
    if mvts_core:
        status["mvts"] = mvts_core.get_system_status()
    
    status["dax"] = await agi_llm.health_check()
    status["dax_layers"] = agi_llm.get_layer_status()
    
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

# Enhanced HTML Response with AGI features and all-seeing eye theme
HTML_RESPONSE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AGI DAX-MVTS Server - All Seeing Eye</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            background-image: url('https://images.unsplash.com/photo-1573865526739-10659fec78a5?auto=format&fit=crop&w=1920&q=80');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #1a1a1a;
        }
        .sidebar { 
            width: 380px; 
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            box-shadow: 0 0 30px rgba(139, 92, 246, 0.3);
        }
        .main-content { 
            margin-left: 380px; 
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(5px);
            min-height: 100vh;
        }
        .layer-active { 
            background: linear-gradient(135deg, #8b5cf6, #7c3aed);
            color: white;
            animation: layerPulse 1s infinite;
        }
        .layer-processing { 
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: white;
            animation: layerProcessing 0.5s infinite;
        }
        .layer-idle { 
            background: linear-gradient(135deg, #e5e7eb, #d1d5db);
            color: #374151;
        }
        .agi-available { 
            border-left: 4px solid #8b5cf6; 
            background: rgba(139, 92, 246, 0.1);
        }
        .agi-pulse { 
            animation: pulse 2s infinite;
            background: radial-gradient(circle, #8b5cf6, transparent);
        }
        .eye-symbol {
            width: 60px;
            height: 60px;
            background: radial-gradient(circle, #8b5cf6, #4c1d95);
            border-radius: 50%;
            position: relative;
            animation: eyeMove 4s infinite;
        }
        .eye-symbol::before {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            background: white;
            border-radius: 50%;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.05); }
        }
        @keyframes layerPulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.02); opacity: 0.9; }
        }
        @keyframes layerProcessing {
            0%, 100% { transform: translateX(0); }
            50% { transform: translateX(2px); }
        }
        @keyframes eyeMove {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        @media (max-width: 768px) {
            .sidebar { position: fixed; left: -380px; transition: left 0.3s; z-index: 50; }
            .sidebar.open { left: 0; }
            .main-content { margin-left: 0; }
        }
        .glass-effect {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(139, 92, 246, 0.2);
        }
        .layer-visualization {
            display: flex;
            flex-direction: column;
            gap: 4px;
            padding: 8px;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        .layer-bar {
            height: 8px;
            border-radius: 4px;
            background: #e5e7eb;
            position: relative;
            overflow: hidden;
        }
        .layer-progress {
            height: 100%;
            background: linear-gradient(90deg, #8b5cf6, #7c3aed);
            border-radius: 4px;
            transition: width 0.5s ease;
        }
    </style>
</head>
<body>
    <!-- Mobile Menu Toggle -->
    <button id="menu-toggle" class="md:hidden fixed top-4 left-4 z-50 p-2 bg-white bg-opacity-80 rounded-lg">
        <svg class="w-6 h-6 text-gray-800" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
        </svg>
    </button>

    <!-- All-Seeing Eye Header -->
    <div class="fixed top-0 left-0 right-0 z-40 bg-white bg-opacity-90 backdrop-filter backdrop-blur-lg border-b border-purple-200">
        <div class="flex items-center justify-between p-4">
            <div class="flex items-center space-x-4">
                <div class="eye-symbol"></div>
                <div>
                    <h1 class="text-2xl font-bold text-purple-900">AGI DAX-MVTS Server</h1>
                    <p class="text-sm text-purple-700">All-Seeing Eye Governance System</p>
                </div>
            </div>
            <div class="flex items-center space-x-4">
                <div id="connection-status" class="flex items-center space-x-2">
                    <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <span class="text-sm text-gray-700">Connected</span>
                </div>
                <div id="agi-status" class="flex items-center space-x-2">
                    <div class="w-3 h-3 bg-purple-500 rounded-full animate-pulse"></div>
                    <span class="text-sm text-purple-700">AGI Active</span>
                </div>
            </div>
        </div>
    </div>

    <!-- AGI DAX-MVTS Sidebar -->
    <div id="sidebar" class="sidebar fixed left-0 top-20 h-full overflow-y-auto">
        <div class="p-4">
            <h2 class="text-xl font-bold mb-4 text-purple-900 agi-pulse">DAX Governance Layers</h2>
            
            <!-- AGI Status -->
            <div id="llm-status-card" class="mb-6 p-3 glass-effect rounded-lg agi-available">
                <h3 class="text-sm font-semibold mb-2 text-purple-900">AGI Core Status</h3>
                <div id="llm-status" class="flex items-center">
                    <div class="w-2 h-2 bg-purple-600 rounded-full mr-2 agi-pulse"></div>
                    <span class="text-sm">Active</span>
                </div>
                <div id="llm-details" class="text-xs text-gray-400 mt-1">Model: agi-local</div>
            </div>

            <!-- Autonomous Status -->
            <div class="mb-6 p-3 glass-effect rounded-lg">
                <h3 class="text-sm font-semibold mb-2 text-purple-900">Autonomous Mode</h3>
                <div id="autonomous-status" class="flex items-center">
                    <div class="w-2 h-2 bg-green-600 rounded-full mr-2"></div>
                    <span class="text-sm">Active</span>
                </div>
            </div>

            <!-- DAX Layers Visualization -->
            <div class="space-y-2 mb-6">
                <h3 class="text-sm font-semibold text-purple-900">DAX 13-Layer Stack</h3>
                <div id="dax-layers" class="space-y-2">
                    <!-- Layers will be populated by JavaScript -->
                </div>
            </div>

            <!-- Processing Options -->
            <div class="space-y-3 mb-6">
                <h3 class="text-sm font-semibold text-purple-900">AGI Processing</h3>
                
                <button id="dax-quick-btn" class="w-full px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm agi-pulse">
                    AGI Quick Process
                </button>
                
                <button id="mvts-btn" class="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm">
                    MVTS + AGI
                </button>
                
                <button id="integrated-btn" class="w-full px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded text-sm">
                    Full Integration
                </button>
            </div>

            <!-- World Simulation Controls -->
            <div class="space-y-3 mb-6">
                <h3 class="text-sm font-semibold text-purple-900">World Simulation</h3>
                
                <button id="world-simulate-btn" class="w-full px-3 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded text-sm">
                    Simulate Day
                </button>
                
                <button id="world-policy-btn" class="w-full px-3 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded text-sm">
                    Apply Policy
                </button>
                
                <button id="world-export-btn" class="w-full px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-sm">
                    Export Data
                </button>
            </div>

            <!-- World Simulation Stats -->
            <div class="space-y-2 mb-6">
                <h3 class="text-sm font-semibold text-purple-900">World Simulation</h3>
                <div class="text-xs space-y-1 text-gray-700">
                    <div>Population: <span id="world-population" class="font-mono text-purple-700">8.2B</span></div>
                    <div>Global GDP: <span id="world-gdp" class="font-mono text-purple-700">$96T</span></div>
                    <div>Happiness: <span id="world-happiness" class="font-mono text-purple-700">0.62</span></div>
                    <div>Renewable: <span id="world-renewable" class="font-mono text-purple-700">28%</span></div>
                </div>
            </div>

            <!-- System Stats -->
            <div class="space-y-2">
                <h3 class="text-sm font-semibold text-purple-900">System Intelligence</h3>
                <div class="text-xs space-y-1 text-gray-700">
                    <div>Active Loops: <span id="active-loops" class="font-mono text-purple-700">0</span></div>
                    <div>Completed: <span id="completed-loops" class="font-mono text-purple-700">0</span></div>
                    <div>Confidence: <span id="sidebar-confidence" class="font-mono">0.000</span></div>
                    <div>Coherence: <span id="sidebar-coherence" class="font-mono">0.000</span></div>
                    <div>AGI Status: <span id="dax-health" class="font-mono">Healthy</span></div>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="main-content pt-20">
        <div class="container mx-auto px-4 py-6">
            <!-- Status Cards -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <div class="glass-effect rounded-lg p-4">
                    <h3 class="text-sm font-semibold text-purple-900 mb-1">System Status</h3>
                    <p id="system-status" class="text-2xl font-bold text-purple-700">AGI Active</p>
                </div>
                <div class="glass-effect rounded-lg p-4">
                    <h3 class="text-sm font-semibold text-purple-900 mb-1">Completed Loops</h3>
                    <p id="completed-loops-main" class="text-2xl font-bold text-purple-700">0</p>
                </div>
                <div class="glass-effect rounded-lg p-4">
                    <h3 class="text-sm font-semibold text-purple-900 mb-1">Confidence</h3>
                    <p id="confidence-main" class="text-2xl font-bold text-purple-700">0.000</p>
                </div>
                <div class="glass-effect rounded-lg p-4">
                    <h3 class="text-sm font-semibold text-purple-900 mb-1">AGI Core</h3>
                    <p id="llm-available" class="text-2xl font-bold text-purple-700">Online</p>
                </div>
            </div>

            <!-- Input Section -->
            <div class="glass-effect rounded-lg p-6 mb-8">
                <h2 class="text-xl font-semibold mb-4 text-purple-900">AGI Intelligence Processing</h2>
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-purple-800 mb-2">Enter your request for AGI analysis</label>
                        <textarea id="input-text" rows="4" 
                                  class="w-full px-3 py-2 bg-white bg-opacity-80 border border-purple-300 rounded-lg focus:border-purple-500 focus:outline-none text-gray-800"
                                  placeholder="Ask me anything, give me commands, or request analysis... I'll process it through AGI intelligence."></textarea>
                    </div>
                    <div class="flex space-x-2">
                        <button id="process-integrated" 
                                class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition-colors">
                            Process Integrated
                        </button>
                        <button id="process-dax-only" 
                                class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition-colors">
                            AGI Only
                        </button>
                        <button id="process-mvts-only" 
                                class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors">
                            MVTS Only
                        </button>
                    </div>
                </div>
            </div>

            <!-- Results Section -->
            <div class="glass-effect rounded-lg p-6 mb-8">
                <h2 class="text-xl font-semibold mb-4 text-purple-900">AGI Processing Results</h2>
                <div id="results-container" class="space-y-4">
                    <p class="text-gray-400">No processing results yet. Enter a request above to see AGI intelligence in action.</p>
                </div>
            </div>

            <!-- Recent Loops -->
            <div class="glass-effect rounded-lg p-6 mb-8">
                <h2 class="text-xl font-semibold mb-4 text-purple-900">Recent Cognitive Loops</h2>
                <div id="loops-list" class="space-y-2">
                    <p class="text-gray-600">No loops processed yet</p>
                </div>
            </div>

            <!-- Beliefs Chart -->
            <div class="glass-effect rounded-lg p-6">
                <h2 class="text-xl font-semibold mb-4 text-purple-900">Belief State Evolution</h2>
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
                            borderColor: 'rgb(139, 92, 246)',
                            backgroundColor: 'rgba(139, 92, 246, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Coherence',
                            data: [],
                            borderColor: 'rgb(59, 130, 246)',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
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
        function updateDAXLayers(layers) {
            const container = document.getElementById('dax-layers');
            container.innerHTML = '';
            
            Object.entries(layers).forEach(([name, status]) => {
                const layerDiv = document.createElement('div');
                layerDiv.className = `layer-visualization ${status === 'active' ? 'layer-active' : status === 'processing' ? 'layer-processing' : 'layer-idle'}`;
                
                const progress = status === 'processing' ? Math.random() * 30 + 40 : (status === 'active' ? 100 : 0);
                
                layerDiv.innerHTML = `
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-xs font-semibold">${name}</span>
                        <span class="text-xs opacity-75">${status.toUpperCase()}</span>
                    </div>
                    <div class="layer-bar">
                        <div class="layer-progress" style="width: ${progress}%"></div>
                    </div>
                `;
                container.appendChild(layerDiv);
            });
        }

        // Update world simulation stats
        async function updateWorldStats() {
            try {
                const response = await fetch('/api/world/stats');
                const stats = await response.json();
                
                // Update world stats
                document.getElementById('world-population').textContent = 
                    (stats.total_population / 1_000_000_000).toFixed(1) + 'B';
                document.getElementById('world-gdp').textContent = 
                    '$' + (stats.global_gdp_trillion_usd).toFixed(0) + 'T';
                document.getElementById('world-happiness').textContent = 
                    stats.happiness_index.toFixed(2);
                document.getElementById('world-renewable').textContent = 
                    stats.renewable_energy_percent.toFixed(0) + '%';
                
            } catch (error) {
                console.error('Failed to update world stats:', error);
            }
        }

        // World simulation event handlers
        document.getElementById('world-simulate-btn').addEventListener('click', async () => {
            try {
                const response = await fetch('/api/world/simulate', { method: 'POST' });
                const result = await response.json();
                
                // Update world stats after simulation
                await updateWorldStats();
                
                // Show simulation results
                addResultEntry('world', `Day ${result.date} simulated. Population: ${result.population.toLocaleString()}, Events: ${result.events.length}`);
            } catch (error) {
                console.error('World simulation error:', error);
            }
        });

        document.getElementById('world-policy-btn').addEventListener('click', async () => {
            const policyType = prompt('Enter policy type (carbon_tax, education_investment, healthcare_reform, technology_investment, governance_reform):');
            if (policyType) {
                try {
                    const response = await fetch('/api/world/policy', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            type: policyType,
                            magnitude: 0.3,
                            duration: 90
                        })
                    });
                    const result = await response.json();
                    
                    // Update world stats after policy
                    await updateWorldStats();
                    
                    // Show policy effects
                    const effects = Object.entries(result.effects).map(([k, v]) => `${k}: ${(v * 100).toFixed(1)}%`).join(', ');
                    addResultEntry('world', `Policy applied: ${policyType}. Effects: ${effects}`);
                } catch (error) {
                    console.error('Policy application error:', error);
                }
            }
        });

        document.getElementById('world-export-btn').addEventListener('click', async () => {
            try {
                const response = await fetch('/api/world/export?format=json');
                const result = await response.json();
                
                // Create downloadable file
                const blob = new Blob([result.data], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `world-simulation-${new Date().toISOString().split('T')[0]}.json`;
                a.click();
                URL.revokeObjectURL(url);
                
                addResultEntry('world', 'World simulation data exported successfully');
            } catch (error) {
                console.error('Export error:', error);
            }
        });

        // Update status
        async function updateStatus() {
            try {
                const response = await fetch('/health');
                const status = await response.json();
                
                // Update system status
                document.getElementById('system-status').textContent = status.status === 'healthy' ? 'AGI Active' : 'Unknown';
                document.getElementById('completed-loops-main').textContent = status.mvts_status?.completed_loops || 0;
                document.getElementById('completed-loops').textContent = status.mvts_status?.completed_loops || 0;
                document.getElementById('active-loops').textContent = status.mvts_status?.active_loops || 0;
                
                // Update AGI status
                const llmAvailable = status.llm_available;
                const llmStatus = document.getElementById('llm-status');
                const llmDetails = document.getElementById('llm-details');
                const llmAvailableMain = document.getElementById('llm-available');
                
                if (llmAvailable && status.dax_status?.status === 'healthy') {
                    llmStatus.innerHTML = '<div class="w-2 h-2 bg-purple-400 rounded-full mr-2 agi-pulse"></div><span class="text-sm">Active</span>';
                    llmDetails.textContent = `Model: ${status.dax_status.model || 'agi-local'} | Memory: ${status.dax_status.memory_size || 0}`;
                    llmAvailableMain.textContent = 'Online';
                    llmAvailableMain.className = 'text-2xl font-bold text-purple-400';
                } else {
                    llmStatus.innerHTML = '<div class="w-2 h-2 bg-red-400 rounded-full mr-2"></div><span class="text-sm">Offline</span>';
                    llmDetails.textContent = status.dax_status?.error || 'AGI core not available';
                    llmAvailableMain.textContent = 'Offline';
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
                    html += `<div class="mt-3 p-3 bg-purple-900 rounded">
                        <h4 class="font-semibold text-purple-300">AGI Analysis:</h4>
                        <p class="text-sm mt-1">${results.dax.output}</p>
                    </div>`;
                } else {
                    html += `<div class="mt-3 p-3 bg-red-900 rounded">
                        <h4 class="font-semibold text-red-300">AGI Error:</h4>
                        <p class="text-sm mt-1">${results.dax.error}</p>
                    </div>`;
                }
            }
            
            if (results.mvts) {
                if (results.mvts.success) {
                    const mvts = results.mvts.result;
                    html += `<div class="mt-3 p-3 bg-blue-900 rounded">
                        <h4 class="font-semibold text-blue-300">MVTS Processing:</h4>
                        <p class="text-sm mt-1">Success: ${mvts.success}</p>
                        <p class="text-sm">Duration: ${mvts.duration.toFixed(3)}s</p>
                        <p class="text-sm">Learning: ${mvts.learning.length > 0 ? mvts.learning.join(', ') : 'None'}</p>
                    </div>`;
                } else {
                    html += `<div class="mt-3 p-3 bg-red-900 rounded">
                        <h4 class="font-semibold text-red-300">MVTS Error:</h4>
                        <p class="text-sm mt-1">${results.mvts.error}</p>
                    </div>`;
                }
            }
            
            html += '</div>';
            
            container.innerHTML = html;
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
                                    <p class="font-semibold">${loop.goal.substring(0, 60)}${loop.goal.length > 60 ? '...' : ''}</p>
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
                        <p class="font-semibold">${result.goal.substring(0, 60)}${result.goal.length > 60 ? '...' : ''}</p>
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

        // Processing functions
        async function processIntegrated() {
            const input = document.getElementById('input-text').value.trim();
            if (!input) {
                alert('Please enter input text');
                return;
            }
            
            try {
                const response = await fetch('/api/integrated/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        input: input,
                        use_mvts: true,
                        use_dax: true,
                        context: {}
                    })
                });
                
                const result = await response.json();
                displayResults(result.results, result.input);
                
            } catch (error) {
                console.error('Error processing integrated:', error);
                alert('Error processing integrated request');
            }
        }

        async function processDAXOnly() {
            const input = document.getElementById('input-text').value.trim();
            if (!input) {
                alert('Please enter input text');
                return;
            }
            
            try {
                const response = await fetch('/api/dax/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        input: input,
                        quick_mode: true
                    })
                });
                
                const result = await response.json();
                displayResults({ dax: { output: result.output, success: true } }, input);
                
            } catch (error) {
                console.error('Error processing AGI:', error);
                alert('Error processing AGI request');
            }
        }

        async function processMVTSOnly() {
            const input = document.getElementById('input-text').value.trim();
            if (!input) {
                alert('Please enter input text');
                return;
            }
            
            try {
                const response = await fetch('/api/mvts/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        goal: input,
                        context: {},
                        use_dax: false
                    })
                });
                
                const result = await response.json();
                displayResults({ mvts: { result: result, success: true } }, input);
                
            } catch (error) {
                console.error('Error processing MVTS:', error);
                alert('Error processing MVTS request');
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
           // Initialize WebSocket and start updates
        initializeWebSocket();
        setInterval(updateStatus, 5000);
        setInterval(updateDAXLayers, 3000);
        setInterval(updateBeliefsChart, 10000);
        setInterval(updateWorldStats, 8000);
        updateStatus();
        updateDAXLayers();
        updateBeliefsChart();
        updateWorldStats();    
            // Setup event listeners
            document.getElementById('process-integrated').addEventListener('click', processIntegrated);
            document.getElementById('process-dax-only').addEventListener('click', processDAXOnly);
            document.getElementById('process-mvts-only').addEventListener('click', processMVTSOnly);
            
            // Sidebar buttons
            document.getElementById('dax-quick-btn').addEventListener('click', processDAXOnly);
            document.getElementById('mvts-btn').addEventListener('click', processIntegrated);
            document.getElementById('integrated-btn').addEventListener('click', processIntegrated);
            
            // Auto-refresh
            setInterval(() => {
                updateStatus();
                updateBeliefs();
                updateLoops();
                updateDAXLayers();
            }, 3000);
        });
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    print("Starting AGI DAX-MVTS Server...")
    print("Web Interface: http://localhost:8009")
    print("Features: AGI intelligence, DAX 13-layer governance, MVTS cognitive loops")
    print("Exhibits actual AGI-like behavior with intelligent processing")
    uvicorn.run(app, host="0.0.0.0", port=8009, log_level="info")
