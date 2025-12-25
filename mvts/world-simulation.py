#!/usr/bin/env python3
"""
World Simulation Engine for AGI DAX-MVTS System
Simulates global population dynamics, governance, and resource management
"""

import asyncio
import random
import time
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PopulationSegment:
    """Represents a demographic segment of the world population"""
    count: int
    age_distribution: Dict[str, float]  # age ranges and percentages
    education_levels: Dict[str, float]  # education levels and percentages
    economic_status: Dict[str, float]   # economic brackets and percentages
    geographic_distribution: Dict[str, float]  # regions and percentages
    health_status: Dict[str, float]     # health categories and percentages

@dataclass
class WorldState:
    """Current state of the world simulation"""
    total_population: int
    segments: Dict[str, PopulationSegment]
    global_gdp: float
    carbon_emissions: float
    renewable_energy_percentage: float
    food_production: float
    water_resources: float
    technology_index: float
    governance_index: float
    happiness_index: float
    timestamp: datetime

class WorldSimulationEngine:
    """Advanced world simulation engine with 8.2 billion population"""
    
    def __init__(self, initial_population: int = 8_200_000_000):
        self.initial_population = initial_population
        self.current_state = self._initialize_world()
        self.simulation_speed = 1.0  # 1 second = 1 day in simulation
        self.running = False
        self.event_queue = []
        self.historical_data = []
        
        # Simulation parameters
        self.birth_rate = 0.018  # births per person per year
        self.death_rate = 0.007  # deaths per person per year
        self.gdp_growth_rate = 0.03  # 3% annual growth
        self.technology_growth_rate = 0.05  # 5% annual growth
        
        # Climate and resources
        self.carbon_reduction_rate = 0.02  # annual reduction target
        self.renewable_energy_growth_rate = 0.08  # annual growth
        self.food_production_growth_rate = 0.02  # annual growth
        
    def _initialize_world(self) -> WorldState:
        """Initialize world state with realistic demographic data"""
        
        # Create population segments
        segments = {
            "asia": PopulationSegment(
                count=4_700_000_000,  # ~57% of world population
                age_distribution={
                    "0-14": 0.24, "15-24": 0.15, "25-54": 0.48, 
                    "55-64": 0.08, "65+": 0.05
                },
                education_levels={
                    "no_formal": 0.15, "primary": 0.35, "secondary": 0.35, 
                    "tertiary": 0.15
                },
                economic_status={
                    "low": 0.30, "lower_middle": 0.35, "upper_middle": 0.25, 
                    "high": 0.10
                },
                geographic_distribution={
                    "east_asia": 0.40, "south_asia": 0.35, "southeast_asia": 0.15,
                    "central_asia": 0.05, "west_asia": 0.05
                },
                health_status={
                    "excellent": 0.20, "good": 0.40, "fair": 0.25, 
                    "poor": 0.12, "critical": 0.03
                }
            ),
            "africa": PopulationSegment(
                count=1_400_000_000,  # ~17% of world population
                age_distribution={
                    "0-14": 0.40, "15-24": 0.19, "25-54": 0.33,
                    "55-64": 0.05, "65+": 0.03
                },
                education_levels={
                    "no_formal": 0.30, "primary": 0.45, "secondary": 0.20,
                    "tertiary": 0.05
                },
                economic_status={
                    "low": 0.45, "lower_middle": 0.35, "upper_middle": 0.15,
                    "high": 0.05
                },
                geographic_distribution={
                    "north_africa": 0.15, "west_africa": 0.30, "east_africa": 0.25,
                    "central_africa": 0.20, "southern_africa": 0.10
                },
                health_status={
                    "excellent": 0.10, "good": 0.25, "fair": 0.35,
                    "poor": 0.22, "critical": 0.08
                }
            ),
            "europe": PopulationSegment(
                count=750_000_000,  # ~9% of world population
                age_distribution={
                    "0-14": 0.15, "15-24": 0.11, "25-54": 0.45,
                    "55-64": 0.15, "65+": 0.14
                },
                education_levels={
                    "no_formal": 0.05, "primary": 0.20, "secondary": 0.45,
                    "tertiary": 0.30
                },
                economic_status={
                    "low": 0.10, "lower_middle": 0.20, "upper_middle": 0.35,
                    "high": 0.35
                },
                geographic_distribution={
                    "western_europe": 0.35, "eastern_europe": 0.30,
                    "southern_europe": 0.20, "northern_europe": 0.15
                },
                health_status={
                    "excellent": 0.35, "good": 0.40, "fair": 0.18,
                    "poor": 0.06, "critical": 0.01
                }
            ),
            "americas": PopulationSegment(
                count=1_000_000_000,  # ~12% of world population
                age_distribution={
                    "0-14": 0.20, "15-24": 0.14, "25-54": 0.45,
                    "55-64": 0.12, "65+": 0.09
                },
                education_levels={
                    "no_formal": 0.10, "primary": 0.25, "secondary": 0.40,
                    "tertiary": 0.25
                },
                economic_status={
                    "low": 0.20, "lower_middle": 0.30, "upper_middle": 0.30,
                    "high": 0.20
                },
                geographic_distribution={
                    "north_america": 0.60, "south_america": 0.30,
                    "central_america": 0.07, "caribbean": 0.03
                },
                health_status={
                    "excellent": 0.25, "good": 0.35, "fair": 0.25,
                    "poor": 0.12, "critical": 0.03
                }
            ),
            "oceania": PopulationSegment(
                count=45_000_000,  # ~0.5% of world population
                age_distribution={
                    "0-14": 0.18, "15-24": 0.13, "25-54": 0.44,
                    "55-64": 0.13, "65+": 0.12
                },
                education_levels={
                    "no_formal": 0.08, "primary": 0.22, "secondary": 0.40,
                    "tertiary": 0.30
                },
                economic_status={
                    "low": 0.15, "lower_middle": 0.25, "upper_middle": 0.35,
                    "high": 0.25
                },
                geographic_distribution={
                    "australia": 0.60, "new_zealand": 0.08,
                    "pacific_islands": 0.32
                },
                health_status={
                    "excellent": 0.30, "good": 0.38, "fair": 0.22,
                    "poor": 0.08, "critical": 0.02
                }
            )
        }
        
        return WorldState(
            total_population=initial_population,
            segments=segments,
            global_gdp=96_100_000_000_000,  # ~96 trillion USD
            carbon_emissions=37_000_000_000,  # 37 gigatons CO2
            renewable_energy_percentage=0.28,  # 28% renewable
            food_production=1.0,  # normalized to 1.0 = current production
            water_resources=0.85,  # 85% of sustainable water usage
            technology_index=0.75,  # 75% of theoretical maximum
            governance_index=0.68,  # 68% effective governance
            happiness_index=0.62,  # 62% global happiness
            timestamp=datetime.now()
        )
    
    def simulate_day(self) -> Dict:
        """Simulate one day of world events"""
        
        # Population dynamics
        births = int(self.current_state.total_population * self.birth_rate / 365)
        deaths = int(self.current_state.total_population * self.death_rate / 365)
        
        # Update population
        self.current_state.total_population += births - deaths
        
        # Economic growth
        daily_gdp_growth = self.gdp_growth_rate / 365
        self.current_state.global_gdp *= (1 + daily_gdp_growth)
        
        # Technology advancement
        daily_tech_growth = self.technology_growth_rate / 365
        self.current_state.technology_index *= (1 + daily_tech_growth)
        self.current_state.technology_index = min(self.current_state.technology_index, 1.0)
        
        # Climate and energy transitions
        daily_carbon_reduction = self.carbon_reduction_rate / 365
        self.current_state.carbon_emissions *= (1 - daily_carbon_reduction)
        
        daily_renewable_growth = self.renewable_energy_growth_rate / 365
        self.current_state.renewable_energy_percentage *= (1 + daily_renewable_growth)
        self.current_state.renewable_energy_percentage = min(
            self.current_state.renewable_energy_percentage, 1.0
        )
        
        # Food and water resources
        daily_food_growth = self.food_production_growth_rate / 365
        self.current_state.food_production *= (1 + daily_food_growth)
        
        # Water stress based on population and climate
        water_stress_factor = (self.current_state.total_population / self.initial_population) * 0.99
        self.current_state.water_resources *= water_stress_factor
        
        # Governance improvement (slow, correlated with education and technology)
        governance_growth = (self.current_state.technology_index * 0.001) / 365
        self.current_state.governance_index *= (1 + governance_growth)
        self.current_state.governance_index = min(self.current_state.governance_index, 1.0)
        
        # Happiness calculation (complex formula based on multiple factors)
        base_happiness = 0.5
        economic_factor = min(self.current_state.global_gdp / 100_000_000_000_000, 1.0) * 0.2
        health_factor = (1 - (deaths / max(births + deaths, 1))) * 0.15
        environment_factor = (1 - self.current_state.carbon_emissions / 40_000_000_000) * 0.1
        governance_factor = self.current_state.governance_index * 0.15
        
        self.current_state.happiness_index = (
            base_happiness + economic_factor + health_factor + 
            environment_factor + governance_factor + random.uniform(-0.05, 0.05)
        )
        self.current_state.happiness_index = max(0, min(1, self.current_state.happiness_index))
        
        # Update timestamp
        self.current_state.timestamp += timedelta(days=1)
        
        # Generate random world events
        events = self._generate_events()
        
        # Store historical data
        self.historical_data.append({
            'timestamp': self.current_state.timestamp.isoformat(),
            'population': self.current_state.total_population,
            'gdp': self.current_state.global_gdp,
            'carbon_emissions': self.current_state.carbon_emissions,
            'renewable_energy': self.current_state.renewable_energy_percentage,
            'happiness': self.current_state.happiness_index,
            'events': events
        })
        
        # Keep only last 365 days of history
        if len(self.historical_data) > 365:
            self.historical_data.pop(0)
        
        return {
            'date': self.current_state.timestamp.strftime('%Y-%m-%d'),
            'population': self.current_state.total_population,
            'births': births,
            'deaths': deaths,
            'gdp': self.current_state.global_gdp,
            'carbon_emissions': self.current_state.carbon_emissions,
            'renewable_energy_percentage': self.current_state.renewable_energy_percentage,
            'food_production': self.current_state.food_production,
            'water_resources': self.current_state.water_resources,
            'technology_index': self.current_state.technology_index,
            'governance_index': self.current_state.governance_index,
            'happiness_index': self.current_state.happiness_index,
            'events': events
        }
    
    def _generate_events(self) -> List[Dict]:
        """Generate random world events"""
        events = []
        
        # Probability of major events
        if random.random() < 0.02:  # 2% chance per day
            event_types = [
                ("technological_breakthrough", "New AI advancement announced", 0.1),
                ("climate_event", "Major climate summit agreement", 0.05),
                ("economic_shift", "Global market adjustment", 0.08),
                ("health_crisis", "Regional health alert", 0.03),
                ("political_change", "Major policy reform", 0.06),
                ("natural_disaster", "Natural disaster response", 0.02)
            ]
            
            event_type, description, impact = random.choice(event_types)
            
            events.append({
                'type': event_type,
                'description': description,
                'impact': impact,
                'affected_regions': random.sample(list(self.current_state.segments.keys()), 
                                                random.randint(1, 3))
            })
            
            # Apply event impacts
            if event_type == "technological_breakthrough":
                self.current_state.technology_index *= (1 + impact)
            elif event_type == "climate_event":
                self.current_state.carbon_emissions *= (1 - impact)
                self.current_state.renewable_energy_percentage *= (1 + impact)
            elif event_type == "economic_shift":
                self.current_state.global_gdp *= (1 + random.uniform(-impact, impact))
            elif event_type == "health_crisis":
                self.death_rate *= (1 + impact * 0.5)
            elif event_type == "political_change":
                self.current_state.governance_index *= (1 + impact * 0.3)
        
        return events
    
    def get_statistics(self) -> Dict:
        """Get comprehensive world statistics"""
        
        # Calculate population by continent
        continent_pop = {
            name: segment.count for name, segment in self.current_state.segments.items()
        }
        
        # Calculate global metrics
        population_growth_rate = (self.birth_rate - self.death_rate) * 100
        
        # Project future population (simple projection)
        future_population = self.current_state.total_population * (
            1 + (self.birth_rate - self.death_rate) * 10  # 10 year projection
        )
        
        return {
            'current_date': self.current_state.timestamp.strftime('%Y-%m-%d'),
            'total_population': self.current_state.total_population,
            'population_growth_rate_percent': population_growth_rate,
            'continent_distribution': continent_pop,
            'global_gdp_trillion_usd': self.current_state.global_gdp / 1_000_000_000_000,
            'carbon_emissions_gigatons': self.current_state.carbon_emissions / 1_000_000_000,
            'renewable_energy_percent': self.current_state.renewable_energy_percentage * 100,
            'technology_index': self.current_state.technology_index,
            'governance_index': self.current_state.governance_index,
            'happiness_index': self.current_state.happiness_index,
            'water_resources_percent': self.current_state.water_resources * 100,
            'food_production_index': self.current_state.food_production,
            'projected_population_10_years': int(future_population),
            'days_simulated': len(self.historical_data),
            'major_events_today': len(self._generate_events())
        }
    
    def get_detailed_demographics(self) -> Dict:
        """Get detailed demographic breakdowns"""
        
        demographics = {}
        
        for region, segment in self.current_state.segments.items():
            demographics[region] = {
                'population': segment.count,
                'percentage_of_world': (segment.count / self.current_state.total_population) * 100,
                'age_distribution': segment.age_distribution,
                'education_levels': segment.education_levels,
                'economic_status': segment.economic_status,
                'geographic_distribution': segment.geographic_distribution,
                'health_status': segment.health_status
            }
        
        return demographics
    
    def apply_policy_intervention(self, policy: Dict) -> Dict:
        """Apply a policy intervention to the world simulation"""
        
        policy_type = policy.get('type', 'unknown')
        magnitude = policy.get('magnitude', 0.1)
        duration = policy.get('duration', 30)  # days
        
        results = {
            'policy_applied': policy_type,
            'magnitude': magnitude,
            'duration': duration,
            'effects': {}
        }
        
        if policy_type == 'carbon_tax':
            self.current_state.carbon_emissions *= (1 - magnitude * 0.5)
            self.current_state.renewable_energy_percentage *= (1 + magnitude * 0.3)
            results['effects']['carbon_reduction'] = magnitude * 0.5
            results['effects']['renewable_boost'] = magnitude * 0.3
            
        elif policy_type == 'education_investment':
            for segment in self.current_state.segments.values():
                # Shift education levels upward
                tertiary_boost = magnitude * 0.1
                segment.education_levels['tertiary'] += tertiary_boost
                segment.education_levels['no_formal'] -= tertiary_boost * 0.5
                segment.education_levels['primary'] -= tertiary_boost * 0.5
            results['effects']['education_improvement'] = magnitude * 0.1
            
        elif policy_type == 'healthcare_reform':
            self.death_rate *= (1 - magnitude * 0.3)
            for segment in self.current_state.segments.values():
                # Improve health status
                excellent_boost = magnitude * 0.05
                segment.health_status['excellent'] += excellent_boost
                segment.health_status['critical'] -= excellent_boost * 0.5
                segment.health_status['poor'] -= excellent_boost * 0.5
            results['effects']['death_rate_reduction'] = magnitude * 0.3
            results['effects']['health_improvement'] = magnitude * 0.05
            
        elif policy_type == 'technology_investment':
            self.current_state.technology_index *= (1 + magnitude * 0.2)
            self.current_state.gdp_growth_rate *= (1 + magnitude * 0.1)
            results['effects']['technology_boost'] = magnitude * 0.2
            results['effects']['gdp_boost'] = magnitude * 0.1
            
        elif policy_type == 'governance_reform':
            self.current_state.governance_index *= (1 + magnitude * 0.15)
            self.current_state.happiness_index *= (1 + magnitude * 0.1)
            results['effects']['governance_improvement'] = magnitude * 0.15
            results['effects']['happiness_boost'] = magnitude * 0.1
        
        return results
    
    def export_data(self, format: str = 'json') -> str:
        """Export simulation data"""
        
        data = {
            'simulation_state': asdict(self.current_state),
            'statistics': self.get_statistics(),
            'demographics': self.get_detailed_demographics(),
            'historical_data': self.historical_data[-30:],  # Last 30 days
            'export_timestamp': datetime.now().isoformat()
        }
        
        if format == 'json':
            return json.dumps(data, indent=2, default=str)
        else:
            return str(data)
    
    async def run_simulation(self, duration_days: int = None) -> None:
        """Run the simulation continuously"""
        
        self.running = True
        start_time = time.time()
        days_simulated = 0
        
        logger.info(f"Starting world simulation with {self.current_state.total_population:,} population")
        
        while self.running:
            if duration_days and days_simulated >= duration_days:
                break
            
            # Simulate one day
            day_result = self.simulate_day()
            days_simulated += 1
            
            # Log progress every 30 days
            if days_simulated % 30 == 0:
                logger.info(f"Simulated {days_simulated} days. Population: {day_result['population']:,}, "
                          f"Happiness: {day_result['happiness_index']:.3f}")
            
            # Control simulation speed
            await asyncio.sleep(1.0 / self.simulation_speed)
        
        logger.info(f"Simulation completed. Total days simulated: {days_simulated}")

