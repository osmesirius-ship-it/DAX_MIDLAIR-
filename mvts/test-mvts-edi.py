"""
Simple test to run MVTS with EDI integration
"""

import asyncio
import sys
import os
import json

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'phase10_edi_sim'))

from edi import DAXEDIIntegration
from mvts_core import MVTSCore

async def test_mvts_edi():
    """Test MVTS with EDI integration"""
    print("=== MVTS-EDI Integration Test ===\n")
    
    # Initialize EDI
    edi = DAXEDIIntegration(fs=200, window_s=2.0)
    print("EDI initialized")
    
    # Initialize MVTS
    mvts = MVTSCore({
        "storage_path": "./test-mvts-edi-state.json",
        "auto_apply_rules": True
    })
    print("MVTS initialized")
    
    # Generate test sensor data
    from phase10_edi_sim import simulate_scenario
    t, X, R = simulate_scenario(fs=200, T_s=10, scenario="solar_storm")
    
    print(f"Generated sensor data: {X.shape}")
    
    # Process through EDI
    edi_result = edi.process_sensor_data(X.tolist(), R.tolist())
    print(f"EDI Coherence: {edi_result['coherence']:.3f}")
    print(f"EDI Risk Level: {edi_result['risk_assessment']['level']}")
    
    # Process goal through MVTS with EDI context
    goal = "Respond to solar storm anomaly detected by sensors"
    context = {
        "edi_outputs": edi_result,
        "sensor_anomaly": True,
        "coherence": edi_result['coherence'],
        "risk_level": edi_result['risk_assessment']['level']
    }
    
    print(f"\nProcessing goal: {goal}")
    mvts_result = await mvts.process_goal(goal, context)
    
    print(f"\nMVTS Result:")
    print(f"  Success: {mvts_result['success']}")
    print(f"  Duration: {mvts_result['duration']:.3f}s")
    print(f"  Learning: {mvts_result['learning']}")
    print(f"  Final Confidence: {mvts_result['final_beliefs']['confidence']:.3f}")
    print(f"  Final Coherence: {mvts_result['final_beliefs']['coherence']:.3f}")
    
    # Get system status
    mvts_status = mvts.get_system_status()
    edi_health = edi.edi.get_system_health()
    
    print(f"\nSystem Status:")
    print(f"  MVTS Loops: {mvts_status['completed_loops']}")
    print(f"  EDI Health: {edi_health['status']}")
    print(f"  Memory Size: {mvts_status['memory_size']}")
    
    print("\n=== MVTS-EDI Integration Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_mvts_edi())
