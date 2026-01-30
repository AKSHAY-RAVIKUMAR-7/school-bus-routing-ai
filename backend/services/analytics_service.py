"""
Analytics Service

Provides analytics, metrics, and insights for the system
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from database.connection import get_db
from database.models import Bus, Route, Student, TrackingData, OptimizationHistory
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for system analytics and metrics"""
    
    def calculate_efficiency(self, route_id: Optional[int] = None,
                           time_period: str = 'week') -> Dict:
        """Calculate route efficiency metrics"""
        try:
            db = next(get_db())
            
            # Calculate time range
            end_date = datetime.utcnow()
            if time_period == 'day':
                start_date = end_date - timedelta(days=1)
            elif time_period == 'week':
                start_date = end_date - timedelta(weeks=1)
            else:  # month
                start_date = end_date - timedelta(days=30)
            
            # Get routes
            query = db.query(Route).filter(Route.is_active == True)
            if route_id:
                query = query.filter(Route.id == route_id)
            
            routes = query.all()
            
            metrics = {
                'period': time_period,
                'routes_analyzed': len(routes),
                'average_distance': self._calculate_avg_distance(routes),
                'average_time': self._calculate_avg_time(routes),
                'average_efficiency_score': self._calculate_avg_efficiency(routes),
                'best_route': self._find_best_route(routes),
                'worst_route': self._find_worst_route(routes)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating efficiency: {str(e)}")
            return {}
    
    def calculate_fuel_consumption(self, bus_id: Optional[int] = None,
                                  time_period: str = 'month') -> Dict:
        """Calculate fuel consumption"""
        try:
            db = next(get_db())
            
            query = db.query(Bus).filter(Bus.status == 'active')
            if bus_id:
                query = query.filter(Bus.id == bus_id)
            
            buses = query.all()
            
            total_distance = 0.0
            total_fuel = 0.0
            
            for bus in buses:
                routes = db.query(Route).filter(Route.bus_id == bus.id).all()
                bus_distance = sum(r.total_distance or 0 for r in routes)
                bus_fuel = bus_distance / bus.fuel_efficiency
                
                total_distance += bus_distance
                total_fuel += bus_fuel
            
            return {
                'period': time_period,
                'buses_analyzed': len(buses),
                'total_distance_km': round(total_distance, 2),
                'total_fuel_liters': round(total_fuel, 2),
                'average_efficiency': round(total_distance / total_fuel if total_fuel > 0 else 0, 2),
                'estimated_cost': round(total_fuel * 1.5, 2)  # Assuming $1.5 per liter
            }
            
        except Exception as e:
            logger.error(f"Error calculating fuel consumption: {str(e)}")
            return {}
    
    def analyze_delays(self, route_id: Optional[int] = None) -> Dict:
        """Analyze delays and predict future delays"""
        try:
            # Mock implementation - would analyze actual tracking data
            analysis = {
                'average_delay_minutes': 5.2,
                'delay_frequency': 0.15,  # 15% of trips
                'common_causes': [
                    {'cause': 'Traffic congestion', 'percentage': 45},
                    {'cause': 'Weather conditions', 'percentage': 25},
                    {'cause': 'Road construction', 'percentage': 20},
                    {'cause': 'Other', 'percentage': 10}
                ],
                'predicted_delay_tomorrow': 3.5,
                'recommendations': [
                    'Adjust departure time by 10 minutes earlier',
                    'Consider alternate route via Main Street',
                    'Monitor traffic conditions in real-time'
                ]
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing delays: {str(e)}")
            return {}
    
    def get_total_buses(self) -> int:
        """Get total number of active buses"""
        try:
            db = next(get_db())
            return db.query(Bus).filter(Bus.status == 'active').count()
        except:
            return 0
    
    def get_active_routes_count(self) -> int:
        """Get number of active routes"""
        try:
            db = next(get_db())
            return db.query(Route).filter(Route.is_active == True).count()
        except:
            return 0
    
    def get_total_students(self) -> int:
        """Get total number of active students"""
        try:
            db = next(get_db())
            return db.query(Student).filter(Student.is_active == True).count()
        except:
            return 0
    
    def get_avg_efficiency(self) -> float:
        """Get average efficiency score"""
        try:
            db = next(get_db())
            routes = db.query(Route).filter(Route.is_active == True).all()
            
            if not routes:
                return 0.0
            
            scores = [r.optimization_score for r in routes if r.optimization_score]
            return round(sum(scores) / len(scores) if scores else 0.0, 2)
        except:
            return 0.0
    
    def get_recent_alerts(self, limit: int = 5) -> List[Dict]:
        """Get recent system alerts"""
        # Mock implementation
        return [
            {'type': 'info', 'message': 'Route optimization completed', 'timestamp': datetime.utcnow().isoformat()},
            {'type': 'warning', 'message': 'Bus 101 running 5 minutes late', 'timestamp': (datetime.utcnow() - timedelta(minutes=10)).isoformat()},
            {'type': 'success', 'message': 'New student added successfully', 'timestamp': (datetime.utcnow() - timedelta(hours=1)).isoformat()}
        ][:limit]
    
    def get_daily_stats(self) -> Dict:
        """Get daily statistics"""
        return {
            'trips_completed': 24,
            'total_distance_km': 450.5,
            'fuel_consumed_liters': 65.2,
            'students_transported': 245,
            'average_delay_minutes': 3.2,
            'on_time_percentage': 92.5
        }
    
    def get_optimization_history(self, limit: int = 10) -> List[Dict]:
        """Get history of optimization runs"""
        try:
            db = next(get_db())
            history = db.query(OptimizationHistory)\
                       .order_by(OptimizationHistory.created_at.desc())\
                       .limit(limit)\
                       .all()
            
            return [
                {
                    'id': h.id,
                    'algorithm': h.algorithm,
                    'execution_time': h.execution_time,
                    'metrics': h.metrics,
                    'created_at': h.created_at.isoformat()
                }
                for h in history
            ]
            
        except Exception as e:
            logger.error(f"Error fetching optimization history: {str(e)}")
            return []
    
    # Helper methods
    
    def _calculate_avg_distance(self, routes: List) -> float:
        """Calculate average distance across routes"""
        distances = [r.total_distance for r in routes if r.total_distance]
        return round(sum(distances) / len(distances) if distances else 0.0, 2)
    
    def _calculate_avg_time(self, routes: List) -> float:
        """Calculate average time across routes"""
        times = [r.estimated_duration for r in routes if r.estimated_duration]
        return round(sum(times) / len(times) if times else 0.0, 2)
    
    def _calculate_avg_efficiency(self, routes: List) -> float:
        """Calculate average efficiency score"""
        scores = [r.optimization_score for r in routes if r.optimization_score]
        return round(sum(scores) / len(scores) if scores else 0.0, 3)
    
    def _find_best_route(self, routes: List) -> Optional[Dict]:
        """Find best performing route"""
        if not routes:
            return None
        
        best = max(routes, key=lambda r: r.optimization_score or 0)
        
        return {
            'id': best.id,
            'name': best.name,
            'score': best.optimization_score
        }
    
    def _find_worst_route(self, routes: List) -> Optional[Dict]:
        """Find worst performing route"""
        if not routes:
            return None
        
        worst = min(routes, key=lambda r: r.optimization_score or 0)
        
        return {
            'id': worst.id,
            'name': worst.name,
            'score': worst.optimization_score
        }