# Demo function
async def demo_world_simulation():
    """Demonstrate the world simulation"""
    
    sim = WorldSimulationEngine()
    
    print("=== World Simulation Demo ===")
    print(f"Initial Population: {sim.current_state.total_population:,}")
    print(f"Simulation Start Date: {sim.current_state.timestamp.strftime('%Y-%m-%d')}")
    
    # Run 30 days of simulation
    await sim.run_simulation(duration_days=30)
    
    # Display results
    stats = sim.get_statistics()
    print("\n=== Simulation Results ===")
    print(f"Final Population: {stats['total_population']:,}")
    print(f"Population Growth Rate: {stats['population_growth_rate_percent']:.2f}%")
    print(f"Global GDP: ${stats['global_gdp_trillion_usd']:.2f} trillion")
    print(f"Carbon Emissions: {stats['carbon_emissions_gigatons']:.2f} gigatons")
    print(f"Renewable Energy: {stats['renewable_energy_percent']:.1f}%")
    print(f"Happiness Index: {stats['happiness_index']:.3f}")
    print(f"Technology Index: {stats['technology_index']:.3f}")
    print(f"Governance Index: {stats['governance_index']:.3f}")
    
    # Apply a policy intervention
    print("\n=== Applying Policy: Carbon Tax ===")
    policy_result = sim.apply_policy_intervention({
        'type': 'carbon_tax',
        'magnitude': 0.3,
        'duration': 90
    })
    
    print(f"Carbon Reduction: {policy_result['effects'].get('carbon_reduction', 0):.2%}")
    print(f"Renewable Energy Boost: {policy_result['effects'].get('renewable_boost', 0):.2%}")
    
    # Run another 30 days with the policy
    await sim.run_simulation(duration_days=30)
    
    # Final statistics
    final_stats = sim.get_statistics()
    print(f"\nFinal Carbon Emissions: {final_stats['carbon_emissions_gigatons']:.2f} gigatons")
    print(f"Final Renewable Energy: {final_stats['renewable_energy_percent']:.1f}%")

if __name__ == "__main__":
    asyncio.run(demo_world_simulation())
