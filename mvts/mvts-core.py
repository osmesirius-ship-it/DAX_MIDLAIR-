"""
MVTS Core - Minimum Viable Thinking Server (Python Version)
Integrates cognitive modules for persistent learning and closed-loop reasoning
"""

import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import uuid
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BeliefState:
    """System belief state for MVTS"""
    coherence: float = 0.8
    reliability: float = 0.9
    learning_rate: float = 0.1
    confidence: float = 0.7
    last_updated: str = ""

@dataclass
class CognitivePhase:
    """Single phase in cognitive loop"""
    phase_id: str
    phase_type: str  # "plan", "execute", "evaluate", "update"
    start_time: str
    end_time: Optional[str] = None
    success: bool = False
    output: Dict[str, Any] = None
    learning: List[str] = None

@dataclass
class CognitiveLoop:
    """Complete cognitive loop with multiple phases"""
    loop_id: str
    goal: str
    context: Dict[str, Any]
    phases: List[CognitivePhase]
    start_time: str
    end_time: Optional[str] = None
    success: bool = False
    learning: List[str] = None
    
    def __post_init__(self):
        if self.learning is None:
            self.learning = []

class StateStore:
    """Persistent state storage for MVTS"""
    
    def __init__(self, storage_path: str = "./mvts-state.json"):
        self.storage_path = storage_path
        self.state = {
            "beliefs": asdict(BeliefState()),
            "memory": [],
            "rules": [],
            "last_updated": datetime.now().isoformat()
        }
        self.load_state()
    
    def load_state(self):
        """Load state from storage"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    loaded_state = json.load(f)
                    self.state.update(loaded_state)
                logger.info(f"State loaded from {self.storage_path}")
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
    
    def save_state(self):
        """Save state to storage"""
        try:
            self.state["last_updated"] = datetime.now().isoformat()
            with open(self.storage_path, 'w') as f:
                json.dump(self.state, f, indent=2)
            logger.info(f"State saved to {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def get_beliefs(self) -> BeliefState:
        """Get current belief state"""
        beliefs_data = self.state.get("beliefs", {})
        return BeliefState(**beliefs_data)
    
    def update_beliefs(self, beliefs: BeliefState):
        """Update belief state"""
        beliefs.last_updated = datetime.now().isoformat()
        self.state["beliefs"] = asdict(beliefs)
        self.save_state()
    
    def add_memory(self, memory: Dict[str, Any]):
        """Add memory to storage"""
        self.state["memory"].append({
            **memory,
            "timestamp": datetime.now().isoformat()
        })
        self.save_state()
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent memories"""
        memories = self.state.get("memory", [])
        return memories[-limit:] if memories else []

