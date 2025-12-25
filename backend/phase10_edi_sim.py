"""
Phase 10 Simulation with EDI Integration
Combines DAX governance with Extended Detection & Integration for real-time anomaly detection and adaptive control
"""

import numpy as np
import matplotlib.pyplot as plt
import asyncio
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import sys
import os

# Add backend path for imports
sys.path.append(os.path.dirname(__file__))
from edi import DAXEDIIntegration, simulate_scenario

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SimulationState:
    """Current simulation state"""
    time: float
    scenario: str
    sensors: np.ndarray
    residuals: np.ndarray
    edi_outputs: Dict
    dax_knobs: Dict
    risk_level: str
    system_health: str
    governance_bias: Dict

@dataclass
class SimulationConfig:
    """Simulation configuration"""
    fs: int = 200  # Sampling frequency (Hz)
    duration: float = 30.0  # Simulation duration (seconds)
    window_size: float = 2.0  # EDI analysis window (seconds)
    scenarios: List[str] = None
    
    def __post_init__(self):
        if self.scenarios is None:
            self.scenarios = ["solar_storm", "micrometeoroid", "sensor_spoof"]

class Phase10EDISimulator:
    """
    Phase 10 simulation with EDI integration for DAX governance system
    """
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.edi_integration = DAXEDIIntegration(
            fs=config.fs, 
            window_s=config.window_size
        )
        
        # Simulation state
        self.current_time = 0.0
        self.current_scenario = config.scenarios[0]
        self.state_history: List[SimulationState] = []
        
        # Data buffers
        self.sensor_buffer = []
        self.residual_buffer = []
        self.max_buffer_size = int(config.fs * config.window_size * 2)
        
        logger.info(f"Phase10 EDI Simulator initialized: {config.duration}s, {config.fs}Hz")
    
    def _generate_scenario_data(self, scenario: str, duration: float):
        """Generate sensor data for specific scenario"""
        t, X, R = simulate_scenario(
            fs=self.config.fs,
            T_s=duration,
            scenario=scenario,
            K=4,
            seed=int(hash(scenario) % 1000)
        )
        return t, X, R
    
    def _update_buffers(self, sensors: np.ndarray, residuals: np.ndarray):
        """Update sensor and residual buffers"""
        # Add new data
        for i in range(len(sensors)):
            self.sensor_buffer.append(sensors[i])
            self.residual_buffer.append(residuals[i])
        
        # Maintain buffer size
        while len(self.sensor_buffer) > self.max_buffer_size:
            self.sensor_buffer.pop(0)
            self.residual_buffer.pop(0)
    
    def step(self, dt: float = 0.1) -> SimulationState:
        """
        Advance simulation by one time step
        
        Args:
            dt: time step in seconds
            
        Returns:
            Current simulation state
        """
        self.current_time += dt
        
        # Generate scenario data for current time window
        t_window, X_window, R_window = self._generate_scenario_data(
            self.current_scenario, 
            dt
        )
        
        # Update buffers
        self._update_buffers(X_window, R_window)
        
        # Process through EDI if we have enough data
        if len(self.sensor_buffer) >= int(self.config.fs * self.config.window_size):
            sensor_array = np.array(self.sensor_buffer)
            residual_array = np.array(self.residual_buffer)
            
            # Process through EDI integration
            edi_result = self.edi_integration.process_sensor_data(
                sensor_array, 
                residual_array
            )
            
            # Get governance bias for DAX
            governance_bias = self.edi_integration.get_governance_bias()
            
            # Create state
            state = SimulationState(
                time=self.current_time,
                scenario=self.current_scenario,
                sensors=sensor_array[-1],  # Latest sensor reading
                residuals=residual_array[-1],  # Latest residual
                edi_outputs=edi_result,
                dax_knobs=edi_result['knobs'],
                risk_level=edi_result['risk_assessment']['level'],
                system_health=edi_result['system_health']['status'],
                governance_bias=governance_bias
            )
        else:
            # Initial state before EDI processing
            state = SimulationState(
                time=self.current_time,
                scenario=self.current_scenario,
                sensors=np.zeros(4),
                residuals=np.zeros(4),
                edi_outputs={},
                dax_knobs=self.edi_integration.planner.knobs,
                risk_level="initializing",
                system_health="initializing",
                governance_bias={}
            )
        
        self.state_history.append(state)
        return state
    
    def run_simulation(self, scenario: str = None) -> List[SimulationState]:
        """
        Run complete simulation
        
        Args:
            scenario: specific scenario to run, or None for all scenarios
            
        Returns:
            List of simulation states
        """
        if scenario:
            self.current_scenario = scenario
            logger.info(f"Running simulation for scenario: {scenario}")
        else:
            logger.info(f"Running simulation for all scenarios: {self.config.scenarios}")
        
        # Clear history
        self.state_history.clear()
        self.current_time = 0.0
        
        # Run simulation
        steps = int(self.config.duration / 0.1)  # 0.1s time steps
        
        for step in range(steps):
            state = self.step(0.1)
            
            # Log progress
            if step % 100 == 0:
                logger.info(f"Step {step}/{steps}, t={state.time:.1f}s, "
                          f"C={state.edi_outputs.get('coherence', 0):.3f}, "
                          f"Risk={state.risk_level}")
        
        logger.info(f"Simulation complete: {len(self.state_history)} states")
        return self.state_history
    
    def switch_scenario(self, scenario: str):
        """Switch to different scenario"""
        if scenario in self.config.scenarios:
            self.current_scenario = scenario
            logger.info(f"Switched to scenario: {scenario}")
        else:
            logger.error(f"Unknown scenario: {scenario}")
    
    def get_metrics_summary(self) -> Dict:
        """Get summary metrics from simulation"""
        if not self.state_history:
            return {}
        
        # Extract metrics
        coherences = [s.edi_outputs.get('coherence', 0) for s in self.state_history if s.edi_outputs]
        risk_levels = [s.risk_level for s in self.state_history]
        health_levels = [s.system_health for s in self.state_history]
        
        # Calculate statistics
        summary = {
            "total_states": len(self.state_history),
            "duration": self.state_history[-1].time if self.state_history else 0,
            "coherence": {
                "mean": np.mean(coherences) if coherences else 0,
                "min": np.min(coherences) if coherences else 0,
                "max": np.max(coherences) if coherences else 0,
                "std": np.std(coherences) if coherences else 0
            },
            "risk_distribution": {
                level: risk_levels.count(level) for level in set(risk_levels)
            },
            "health_distribution": {
                level: health_levels.count(level) for level in set(health_levels)
            },
            "final_knobs": self.state_history[-1].dax_knobs if self.state_history else {},
            "scenarios_run": list(set([s.scenario for s in self.state_history]))
        }
        
        return summary

