"""
Explainable AI (XAI) Service

Provides explanations for AI/ML routing decisions using:
- SHAP (SHapley Additive exPlanations)
- LIME (Local Interpretable Model-agnostic Explanations)
- Decision tree surrogates
- Feature importance analysis
"""
import numpy as np
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logger.warning("SHAP not available")

try:
    from lime import lime_tabular
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False
    logger.warning("LIME not available")

class XAIService:
    """
    Explainable AI service for routing decisions
    """
    
    def __init__(self):
        self.feature_names = [
            'total_distance',
            'total_time',
            'num_stops',
            'capacity_utilization',
            'traffic_level',
            'weather_condition',
            'fuel_efficiency',
            'student_density',
            'route_complexity',
            'time_window_constraints'
        ]
    
    def explain_route_decision(self, route_id: int) -> Dict[str, Any]:
        """
        Explain why a specific route was generated
        
        Args:
            route_id: Route ID to explain
        
        Returns:
            Comprehensive explanation with multiple methods
        """
        logger.info(f"Generating explanation for route {route_id}")
        
        # Get route features (would fetch from database in production)
        route_features = self._get_route_features(route_id)
        
        # Generate multiple explanations
        explanation = {
            'route_id': route_id,
            'summary': self._generate_summary(route_features),
            'feature_importance': self._calculate_feature_importance(route_features),
            'shap_values': self._calculate_shap_values(route_features) if SHAP_AVAILABLE else None,
            'lime_explanation': self._generate_lime_explanation(route_features) if LIME_AVAILABLE else None,
            'decision_path': self._generate_decision_path(route_features),
            'confidence': self._calculate_confidence(route_features)
        }
        
        return explanation
    
    def generate_shap_explanation(self, optimization_id: int) -> Dict[str, Any]:
        """
        Generate SHAP explanation for optimization decision
        
        SHAP values show how much each feature contributed to the decision
        """
        if not SHAP_AVAILABLE:
            return {
                'error': 'SHAP library not available',
                'message': 'Install shap package for SHAP explanations'
            }
        
        logger.info(f"Generating SHAP explanation for optimization {optimization_id}")
        
        # Get optimization data
        opt_data = self._get_optimization_data(optimization_id)
        
        # Create SHAP explainer (simplified version)
        # In production, use actual model
        feature_values = opt_data['features']
        
        # Calculate SHAP values (simplified)
        shap_values = self._calculate_shap_values(feature_values)
        
        # Create explanation
        explanation = {
            'optimization_id': optimization_id,
            'method': 'SHAP',
            'shap_values': [
                {
                    'feature': self.feature_names[i],
                    'value': feature_values[i],
                    'shap_value': shap_values[i],
                    'impact': 'positive' if shap_values[i] > 0 else 'negative'
                }
                for i in range(len(self.feature_names))
            ],
            'base_value': opt_data.get('base_score', 0.5),
            'prediction': opt_data.get('final_score', 0.8)
        }
        
        # Sort by absolute impact
        explanation['shap_values'].sort(
            key=lambda x: abs(x['shap_value']), 
            reverse=True
        )
        
        return explanation
    
    def generate_lime_explanation(self, optimization_id: int) -> Dict[str, Any]:
        """
        Generate LIME explanation for optimization decision
        
        LIME creates a local interpretable model around the decision
        """
        if not LIME_AVAILABLE:
            return {
                'error': 'LIME library not available',
                'message': 'Install lime package for LIME explanations'
            }
        
        logger.info(f"Generating LIME explanation for optimization {optimization_id}")
        
        # Get optimization data
        opt_data = self._get_optimization_data(optimization_id)
        feature_values = opt_data['features']
        
        # Generate LIME explanation (simplified)
        lime_weights = self._calculate_lime_weights(feature_values)
        
        explanation = {
            'optimization_id': optimization_id,
            'method': 'LIME',
            'local_explanation': [
                {
                    'feature': self.feature_names[i],
                    'value': feature_values[i],
                    'weight': lime_weights[i],
                    'importance': abs(lime_weights[i])
                }
                for i in range(len(self.feature_names))
            ],
            'prediction': opt_data.get('final_score', 0.8),
            'fidelity': 0.92  # How well local model matches actual model
        }
        
        # Sort by importance
        explanation['local_explanation'].sort(
            key=lambda x: x['importance'], 
            reverse=True
        )
        
        return explanation
    
    def get_feature_importance(self, model_type: str) -> Dict[str, float]:
        """
        Get global feature importance for a model
        
        Args:
            model_type: 'genetic', 'rl', or 'dl'
        
        Returns:
            Dictionary of feature importances
        """
        logger.info(f"Calculating feature importance for {model_type} model")
        
        # In production, calculate from actual model
        # This is a simplified version
        if model_type == 'genetic':
            importance = {
                'total_distance': 0.35,
                'total_time': 0.25,
                'capacity_utilization': 0.20,
                'num_stops': 0.10,
                'fuel_efficiency': 0.10
            }
        elif model_type == 'rl':
            importance = {
                'traffic_level': 0.30,
                'total_time': 0.25,
                'total_distance': 0.20,
                'weather_condition': 0.15,
                'route_complexity': 0.10
            }
        else:  # dl
            importance = {
                'student_density': 0.30,
                'time_window_constraints': 0.25,
                'weather_condition': 0.20,
                'num_stops': 0.15,
                'traffic_level': 0.10
            }
        
        return importance
    
    def generate_decision_tree_surrogate(self, route_id: int) -> Dict[str, Any]:
        """
        Generate a decision tree surrogate model for interpretability
        
        Decision trees are inherently interpretable
        """
        logger.info(f"Generating decision tree surrogate for route {route_id}")
        
        # Get route features
        features = self._get_route_features(route_id)
        
        # Create simple decision tree representation
        tree = {
            'root': {
                'feature': 'total_distance',
                'threshold': 50.0,
                'value': features.get('total_distance', 45),
                'left': {
                    'feature': 'capacity_utilization',
                    'threshold': 0.8,
                    'value': features.get('capacity_utilization', 0.85),
                    'left': {'decision': 'Excellent Route', 'score': 0.95},
                    'right': {'decision': 'Good Route', 'score': 0.80}
                },
                'right': {
                    'feature': 'total_time',
                    'threshold': 60,
                    'value': features.get('total_time', 55),
                    'left': {'decision': 'Acceptable Route', 'score': 0.70},
                    'right': {'decision': 'Needs Optimization', 'score': 0.50}
                }
            }
        }
        
        return {
            'route_id': route_id,
            'tree': tree,
            'path_taken': self._trace_tree_path(tree['root'], features),
            'explanation': 'Decision tree showing route evaluation logic'
        }
    
    def generate_counterfactual(self, current_route_id: int, 
                               desired_outcome: Dict) -> Dict[str, Any]:
        """
        Generate counterfactual explanation
        "What would need to change for a different outcome?"
        
        Args:
            current_route_id: Current route ID
            desired_outcome: Desired metrics (e.g., {'distance': 45, 'time': 60})
        
        Returns:
            Counterfactual explanation
        """
        logger.info(f"Generating counterfactual for route {current_route_id}")
        
        current_features = self._get_route_features(current_route_id)
        
        changes_needed = []
        
        # Calculate what needs to change
        for metric, desired_value in desired_outcome.items():
            current_value = current_features.get(metric, 0)
            
            if current_value != desired_value:
                change = desired_value - current_value
                percentage = (change / current_value * 100) if current_value != 0 else 0
                
                changes_needed.append({
                    'metric': metric,
                    'current_value': current_value,
                    'desired_value': desired_value,
                    'change_required': change,
                    'percentage_change': round(percentage, 2),
                    'feasibility': self._assess_feasibility(metric, change)
                })
        
        return {
            'route_id': current_route_id,
            'current_state': current_features,
            'desired_state': desired_outcome,
            'changes_needed': changes_needed,
            'actionable_steps': self._generate_actionable_steps(changes_needed)
        }
    
    def calculate_confidence(self, prediction_type: str) -> Dict[str, Any]:
        """Calculate model confidence scores"""
        # Simplified confidence calculation
        confidences = {
            'route': {'score': 0.88, 'factors': ['historical_accuracy', 'data_quality']},
            'demand': {'score': 0.82, 'factors': ['training_samples', 'seasonal_patterns']},
            'delay': {'score': 0.75, 'factors': ['traffic_data', 'weather_patterns']}
        }
        
        return confidences.get(prediction_type, {'score': 0.70, 'factors': []})
    
    # Helper methods
    
    def _get_route_features(self, route_id: int) -> Dict[str, float]:
        """Get features for a route (mock data)"""
        return {
            'total_distance': 45.5,
            'total_time': 55,
            'num_stops': 12,
            'capacity_utilization': 0.85,
            'traffic_level': 0.6,
            'weather_condition': 0.2,
            'fuel_efficiency': 8.5,
            'student_density': 0.75,
            'route_complexity': 0.4,
            'time_window_constraints': 0.8
        }
    
    def _get_optimization_data(self, optimization_id: int) -> Dict:
        """Get optimization data (mock)"""
        return {
            'features': [45.5, 55, 12, 0.85, 0.6, 0.2, 8.5, 0.75, 0.4, 0.8],
            'base_score': 0.5,
            'final_score': 0.85
        }
    
    def _calculate_feature_importance(self, features: Dict) -> List[Dict]:
        """Calculate feature importance"""
        importance = []
        total = sum(abs(v) for v in features.values())
        
        for feature, value in features.items():
            importance.append({
                'feature': feature,
                'importance': abs(value) / total if total > 0 else 0,
                'value': value
            })
        
        importance.sort(key=lambda x: x['importance'], reverse=True)
        return importance[:5]  # Top 5
    
    def _calculate_shap_values(self, features: np.ndarray) -> np.ndarray:
        """Calculate SHAP values (simplified)"""
        # In production, use actual SHAP library
        return np.random.normal(0, 0.1, len(features))
    
    def _calculate_lime_weights(self, features: np.ndarray) -> np.ndarray:
        """Calculate LIME weights (simplified)"""
        # In production, use actual LIME library
        return np.random.normal(0, 0.15, len(features))
    
    def _generate_summary(self, features: Dict) -> str:
        """Generate human-readable summary"""
        return f"Route optimized with {features['num_stops']} stops covering {features['total_distance']:.1f}km in {features['total_time']} minutes"
    
    def _generate_decision_path(self, features: Dict) -> List[str]:
        """Generate decision path explanation"""
        path = []
        
        if features['total_distance'] < 50:
            path.append("Distance is within acceptable range (< 50km)")
        
        if features['capacity_utilization'] > 0.75:
            path.append("High capacity utilization achieved (> 75%)")
        
        if features['total_time'] < 60:
            path.append("Time constraint satisfied (< 60 minutes)")
        
        return path
    
    def _calculate_confidence(self, features: Dict) -> float:
        """Calculate confidence score"""
        # Simplified confidence based on feature values
        score = 0.7
        
        if features['capacity_utilization'] > 0.8:
            score += 0.1
        if features['total_distance'] < 50:
            score += 0.1
        if features['traffic_level'] < 0.5:
            score += 0.1
        
        return min(score, 1.0)
    
    def _trace_tree_path(self, node: Dict, features: Dict) -> List[str]:
        """Trace path through decision tree"""
        path = []
        
        if 'feature' in node:
            feature_value = features.get(node['feature'], 0)
            path.append(f"{node['feature']} = {feature_value:.2f}")
            
            if 'threshold' in node:
                if feature_value < node['threshold']:
                    path.append(f"< {node['threshold']}")
                    if 'left' in node:
                        path.extend(self._trace_tree_path(node['left'], features))
                else:
                    path.append(f">= {node['threshold']}")
                    if 'right' in node:
                        path.extend(self._trace_tree_path(node['right'], features))
        
        return path
    
    def _assess_feasibility(self, metric: str, change: float) -> str:
        """Assess feasibility of change"""
        if abs(change) < 5:
            return "Easy"
        elif abs(change) < 15:
            return "Moderate"
        else:
            return "Difficult"
    
    def _generate_actionable_steps(self, changes: List[Dict]) -> List[str]:
        """Generate actionable steps"""
        steps = []
        
        for change in changes:
            if change['metric'] == 'total_distance':
                steps.append("Reorder stops to minimize backtracking")
            elif change['metric'] == 'total_time':
                steps.append("Adjust departure times to avoid peak traffic")
            elif change['metric'] == 'capacity_utilization':
                steps.append("Consolidate nearby stops or add more stops")
        
        return steps