class Planner:
    """Planning module for MVTS"""
    
    def __init__(self, state_store: StateStore, model_client=None):
        self.state_store = state_store
        self.model_client = model_client
    
    async def create_plan(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create execution plan for goal"""
        beliefs = self.state_store.get_beliefs()
        recent_memories = self.state_store.get_recent_memories(5)
        
        # Simulate planning process
        plan = {
            "goal": goal,
            "steps": [
                "Analyze requirements",
                "Design solution", 
                "Implement core functionality",
                "Test and validate",
                "Deploy and monitor"
            ],
            "estimated_confidence": beliefs.confidence,
            "learning_from_history": len(recent_memories) > 0,
            "context_integration": bool(context)
        }
        
        return plan

class OutcomeEvaluator:
    """Outcome evaluation module"""
    
    def __init__(self, state_store: StateStore):
        self.state_store = state_store
    
    async def evaluate_outcome(self, goal: str, plan: Dict[str, Any], execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate outcome of execution"""
        beliefs = self.state_store.get_beliefs()
        
        # Simulate evaluation
        success_score = min(1.0, execution_result.get("success_rate", 0.7))
        learning_potential = 1.0 - success_score  # More learning from failures
        
        evaluation = {
            "success_score": success_score,
            "learning_potential": learning_potential,
            "confidence_adjustment": (success_score - 0.5) * beliefs.learning_rate,
            "identified_patterns": ["pattern_1", "pattern_2"],  # Simulated
            "recommendations": [
                "Improve planning accuracy",
                "Enhance execution monitoring"
            ]
        }
        
        return evaluation

class UpdateRules:
    """Rule-based learning updates"""
    
    def __init__(self, state_store: StateStore):
        self.state_store = state_store
    
    async def apply_learning_rules(self, evaluation: Dict[str, Any]) -> List[str]:
        """Apply learning rules based on evaluation"""
        beliefs = self.state_store.get_beliefs()
        learning_updates = []
        
        # Rule 1: Update confidence based on success
        confidence_adj = evaluation.get("confidence_adjustment", 0)
        new_confidence = max(0.1, min(1.0, beliefs.confidence + confidence_adj))
        beliefs.confidence = new_confidence
        learning_updates.append(f"Updated confidence to {new_confidence:.3f}")
        
        # Rule 2: Update learning rate based on performance
        if evaluation["success_score"] < 0.5:
            beliefs.learning_rate = min(0.3, beliefs.learning_rate * 1.1)
            learning_updates.append("Increased learning rate due to low success")
        elif evaluation["success_score"] > 0.8:
            beliefs.learning_rate = max(0.05, beliefs.learning_rate * 0.9)
            learning_updates.append("Decreased learning rate due to high success")
        
        # Rule 3: Update coherence based on consistency
        new_coherence = beliefs.coherence * 0.9 + evaluation["success_score"] * 0.1
        beliefs.coherence = new_coherence
        learning_updates.append(f"Updated coherence to {new_coherence:.3f}")
        
        # Save updated beliefs
        self.state_store.update_beliefs(beliefs)
        
        return learning_updates

class MVTSCore:
    """Main MVTS cognitive system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize modules
        storage_path = self.config.get("storage_path", "./mvts-state.json")
        self.state_store = StateStore(storage_path)
        self.planner = Planner(self.state_store)
        self.outcome_evaluator = OutcomeEvaluator(self.state_store)
        self.update_rules = UpdateRules(self.state_store)
        
        # System state
        self.active_loops: Dict[str, CognitiveLoop] = {}
        self.loop_history: List[CognitiveLoop] = []
        
        # Auto-apply rules
        if self.config.get("auto_apply_rules", True):
            asyncio.create_task(self.rule_application_loop())
        
        logger.info("MVTS Core initialized")
    
    async def process_goal(self, goal: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process goal through complete cognitive loop"""
        if context is None:
            context = {}
        
        loop_id = f"loop_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now().isoformat()
        
        # Initialize loop
        loop = CognitiveLoop(
            loop_id=loop_id,
            goal=goal,
            context=context,
            phases=[],
            start_time=start_time
        )
        
        self.active_loops[loop_id] = loop
        
        try:
            # Phase 1: Planning
            plan_phase = await self.execute_plan_phase(goal, context)
            loop.phases.append(plan_phase)
            
            # Phase 2: Execution (simulated)
            exec_phase = await self.execute_execution_phase(plan_phase.output)
            loop.phases.append(exec_phase)
            
            # Phase 3: Evaluation
            eval_phase = await self.execute_evaluation_phase(goal, plan_phase.output, exec_phase.output)
            loop.phases.append(eval_phase)
            
            # Phase 4: Learning Update
            update_phase = await self.execute_update_phase(eval_phase.output)
            loop.phases.append(update_phase)
            
            # Complete loop
            loop.end_time = datetime.now().isoformat()
            loop.success = all(phase.success for phase in loop.phases)
            loop.learning = update_phase.output.get("learning_updates", [])
            
            # Move to history
            self.loop_history.append(loop)
            del self.active_loops[loop_id]
            
            # Add to memory
            self.state_store.add_memory({
                "type": "cognitive_loop",
                "loop_id": loop_id,
                "goal": goal,
                "success": loop.success,
                "learning": loop.learning
            })
            
            return self.format_loop_result(loop)
            
        except Exception as e:
            logger.error(f"Error in cognitive loop {loop_id}: {e}")
            loop.success = False
            loop.end_time = datetime.now().isoformat()
            return {"error": str(e), "loop_id": loop_id}
    
    async def execute_plan_phase(self, goal: str, context: Dict[str, Any]) -> CognitivePhase:
        """Execute planning phase"""
        phase_id = f"plan_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now().isoformat()
        
        try:
            plan = await self.planner.create_plan(goal, context)
            
            return CognitivePhase(
                phase_id=phase_id,
                phase_type="plan",
                start_time=start_time,
                end_time=datetime.now().isoformat(),
                success=True,
                output=plan
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
    
    async def execute_execution_phase(self, plan: Dict[str, Any]) -> CognitivePhase:
        """Execute execution phase (simulated)"""
        phase_id = f"exec_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now().isoformat()
        
        try:
            # Simulate execution with some randomness
            import random
            success_rate = 0.7 + random.random() * 0.3  # 70-100% success
            
            execution_result = {
                "plan_executed": True,
                "success_rate": success_rate,
                "completed_steps": plan.get("steps", [])[:3],  # Completed some steps
                "execution_time": "2.5s",
                "resources_used": ["CPU", "Memory", "Network"]
            }
            
            return CognitivePhase(
                phase_id=phase_id,
                phase_type="execute",
                start_time=start_time,
                end_time=datetime.now().isoformat(),
                success=success_rate > 0.6,
                output=execution_result
            )
        except Exception as e:
            return CognitivePhase(
                phase_id=phase_id,
                phase_type="execute",
                start_time=start_time,
                end_time=datetime.now().isoformat(),
                success=False,
                output={"error": str(e)}
            )
    
    async def execute_evaluation_phase(self, goal: str, plan: Dict[str, Any], execution: Dict[str, Any]) -> CognitivePhase:
        """Execute evaluation phase"""
        phase_id = f"eval_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now().isoformat()
        
        try:
            evaluation = await self.outcome_evaluator.evaluate_outcome(goal, plan, execution)
            
            return CognitivePhase(
                phase_id=phase_id,
                phase_type="evaluate",
                start_time=start_time,
                end_time=datetime.now().isoformat(),
                success=True,
                output=evaluation
            )
        except Exception as e:
            return CognitivePhase(
                phase_id=phase_id,
                phase_type="evaluate",
                start_time=start_time,
                end_time=datetime.now().isoformat(),
                success=False,
                output={"error": str(e)}
            )
    
    async def execute_update_phase(self, evaluation: Dict[str, Any]) -> CognitivePhase:
        """Execute learning update phase"""
        phase_id = f"update_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now().isoformat()
        
        try:
            learning_updates = await self.update_rules.apply_learning_rules(evaluation)
            
            return CognitivePhase(
                phase_id=phase_id,
                phase_type="update",
                start_time=start_time,
                end_time=datetime.now().isoformat(),
                success=True,
                output={"learning_updates": learning_updates}
            )
        except Exception as e:
            return CognitivePhase(
                phase_id=phase_id,
                phase_type="update",
                start_time=start_time,
                end_time=datetime.now().isoformat(),
                success=False,
                output={"error": str(e)}
            )
    
    def format_loop_result(self, loop: CognitiveLoop) -> Dict[str, Any]:
        """Format loop result for output"""
        return {
            "loop_id": loop.loop_id,
            "goal": loop.goal,
            "success": loop.success,
            "duration": self.calculate_duration(loop.start_time, loop.end_time),
            "phases_completed": len(loop.phases),
            "learning": loop.learning,
            "final_beliefs": asdict(self.state_store.get_beliefs()),
            "phase_summary": [
                {
                    "type": phase.phase_type,
                    "success": phase.success,
                    "duration": self.calculate_duration(phase.start_time, phase.end_time)
                }
                for phase in loop.phases
            ]
        }
    
    def calculate_duration(self, start_time: str, end_time: str) -> float:
        """Calculate duration between timestamps"""
        if not end_time:
            return 0.0
        
        try:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            return (end - start).total_seconds()
        except:
            return 0.0
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        beliefs = self.state_store.get_beliefs()
        
        return {
            "active_loops": len(self.active_loops),
            "completed_loops": len(self.loop_history),
            "current_beliefs": asdict(beliefs),
            "memory_size": len(self.state_store.state.get("memory", [])),
            "system_uptime": "N/A",  # Could track actual uptime
            "last_activity": self.state_store.state.get("last_updated")
        }
    
    async def rule_application_loop(self):
        """Background loop for rule application"""
        while True:
            try:
                await asyncio.sleep(self.config.get("rule_application_interval", 60))
                # Could add periodic rule applications here
                logger.debug("Rule application loop tick")
            except Exception as e:
                logger.error(f"Error in rule application loop: {e}")

# Demo function
async def run_mvts_demo():
    """Run MVTS demonstration"""
    mvts = MVTSCore({
        "storage_path": "./demo-mvts-state.json",
        "auto_apply_rules": True,
        "rule_application_interval": 5  # 5 seconds for demo
    })
    
    print("=== MVTS Closed-Loop Learning Demonstration ===\n")
    
    # Demo 1: Initial learning attempt
    print("1. First attempt: Implement user authentication system")
    result1 = await mvts.process_goal({
        "description": "Implement secure user authentication system",
        "priority": "high",
        "type": "implementation"
    })
    
    print("Result:", json.dumps(result1, indent=2))
    print("System status:", json.dumps(mvts.get_system_status(), indent=2))
    
    # Demo 2: Second attempt with learning
    print("\n2. Second attempt: Same goal (should learn from first attempt)")
    result2 = await mvts.process_goal({
        "description": "Implement secure user authentication system", 
        "priority": "high",
        "type": "implementation"
    })
    
    print("Result:", json.dumps(result2, indent=2))
    print("Final system status:", json.dumps(mvts.get_system_status(), indent=2))

if __name__ == "__main__":
    asyncio.run(run_mvts_demo())