class Phase10Visualizer:
    """Visualization for Phase10 EDI simulation"""
    
    @staticmethod
    def plot_simulation_results(states: List[SimulationState], save_path: str = None):
        """
        Plot comprehensive simulation results
        
        Args:
            states: List of simulation states
            save_path: Optional path to save plot
        """
        if not states:
            logger.warning("No states to plot")
            return
        
        # Extract time series data
        times = [s.time for s in states]
        coherences = [s.edi_outputs.get('coherence', 0) for s in states]
        risk_levels = [s.risk_level for s in states]
        
        # Extract knob histories
        focus_hist = [s.dax_knobs.get('focus', 0) for s in states]
        entanglement_hist = [s.dax_knobs.get('entanglement', 0) for s in states]
        interference_hist = [s.dax_knobs.get('interference', 0) for s in states]
        exploration_hist = [s.dax_knobs.get('exploration', 0) for s in states]
        
        # Extract salience data (if available)
        salience_data = []
        if states and states[-1].edi_outputs.get('salience'):
            salience_data = np.array([s.edi_outputs.get('salience', [0,0,0,0]) for s in states])
        
        # Create figure
        fig = plt.figure(figsize=(16, 12))
        
        # 1. Coherence and Risk
        ax1 = plt.subplot(5, 1, 1)
        ax1.plot(times, coherences, 'b-', label='Coherence', linewidth=2)
        ax1.set_ylabel('Coherence')
        ax1.set_ylim(-0.05, 1.05)
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper right')
        
        # Add risk level background
        risk_colors = {'low': 'green', 'moderate': 'yellow', 'high': 'orange', 'critical': 'red'}
        for i, (t, risk) in enumerate(zip(times, risk_levels)):
            if i < len(times) - 1:
                ax1.axvspan(t, times[i+1], alpha=0.2, color=risk_colors.get(risk, 'gray'))
        
        # 2. Salience Map
        if salience_data.size > 0:
            ax2 = plt.subplot(5, 1, 2)
            channel_names = ['thermal', 'vibration', 'EM', 'power']
            for i, name in enumerate(channel_names):
                ax2.plot(times, salience_data[:, i], label=f'S_{name}', linewidth=1.5)
            ax2.set_ylabel('Salience')
            ax2.set_ylim(-0.05, 1.05)
            ax2.grid(True, alpha=0.3)
            ax2.legend(loc='upper right')
        
        # 3. DAX Control Knobs
        ax3 = plt.subplot(5, 1, 3)
        ax3.plot(times, focus_hist, label='focus', linewidth=2)
        ax3.plot(times, entanglement_hist, label='entanglement', linewidth=2)
        ax3.plot(times, interference_hist, label='interference', linewidth=2)
        ax3.plot(times, exploration_hist, label='exploration', linewidth=2)
        ax3.set_ylabel('Knob Values')
        ax3.set_ylim(-0.05, 1.05)
        ax3.grid(True, alpha=0.3)
        ax3.legend(loc='upper right')
        
        # 4. Phase Signature Features
        ax4 = plt.subplot(5, 1, 4)
        entropy_hist = [s.edi_outputs.get('phase_signature', {}).get('entropy_mean', 0) for s in states]
        phase_drift_hist = [s.edi_outputs.get('phase_signature', {}).get('phase_drift_mean', 0) for s in states]
        xcorr_hist = [s.edi_outputs.get('phase_signature', {}).get('xcorr_peak_mean', 0) for s in states]
        
        ax4.plot(times, entropy_hist, label='entropy', linewidth=2)
        ax4.plot(times, phase_drift_hist, label='phase drift', linewidth=2)
        ax4.plot(times, xcorr_hist, label='xcorr peak', linewidth=2)
        ax4.set_ylabel('Phase Features')
        ax4.set_ylim(-0.05, 1.05)
        ax4.grid(True, alpha=0.3)
        ax4.legend(loc='upper right')
        
        # 5. Sensor Data (sample)
        ax5 = plt.subplot(5, 1, 5)
        if states and len(states[0].sensors) > 0:
            sensor_hist = np.array([s.sensors for s in states])
            for i, name in enumerate(channel_names):
                ax5.plot(times, sensor_hist[:, i], label=name, linewidth=1, alpha=0.7)
        ax5.set_ylabel('Sensor Values')
        ax5.set_xlabel('Time (s)')
        ax5.grid(True, alpha=0.3)
        ax5.legend(loc='upper right')
        
        plt.suptitle(f'Phase10 EDI Simulation Results', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to {save_path}")
        
        plt.show()
    
    @staticmethod
    def plot_summary_metrics(summary: Dict, save_path: str = None):
        """Plot summary metrics dashboard"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Coherence statistics
        ax1 = axes[0, 0]
        coherence_stats = summary.get('coherence', {})
        labels = ['Mean', 'Min', 'Max']
        values = [coherence_stats.get('mean', 0), coherence_stats.get('min', 0), coherence_stats.get('max', 0)]
        bars = ax1.bar(labels, values, color=['blue', 'red', 'green'])
        ax1.set_ylabel('Coherence Value')
        ax1.set_title('Coherence Statistics')
        ax1.set_ylim(0, 1)
        
        # Add value labels on bars
        for bar, val in zip(bars, values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                    f'{val:.3f}', ha='center', va='bottom')
        
        # Risk distribution
        ax2 = axes[0, 1]
        risk_dist = summary.get('risk_distribution', {})
        if risk_dist:
            ax2.pie(risk_dist.values(), labels=risk_dist.keys(), autopct='%1.1f%%')
        ax2.set_title('Risk Level Distribution')
        
        # Health distribution  
        ax3 = axes[1, 0]
        health_dist = summary.get('health_distribution', {})
        if health_dist:
            ax3.pie(health_dist.values(), labels=health_dist.keys(), autopct='%1.1f%%')
        ax3.set_title('System Health Distribution')
        
        # Final knobs
        ax4 = axes[1, 1]
        final_knobs = summary.get('final_knobs', {})
        if final_knobs:
            knob_names = list(final_knobs.keys())
            knob_values = list(final_knobs.values())
            bars = ax4.bar(knob_names, knob_values)
            ax4.set_ylabel('Knob Value')
            ax4.set_title('Final Control Knobs')
            ax4.set_ylim(0, 1)
            
            # Add value labels
            for bar, val in zip(bars, knob_values):
                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                        f'{val:.3f}', ha='center', va='bottom')
        
        plt.suptitle('Phase10 EDI Simulation Summary', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Summary plot saved to {save_path}")
        
        plt.show()

def run_phase10_edi_demo(scenario: str = "solar_storm", save_plots: bool = True):
    """
    Run Phase10 EDI demonstration
    
    Args:
        scenario: Scenario to run
        save_plots: Whether to save plots
        
    Returns:
        Simulation results and summary
    """
    # Configure simulation
    config = SimulationConfig(
        fs=200,
        duration=20.0,
        window_size=2.0,
        scenarios=[scenario]
    )
    
    # Create and run simulator
    simulator = Phase10EDISimulator(config)
    states = simulator.run_simulation(scenario)
    
    # Get summary
    summary = simulator.get_metrics_summary()
    
    # Print results
    print(f"\n=== Phase10 EDI Simulation Results ===")
    print(f"Scenario: {scenario}")
    print(f"Duration: {summary['duration']:.1f}s")
    print(f"Total States: {summary['total_states']}")
    print(f"Coherence - Mean: {summary['coherence']['mean']:.3f}, "
          f"Min: {summary['coherence']['min']:.3f}, "
          f"Max: {summary['coherence']['max']:.3f}")
    print(f"Risk Distribution: {summary['risk_distribution']}")
    print(f"Health Distribution: {summary['health_distribution']}")
    print(f"Final Knobs: {summary['final_knobs']}")
    
    # Visualize results
    if save_plots:
        Phase10Visualizer.plot_simulation_results(
            states, 
            save_path=f"phase10_edi_{scenario}_results.png"
        )
        Phase10Visualizer.plot_summary_metrics(
            summary,
            save_path=f"phase10_edi_{scenario}_summary.png"
        )
    else:
        Phase10Visualizer.plot_simulation_results(states)
        Phase10Visualizer.plot_summary_metrics(summary)
    
    return states, summary

def run_all_scenarios_demo():
    """Run all scenarios and compare results"""
    scenarios = ["solar_storm", "micrometeoroid", "sensor_spoof"]
    all_results = {}
    
    for scenario in scenarios:
        print(f"\n{'='*50}")
        print(f"Running scenario: {scenario}")
        print(f"{'='*50}")
        
        states, summary = run_phase10_edi_demo(scenario, save_plots=False)
        all_results[scenario] = {
            'states': states,
            'summary': summary
        }
    
    # Compare scenarios
    print(f"\n{'='*50}")
    print("SCENARIO COMPARISON")
    print(f"{'='*50}")
    
    for scenario, result in all_results.items():
        summary = result['summary']
        print(f"\n{scenario.upper()}:")
        print(f"  Coherence Mean: {summary['coherence']['mean']:.3f}")
        print(f"  Coherence Min: {summary['coherence']['min']:.3f}")
        print(f"  Risk Levels: {summary['risk_distribution']}")
        print(f"  Health Levels: {summary['health_distribution']}")
    
    return all_results

if __name__ == "__main__":
    # Run single scenario demo
    print("Running Phase10 EDI simulation demo...")
    states, summary = run_phase10_edi_demo("solar_storm", save_plots=True)
    
    # Uncomment to run all scenarios comparison
    # print("\nRunning all scenarios comparison...")
    # all_results = run_all_scenarios_demo()
