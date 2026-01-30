"""
Reinforcement Learning Agent for Adaptive Route Optimization

Uses Deep Q-Network (DQN) to learn optimal routing policies
based on traffic patterns, weather, and historical data
"""
import numpy as np
import random
from collections import deque
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class RouteState:
    """Represents the current state of routing"""
    def __init__(self, stops: List, current_route: List[int], 
                 traffic_level: float, weather_condition: str):
        self.stops = stops
        self.current_route = current_route
        self.traffic_level = traffic_level  # 0-1 scale
        self.weather_condition = weather_condition
    
    def to_vector(self) -> np.ndarray:
        """Convert state to feature vector"""
        weather_encoding = {'clear': 0, 'rain': 0.5, 'heavy_rain': 1.0, 'snow': 0.8}
        
        features = [
            len(self.current_route),
            self.traffic_level,
            weather_encoding.get(self.weather_condition, 0),
            len(self.stops),
        ]
        
        # Add route encoding (simplified)
        route_features = np.zeros(20)
        for i, stop_id in enumerate(self.current_route[:20]):
            route_features[i] = stop_id / max(len(self.stops), 1)
        
        return np.array(features + route_features.tolist())

class DQN:
    """Deep Q-Network for route optimization"""
    
    def __init__(self, state_size: int, action_size: int):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        
        # Placeholder for neural network (would use TensorFlow/PyTorch in production)
        self.q_table = {}
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in memory"""
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state: np.ndarray) -> int:
        """Choose action using epsilon-greedy policy"""
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        
        # Get Q-values for all actions
        state_key = tuple(state.round(2))  # Discretize state
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        
        return np.argmax(self.q_table[state_key])
    
    def replay(self, batch_size: int = 32):
        """Train on batch of experiences"""
        if len(self.memory) < batch_size:
            return
        
        minibatch = random.sample(self.memory, batch_size)
        
        for state, action, reward, next_state, done in minibatch:
            state_key = tuple(state.round(2))
            next_state_key = tuple(next_state.round(2))
            
            if state_key not in self.q_table:
                self.q_table[state_key] = np.zeros(self.action_size)
            if next_state_key not in self.q_table:
                self.q_table[next_state_key] = np.zeros(self.action_size)
            
            target = reward
            if not done:
                target = reward + self.gamma * np.max(self.q_table[next_state_key])
            
            self.q_table[state_key][action] = target
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

class RLOptimizer:
    """Reinforcement Learning based route optimizer"""
    
    def __init__(self):
        self.state_size = 24  # Size of state vector
        self.action_size = 10  # Number of possible actions
        self.agent = DQN(self.state_size, self.action_size)
        self.episodes = 100
    
    def optimize(self, stops: List[Dict], buses: List[Dict], 
                 constraints: Dict) -> Dict:
        """
        Optimize routes using reinforcement learning
        
        Args:
            stops: List of stop dictionaries
            buses: List of bus dictionaries
            constraints: Optimization constraints
        
        Returns:
            Optimized routes with metrics
        """
        logger.info("Starting RL-based optimization")
        
        best_route = None
        best_reward = float('-inf')
        
        for episode in range(self.episodes):
            state = self._initialize_state(stops)
            route = []
            total_reward = 0
            done = False
            
            while not done and len(route) < len(stops):
                # Get state vector
                state_vector = state.to_vector()
                
                # Choose action
                action = self.agent.act(state_vector)
                
                # Execute action (add stop to route)
                next_stop = self._apply_action(action, route, stops)
                
                # Calculate reward
                reward = self._calculate_reward(route, next_stop, stops, constraints)
                
                # Update state
                next_state = self._update_state(state, next_stop, route)
                
                # Check if done
                done = len(route) >= len(stops) or next_stop is None
                
                if next_stop:
                    route.append(next_stop)
                    total_reward += reward
                
                # Remember experience
                self.agent.remember(state_vector, action, reward, 
                                  next_state.to_vector(), done)
                
                state = next_state
            
            # Train agent
            self.agent.replay()
            
            if total_reward > best_reward:
                best_reward = total_reward
                best_route = route
                logger.info(f"Episode {episode}: New best reward = {best_reward:.2f}")
        
        # Format results
        return self._format_results(best_route, stops, buses, best_reward)
    
    def _initialize_state(self, stops: List[Dict]) -> RouteState:
        """Initialize starting state"""
        return RouteState(
            stops=stops,
            current_route=[],
            traffic_level=random.uniform(0.3, 0.7),
            weather_condition=random.choice(['clear', 'rain', 'heavy_rain'])
        )
    
    def _apply_action(self, action: int, route: List[int], 
                     stops: List[Dict]) -> int:
        """Apply action to select next stop"""
        available_stops = [s['id'] for s in stops if s['id'] not in route]
        
        if not available_stops:
            return None
        
        # Map action to stop selection strategy
        if action == 0:  # Nearest stop
            return available_stops[0] if available_stops else None
        elif action == 1:  # Farthest stop
            return available_stops[-1] if available_stops else None
        else:  # Random stop
            return random.choice(available_stops) if available_stops else None
    
    def _calculate_reward(self, route: List[int], next_stop: int, 
                         stops: List[Dict], constraints: Dict) -> float:
        """
        Calculate reward for taking an action
        Positive reward for good decisions, negative for bad ones
        """
        if next_stop is None:
            return -10.0
        
        reward = 0.0
        
        # Reward for serving students
        stop = next(s for s in stops if s['id'] == next_stop)
        reward += stop.get('students', 1) * 2.0
        
        # Penalty for distance
        if route:
            last_stop = next(s for s in stops if s['id'] == route[-1])
            distance = self._calculate_distance(
                last_stop['location'], 
                stop['location']
            )
            reward -= distance * 0.1
        
        # Penalty for time constraint violation
        max_time = constraints.get('max_time', 60)
        if len(route) * 5 > max_time:  # Rough estimate
            reward -= 5.0
        
        return reward
    
    def _calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """Calculate distance between two locations"""
        lat1, lon1 = loc1['lat'], loc1['lng']
        lat2, lon2 = loc2['lat'], loc2['lng']
        
        # Simplified Euclidean distance (should use Haversine)
        return np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111.0  # Rough km conversion
    
    def _update_state(self, state: RouteState, next_stop: int, 
                     route: List[int]) -> RouteState:
        """Update state after action"""
        new_route = route + ([next_stop] if next_stop else [])
        
        # Traffic might change
        traffic_change = random.uniform(-0.1, 0.1)
        new_traffic = max(0, min(1, state.traffic_level + traffic_change))
        
        return RouteState(
            stops=state.stops,
            current_route=new_route,
            traffic_level=new_traffic,
            weather_condition=state.weather_condition
        )
    
    def _format_results(self, route: List[int], stops: List[Dict], 
                       buses: List[Dict], reward: float) -> Dict:
        """Format optimization results"""
        if not route or not buses:
            return {'routes': [], 'metrics': {}}
        
        bus = buses[0]  # Use first bus
        
        # Calculate metrics
        total_distance = 0.0
        for i in range(len(route) - 1):
            stop1 = next(s for s in stops if s['id'] == route[i])
            stop2 = next(s for s in stops if s['id'] == route[i + 1])
            total_distance += self._calculate_distance(stop1['location'], 
                                                       stop2['location'])
        
        return {
            'routes': [{
                'bus_id': bus['id'],
                'stops': [
                    {
                        'id': stop_id,
                        'location': next(s['location'] for s in stops if s['id'] == stop_id),
                        'sequence': idx
                    }
                    for idx, stop_id in enumerate(route)
                ],
                'rl_reward': round(reward, 2)
            }],
            'metrics': {
                'total_distance_km': round(total_distance, 2),
                'estimated_time_minutes': round(len(route) * 5, 2),
                'stops_count': len(route),
                'rl_episodes': self.episodes,
                'final_reward': round(reward, 2)
            }
        }
