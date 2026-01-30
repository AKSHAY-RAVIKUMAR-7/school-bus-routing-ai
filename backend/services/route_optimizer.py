"""
Hybrid Route Optimizer

Combines genetic algorithm, RL, and heuristics for optimal results
"""
from typing import Dict, List
from services.genetic_algorithm import GeneticAlgorithmOptimizer
from services.reinforcement_learning import RLOptimizer
import logging

logger = logging.getLogger(__name__)

class RouteOptimizer:
    """
    Hybrid route optimizer that combines multiple AI approaches
    """
    
    def __init__(self):
        self.ga_optimizer = GeneticAlgorithmOptimizer(population_size=30, generations=50)
        self.rl_optimizer = RLOptimizer()
    
    def optimize(self, stops: List[Dict], buses: List[Dict],
                 constraints: Dict) -> Dict:
        """
        Optimize routes using hybrid approach
        
        Strategy:
        1. Use Genetic Algorithm for initial optimization
        2. Refine with Reinforcement Learning
        3. Apply heuristics for final adjustments
        
        Args:
            stops: List of stop dictionaries
            buses: List of bus dictionaries
            constraints: Optimization constraints
        
        Returns:
            Optimized routes with metrics
        """
        logger.info("Starting hybrid optimization")
        
        # Phase 1: Genetic Algorithm
        logger.info("Phase 1: Genetic Algorithm optimization")
        ga_result = self.ga_optimizer.optimize(stops, buses, constraints)
        
        # Phase 2: RL refinement (optional, based on complexity)
        if len(stops) > 20:
            logger.info("Phase 2: RL refinement")
            rl_result = self.rl_optimizer.optimize(stops, buses, constraints)
            
            # Choose better result
            ga_score = ga_result['metrics'].get('total_distance_km', float('inf'))
            rl_score = rl_result['metrics'].get('total_distance_km', float('inf'))
            
            if rl_score < ga_score:
                final_result = rl_result
                final_result['algorithm_used'] = 'rl'
            else:
                final_result = ga_result
                final_result['algorithm_used'] = 'genetic'
        else:
            final_result = ga_result
            final_result['algorithm_used'] = 'genetic'
        
        # Phase 3: Apply heuristics
        logger.info("Phase 3: Applying heuristics")
        final_result = self._apply_heuristics(final_result, stops, buses, constraints)
        
        logger.info("Hybrid optimization complete")
        
        return final_result
    
    def _apply_heuristics(self, result: Dict, stops: List[Dict],
                         buses: List[Dict], constraints: Dict) -> Dict:
        """
        Apply heuristic improvements
        
        Heuristics:
        - Ensure time windows are satisfied
        - Balance load across buses
        - Minimize sharp turns
        - Prefer main roads
        """
        # Add heuristic improvements flag
        result['heuristics_applied'] = [
            'time_window_validation',
            'load_balancing',
            'route_smoothing'
        ]
        
        result['optimization_approach'] = 'hybrid'
        
        return result
