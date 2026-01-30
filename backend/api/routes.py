"""
API routes for route optimization
"""
from flask import Blueprint, request, jsonify
from services.route_optimizer import RouteOptimizer
from services.genetic_algorithm import GeneticAlgorithmOptimizer
from services.reinforcement_learning import RLOptimizer
from database.connection import get_db
from database.models import Route, Bus, Stop
import logging

bp = Blueprint('routes', __name__)
logger = logging.getLogger(__name__)

@bp.route('/optimize', methods=['POST'])
def optimize_routes():
    """
    Optimize bus routes using AI/ML algorithms
    
    Request body:
    {
        "algorithm": "genetic|rl|hybrid",
        "stops": [{"id": 1, "location": {"lat": 0, "lng": 0}, "students": 5}],
        "buses": [{"id": 1, "capacity": 50}],
        "constraints": {"max_time": 60, "max_distance": 50}
    }
    """
    try:
        data = request.json
        algorithm = data.get('algorithm', 'genetic')
        
        if algorithm == 'genetic':
            optimizer = GeneticAlgorithmOptimizer()
        elif algorithm == 'rl':
            optimizer = RLOptimizer()
        else:
            optimizer = RouteOptimizer()  # Hybrid approach
        
        result = optimizer.optimize(
            stops=data['stops'],
            buses=data['buses'],
            constraints=data.get('constraints', {})
        )
        
        return jsonify({
            'success': True,
            'routes': result['routes'],
            'metrics': result['metrics'],
            'algorithm': algorithm
        }), 200
        
    except Exception as e:
        logger.error(f"Route optimization error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<int:route_id>', methods=['GET'])
def get_route(route_id):
    """Get route details by ID"""
    try:
        db = next(get_db())
        route = db.query(Route).filter(Route.id == route_id).first()
        
        if not route:
            return jsonify({'error': 'Route not found'}), 404
        
        return jsonify({
            'id': route.id,
            'name': route.name,
            'bus_id': route.bus_id,
            'total_distance': route.total_distance,
            'estimated_duration': route.estimated_duration,
            'optimization_score': route.optimization_score,
            'stops': [
                {
                    'id': rs.stop.id,
                    'name': rs.stop.name,
                    'location': rs.stop.location,
                    'sequence': rs.sequence,
                    'arrival_time': rs.arrival_time.isoformat() if rs.arrival_time else None
                }
                for rs in route.route_stops
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching route: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['GET'])
def list_routes():
    """List all active routes"""
    try:
        db = next(get_db())
        routes = db.query(Route).filter(Route.is_active == True).all()
        
        return jsonify({
            'routes': [
                {
                    'id': r.id,
                    'name': r.name,
                    'bus_number': r.bus.bus_number if r.bus else None,
                    'total_distance': r.total_distance,
                    'stop_count': len(r.route_stops)
                }
                for r in routes
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing routes: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:route_id>', methods=['PUT'])
def update_route(route_id):
    """Update route details"""
    try:
        db = next(get_db())
        route = db.query(Route).filter(Route.id == route_id).first()
        
        if not route:
            return jsonify({'error': 'Route not found'}), 404
        
        data = request.json
        if 'name' in data:
            route.name = data['name']
        if 'is_active' in data:
            route.is_active = data['is_active']
        
        db.commit()
        
        return jsonify({'success': True, 'message': 'Route updated'}), 200
        
    except Exception as e:
        logger.error(f"Error updating route: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:route_id>', methods=['DELETE'])
def delete_route(route_id):
    """Soft delete a route"""
    try:
        db = next(get_db())
        route = db.query(Route).filter(Route.id == route_id).first()
        
        if not route:
            return jsonify({'error': 'Route not found'}), 404
        
        route.is_active = False
        db.commit()
        
        return jsonify({'success': True, 'message': 'Route deleted'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting route: {str(e)}")
        return jsonify({'error': str(e)}), 500
