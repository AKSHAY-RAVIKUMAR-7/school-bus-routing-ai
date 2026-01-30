"""
Genetic Algorithm for Bus Route Optimization

Multi-objective optimization:
- Minimize total distance
- Minimize total time
- Maximize bus capacity utilization
- Minimize fuel consumption
"""
import numpy as np
import random
from typing import List, Dict, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class Stop:
    id: int
    location: Tuple[float, float]  # (lat, lng)
    students: int
    time_window: Tuple[int, int] = (0, 1440)  # minutes from midnight

@dataclass
class Bus:
    id: int
    capacity: int
    fuel_efficiency: float = 8.0  # km per liter

@dataclass
class Route:
    bus_id: int
    stops: List[int]  # List of stop IDs
    total_distance: float = 0.0
    total_time: int = 0
    fitness: float = 0.0

class GeneticAlgorithmOptimizer:
    """
    Genetic Algorithm for optimizing school bus routes
    """
    
    def __init__(self, population_size: int = 50, generations: int = 100,
                 mutation_rate: float = 0.1, crossover_rate: float = 0.8):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.distance_weight = 0.4
        self.time_weight = 0.3
        self.capacity_weight = 0.3
    
    def optimize(self, stops: List[Dict], buses: List[Dict], 
                 constraints: Dict) -> Dict:
        """
        Main optimization function
        
        Args:
            stops: List of stop dictionaries
            buses: List of bus dictionaries
            constraints: Optimization constraints
        
        Returns:
            Optimized routes with metrics
        """
        logger.info("Starting genetic algorithm optimization")
        
        # Convert to dataclass objects
        stop_objects = [Stop(s['id'], (s['location']['lat'], s['location']['lng']), 
                            s.get('students', 1)) for s in stops]
        bus_objects = [Bus(b['id'], b['capacity']) for b in buses]
        
        # Initialize population
        population = self._initialize_population(stop_objects, bus_objects)
        
        best_solution = None
        best_fitness = float('-inf')
        
        for generation in range(self.generations):
            # Evaluate fitness
            for route in population:
                route.fitness = self._calculate_fitness(route, stop_objects, bus_objects)
            
            # Sort by fitness
            population.sort(key=lambda x: x.fitness, reverse=True)
            
            # Track best solution
            if population[0].fitness > best_fitness:
                best_fitness = population[0].fitness
                best_solution = population[0]
                logger.info(f"Generation {generation}: New best fitness = {best_fitness:.4f}")
            
            # Selection and reproduction
            new_population = population[:2]  # Elitism: keep top 2
            
            while len(new_population) < self.population_size:
                parent1 = self._tournament_selection(population)
                parent2 = self._tournament_selection(population)
                
                if random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1, parent2
                
                if random.random() < self.mutation_rate:
                    child1 = self._mutate(child1)
                if random.random() < self.mutation_rate:
                    child2 = self._mutate(child2)
                
                new_population.extend([child1, child2])
            
            population = new_population[:self.population_size]
        
        # Calculate final metrics
        metrics = self._calculate_route_metrics(best_solution, stop_objects, bus_objects)
        
        return {
            'routes': self._format_routes([best_solution], stop_objects),
            'metrics': metrics,
            'generations': self.generations,
            'final_fitness': best_fitness
        }
    
    def _initialize_population(self, stops: List[Stop], buses: List[Bus]) -> List[Route]:
        """Create initial random population"""
        population = []
        stop_ids = [s.id for s in stops]
        
        for _ in range(self.population_size):
            for bus in buses:
                # Randomly shuffle stops
                route_stops = random.sample(stop_ids, 
                                          min(len(stop_ids), random.randint(3, len(stop_ids))))
                
                route = Route(bus_id=bus.id, stops=route_stops)
                population.append(route)
        
        return population[:self.population_size]
    
    def _calculate_fitness(self, route: Route, stops: List[Stop], 
                          buses: List[Bus]) -> float:
        """
        Calculate fitness score for a route
        Higher is better
        """
        # Calculate distance
        distance = self._calculate_total_distance(route, stops)
        
        # Calculate time (assuming average speed of 30 km/h)
        time = distance / 30.0 * 60  # minutes
        
        # Calculate capacity utilization
        bus = next(b for b in buses if b.id == route.bus_id)
        total_students = sum(s.students for s in stops if s.id in route.stops)
        capacity_util = min(total_students / bus.capacity, 1.0)
        
        # Normalize and weight
        distance_score = 1.0 / (1.0 + distance / 100.0)  # Lower distance is better
        time_score = 1.0 / (1.0 + time / 60.0)  # Lower time is better
        capacity_score = capacity_util  # Higher utilization is better
        
        fitness = (self.distance_weight * distance_score + 
                  self.time_weight * time_score + 
                  self.capacity_weight * capacity_score)
        
        return fitness
    
    def _calculate_total_distance(self, route: Route, stops: List[Stop]) -> float:
        """Calculate total distance for a route using Haversine formula"""
        if len(route.stops) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(route.stops) - 1):
            stop1 = next(s for s in stops if s.id == route.stops[i])
            stop2 = next(s for s in stops if s.id == route.stops[i + 1])
            total_distance += self._haversine_distance(stop1.location, stop2.location)
        
        return total_distance
    
    def _haversine_distance(self, loc1: Tuple[float, float], 
                           loc2: Tuple[float, float]) -> float:
        """Calculate distance between two GPS coordinates in kilometers"""
        lat1, lon1 = np.radians(loc1)
        lat2, lon2 = np.radians(loc2)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return 6371 * c  # Earth radius in km
    
    def _tournament_selection(self, population: List[Route], 
                             tournament_size: int = 3) -> Route:
        """Select parent using tournament selection"""
        tournament = random.sample(population, tournament_size)
        return max(tournament, key=lambda x: x.fitness)
    
    def _crossover(self, parent1: Route, parent2: Route) -> Tuple[Route, Route]:
        """Order crossover (OX) for route permutation"""
        if len(parent1.stops) < 2 or len(parent2.stops) < 2:
            return parent1, parent2
        
        # Create children
        size = min(len(parent1.stops), len(parent2.stops))
        start, end = sorted(random.sample(range(size), 2))
        
        child1_stops = parent1.stops[start:end]
        child2_stops = parent2.stops[start:end]
        
        # Fill remaining positions
        for stop in parent2.stops:
            if stop not in child1_stops and len(child1_stops) < len(parent1.stops):
                child1_stops.append(stop)
        
        for stop in parent1.stops:
            if stop not in child2_stops and len(child2_stops) < len(parent2.stops):
                child2_stops.append(stop)
        
        child1 = Route(bus_id=parent1.bus_id, stops=child1_stops)
        child2 = Route(bus_id=parent2.bus_id, stops=child2_stops)
        
        return child1, child2
    
    def _mutate(self, route: Route) -> Route:
        """Swap mutation: swap two random stops"""
        if len(route.stops) < 2:
            return route
        
        mutated_stops = route.stops.copy()
        i, j = random.sample(range(len(mutated_stops)), 2)
        mutated_stops[i], mutated_stops[j] = mutated_stops[j], mutated_stops[i]
        
        return Route(bus_id=route.bus_id, stops=mutated_stops)
    
    def _calculate_route_metrics(self, route: Route, stops: List[Stop], 
                                 buses: List[Bus]) -> Dict:
        """Calculate detailed metrics for the route"""
        distance = self._calculate_total_distance(route, stops)
        time = distance / 30.0 * 60  # minutes
        
        bus = next(b for b in buses if b.id == route.bus_id)
        fuel = distance / bus.fuel_efficiency
        
        total_students = sum(s.students for s in stops if s.id in route.stops)
        
        return {
            'total_distance_km': round(distance, 2),
            'estimated_time_minutes': round(time, 2),
            'fuel_consumption_liters': round(fuel, 2),
            'students_served': total_students,
            'capacity_utilization': round(total_students / bus.capacity * 100, 2),
            'stops_count': len(route.stops)
        }
    
    def _format_routes(self, routes: List[Route], stops: List[Stop]) -> List[Dict]:
        """Format routes for API response"""
        formatted = []
        for route in routes:
            formatted.append({
                'bus_id': route.bus_id,
                'stops': [
                    {
                        'id': stop_id,
                        'location': next(s.location for s in stops if s.id == stop_id),
                        'sequence': idx
                    }
                    for idx, stop_id in enumerate(route.stops)
                ],
                'fitness_score': round(route.fitness, 4)
            })
        return formatted
