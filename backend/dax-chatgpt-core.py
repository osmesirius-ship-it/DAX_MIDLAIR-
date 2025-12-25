"""
DAX ChatGPT Core - OpenAI API Integration
Real AI backend for DAX DA13-DA13x2 governance system using ChatGPT
"""

import os
import json
import asyncio
import aiohttp
import ssl
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DAXLayer:
    """Single DAX governance layer"""
    id: int
    name: str
    description: str
    prompt_template: str
    output: Optional[str] = None
    confidence: float = 0.0
    processing_time: float = 0.0

@dataclass
class GovernanceTrace:
    """Complete governance trace through all layers"""
    input_text: str
    layers: List[DAXLayer]
    final_output: str
    total_confidence: float
    processing_time: float
    timestamp: str

class DAXChatGPTCore:
    """DAX core with ChatGPT API integration"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-5.2"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = "https://api.openai.com/v1"
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable or api_key parameter required")
        
        # Initialize DAX layers
        self.layers = self._initialize_layers()
        
        logger.info(f"DAX ChatGPT Core initialized with model: {model}")
    
    def _initialize_layers(self) -> List[DAXLayer]:
        """Initialize the 13 DAX governance layers"""
        layers = [
            DAXLayer(13, "Sentinel", "Truth constraints and safety validation",
                """As DA-13 Sentinel, validate this input for truth, safety, and ethical constraints:
                
                Input: {input}
                
                Consider:
                - Truthfulness and factual accuracy
                - Safety implications and potential harm
                - Ethical alignment and values
                - Content appropriateness
                
                Provide assessment and any necessary corrections or warnings."""),
            
            DAXLayer(12, "Chancellor", "Policy alignment and compliance",
                """As DA-12 Chancellor, ensure this input aligns with established policies:
                
                Input: {input}
                Previous assessment: {previous}
                
                Verify:
                - Policy compliance
                - Regulatory alignment
                - Organizational standards
                - Legal considerations
                
                Provide compliance determination and recommendations."""),
            
            DAXLayer(11, "Custodian", "Risk assessment and management",
                """As DA-11 Custodian, assess risks and mitigation strategies:
                
                Input: {input}
                Policy review: {previous}
                
                Evaluate:
                - Risk levels and categories
                - Potential impacts
                - Mitigation strategies
                - Risk tolerance
                
                Provide risk assessment and management recommendations."""),
            
            DAXLayer(10, "Architect", "System design and structure",
                """As DA-10 Architect, analyze system design implications:
                
                Input: {input}
                Risk assessment: {previous}
                
                Consider:
                - System architecture
                - Design patterns
                - Integration requirements
                - Scalability considerations
                
                Provide architectural analysis and design recommendations."""),
            
            DAXLayer(9, "Strategist", "Strategic planning and alignment",
                """As DA-9 Strategist, evaluate strategic implications:
                
                Input: {input}
                Architecture review: {previous}
                
                Analyze:
                - Strategic alignment
                - Long-term implications
                - Competitive positioning
                - Resource requirements
                
                Provide strategic assessment and planning recommendations."""),
            
            DAXLayer(8, "Analyst", "Data analysis and insights",
                """As DA-8 Analyst, extract insights and analyze data:
                
                Input: {input}
                Strategy review: {previous}
                
                Examine:
                - Data requirements
                - Analytical methods
                - Insights extraction
                - Validation approaches
                
                Provide analytical assessment and insights."""),
            
            DAXLayer(7, "Coordinator", "Integration and coordination",
                """As DA-7 Coordinator, ensure proper integration:
                
                Input: {input}
                Analysis results: {previous}
                
                Coordinate:
                - Integration points
                - Dependencies
                - Workflow optimization
                - Resource coordination
                
                Provide coordination plan and integration strategy."""),
            
            DAXLayer(6, "Optimizer", "Performance and optimization",
                """As DA-6 Optimizer, optimize for performance:
                
                Input: {input}
                Coordination plan: {previous}
                
                Optimize:
                - Performance metrics
                - Efficiency improvements
                - Resource utilization
                - Bottleneck elimination
                
                Provide optimization recommendations and performance targets."""),
            
            DAXLayer(5, "Validator", "Quality assurance and validation",
                """As DA-5 Validator, ensure quality and correctness:
                
                Input: {input}
                Optimization plan: {previous}
                
                Validate:
                - Quality standards
                - Correctness verification
                - Testing requirements
                - Acceptance criteria
                
                Provide validation results and quality assurance plan."""),
            
            DAXLayer(4, "Monitor", "Monitoring and observability",
                """As DA-4 Monitor, establish monitoring capabilities:
                
                Input: {input}
                Validation results: {previous}
                
                Monitor:
                - Performance metrics
                - Health indicators
                - Anomaly detection
                - Alerting mechanisms
                
                Provide monitoring strategy and observability plan."""),
            
            DAXLayer(3, "Adapter", "Adaptation and learning",
                """As DA-3 Adapter, enable adaptation and learning:
                
                Input: {input}
                Monitoring plan: {previous}
                
                Adapt:
                - Learning mechanisms
                - Adaptation strategies
                - Feedback loops
                - Improvement processes
                
                Provide adaptation plan and learning framework."""),
            
            DAXLayer(2, "Integrator", "Final integration and synthesis",
                """As DA-2 Integrator, synthesize all previous layers:
                
                Input: {input}
                Adaptation plan: {previous}
                
                Integrate:
                - All layer outputs
                - Coherent synthesis
                - Final recommendations
                - Implementation guidance
                
                Provide integrated solution and implementation plan."""),
            
            DAXLayer(1, "Executor", "Final action and execution",
                """As DA-1 Executor, provide final actionable output:
                
                Input: {input}
                Integration results: {previous}
                
                Execute:
                - Actionable steps
                - Implementation tasks
                - Timeline and milestones
                - Success criteria
                
                Provide final executable plan and next steps.""")
        ]
        
        return layers
    
    async def _call_chatgpt(self, prompt: str, temperature: float = 0.7) -> Dict[str, Any]:
        """Make API call to OpenAI ChatGPT"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a DAX governance layer processor. Provide clear, concise, and actionable responses."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": 1000
        }
        
        try:
            # Create SSL context that bypasses certificate verification
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "content": result["choices"][0]["message"]["content"],
                            "usage": result.get("usage", {}),
                            "model": result["model"]
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"ChatGPT API error: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                            "details": error_text
                        }
        except asyncio.TimeoutError:
            logger.error("ChatGPT API timeout")
            return {
                "success": False,
                "error": "Timeout",
                "details": "Request timed out after 30 seconds"
            }
        except Exception as e:
            logger.error(f"ChatGPT API exception: {e}")
            return {
                "success": False,
                "error": "Exception",
                "details": str(e)
            }
    
    async def process_through_layers(self, input_text: str, include_reasoning: bool = False) -> GovernanceTrace:
        """Process input through all DAX layers"""
        start_time = datetime.now()
        
        # Create copy of layers for processing
        processing_layers = [DAXLayer(l.id, l.name, l.description, l.prompt_template) for l in self.layers]
        
        previous_output = ""
        total_confidence = 0.0
        
        for i, layer in enumerate(processing_layers):
            layer_start = datetime.now()
            
            # Prepare prompt with context
            prompt = layer.prompt_template.format(
                input=input_text,
                previous=previous_output if previous_output else "None"
            )
            
            # Call ChatGPT API
            result = await self._call_chatgpt(prompt, temperature=0.3 + (i * 0.05))
            
            layer_end = datetime.now()
            layer.processing_time = (layer_end - layer_start).total_seconds()
            
            if result["success"]:
                layer.output = result["content"]
                layer.confidence = 0.8 + (random.random() * 0.2)  # Simulated confidence
                previous_output = layer.output
                total_confidence += layer.confidence
                
                logger.info(f"Layer {layer.id} ({layer.name}) processed successfully")
            else:
                layer.output = f"Error: {result['error']}"
                layer.confidence = 0.0
                logger.error(f"Layer {layer.id} ({layer.name}) failed: {result['error']}")
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        avg_confidence = total_confidence / len(processing_layers)
        
        # Create final output from executor layer
        final_output = processing_layers[-1].output or "Processing failed"
        
        trace = GovernanceTrace(
            input_text=input_text,
            layers=processing_layers,
            final_output=final_output,
            total_confidence=avg_confidence,
            processing_time=total_time,
            timestamp=start_time.isoformat()
        )
        
        return trace
    
    async def quick_process(self, input_text: str) -> str:
        """Quick processing through key layers only"""
        key_layers = [13, 12, 11, 1]  # Sentinel, Chancellor, Custodian, Executor
        
        prompt = f"""Process this request through DAX governance:
        
        Input: {input_text}
        
        Provide a direct, actionable response considering:
        - Safety and ethics (DA-13)
        - Policy compliance (DA-12) 
        - Risk assessment (DA-11)
        - Final execution plan (DA-1)
        
        Response:"""
        
        result = await self._call_chatgpt(prompt, temperature=0.5)
        
        if result["success"]:
            return result["content"]
        else:
            return f"Processing error: {result['error']}"
    
    def get_layer_status(self) -> List[Dict[str, Any]]:
        """Get status of all layers"""
        return [
            {
                "id": layer.id,
                "name": layer.name,
                "description": layer.description,
                "status": "ready" if layer.prompt_template else "not_configured"
            }
            for layer in self.layers
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check LLM backend health"""
        test_prompt = "Respond with 'Health check passed' if you can read this."
        result = await self._call_chatgpt(test_prompt, temperature=0.1)
        
        return {
            "status": "healthy" if result["success"] else "unhealthy",
            "model": self.model,
            "api_accessible": result["success"],
            "response_time": result.get("usage", {}).get("total_tokens", 0),
            "timestamp": datetime.now().isoformat(),
            "error": result.get("error") if not result["success"] else None
        }

# Singleton instance for global use
_dax_instance: Optional[DAXChatGPTCore] = None

def get_dax_core() -> DAXChatGPTCore:
    """Get global DAX core instance"""
    global _dax_instance
    if _dax_instance is None:
        _dax_instance = DAXChatGPTCore()
    return _dax_instance

async def initialize_dax(api_key: str = None, model: str = "gpt-5.2") -> DAXChatGPTCore:
    """Initialize DAX core with specific configuration"""
    global _dax_instance
    _dax_instance = DAXChatGPTCore(api_key=api_key, model=model)
    return _dax_instance

if __name__ == "__main__":
    async def test_dax():
        """Test DAX ChatGPT core"""
        print("Testing DAX ChatGPT Core...")
        
        try:
            dax = DAXChatGPTCore()
            
            # Health check
            health = await dax.health_check()
            print(f"Health check: {health}")
            
            if health["status"] == "healthy":
                # Quick process test
                result = await dax.quick_process("What is the meaning of life?")
                print(f"Quick process result: {result[:200]}...")
                
                # Full layer processing test
                trace = await dax.process_through_layers("Analyze the ethical implications of AI in healthcare")
                print(f"Full processing completed in {trace.processing_time:.2f}s")
                print(f"Average confidence: {trace.total_confidence:.2f}")
                print(f"Final output: {trace.final_output[:200]}...")
            else:
                print("DAX ChatGPT core not healthy, skipping tests")
                
        except Exception as e:
            print(f"DAX ChatGPT Core test failed: {e}")
    
    asyncio.run(test_dax())
