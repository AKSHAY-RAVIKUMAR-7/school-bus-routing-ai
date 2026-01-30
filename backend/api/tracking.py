"""
API routes for real-time bus tracking
"""
from flask import Blueprint, request, jsonify
from flask_socketio import emit, join_room, leave_room
from services.tracking_service import TrackingService
from database.connection import get_db
from database.models import Bus, TrackingData
import logging

bp = Blueprint('tracking', __name__)
logger = logging.getLogger(__name__)
tracking_service = TrackingService()

@bp.route('/buses/<int:bus_id>/location', methods=['GET'])
def get_bus_location(bus_id):
    """Get current location of a bus"""
    try:
        location = tracking_service.get_current_location(bus_id)
        
        if not location:
            return jsonify({'error': 'Bus not found or no tracking data'}), 404
        
        return jsonify({
            'bus_id': bus_id,
            'location': location['location'],
            'speed': location.get('speed'),
            'heading': location.get('heading'),
            'timestamp': location['timestamp']
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching bus location: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/buses/<int:bus_id>/location', methods=['POST'])
def update_bus_location(bus_id):
    """
    Update bus location (called by GPS device/mobile app)
    
    Request body:
    {
        "location": {"lat": 12.34, "lng": 56.78},
        "speed": 45.5,
        "heading": 180.0,
        "accuracy": 10.0
    }
    """
    try:
        data = request.json
        
        result = tracking_service.update_location(
            bus_id=bus_id,
            location=data['location'],
            speed=data.get('speed'),
            heading=data.get('heading'),
            accuracy=data.get('accuracy', 10.0)
        )
        
        # Broadcast to WebSocket clients
        emit('location_update', {
            'bus_id': bus_id,
            'location': data['location'],
            'speed': data.get('speed'),
            'timestamp': result['timestamp']
        }, broadcast=True, namespace='/tracking')
        
        return jsonify({'success': True, 'message': 'Location updated'}), 200
        
    except Exception as e:
        logger.error(f"Error updating bus location: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/buses/<int:bus_id>/history', methods=['GET'])
def get_tracking_history(bus_id):
    """Get historical tracking data for a bus"""
    try:
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        history = tracking_service.get_history(bus_id, start_time, end_time)
        
        return jsonify({
            'bus_id': bus_id,
            'data_points': len(history),
            'history': history
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching tracking history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/buses/active', methods=['GET'])
def get_active_buses():
    """Get all currently active buses with their locations"""
    try:
        db = next(get_db())
        buses = db.query(Bus).filter(Bus.status == 'active').all()
        
        active_buses = []
        for bus in buses:
            location = tracking_service.get_current_location(bus.id)
            if location:
                active_buses.append({
                    'id': bus.id,
                    'bus_number': bus.bus_number,
                    'location': location['location'],
                    'speed': location.get('speed'),
                    'last_update': location['timestamp']
                })
        
        return jsonify({'buses': active_buses}), 200
        
    except Exception as e:
        logger.error(f"Error fetching active buses: {str(e)}")
        return jsonify({'error': str(e)}), 500

# WebSocket events
def register_socketio_events(socketio):
    """Register SocketIO event handlers"""
    
    @socketio.on('connect', namespace='/tracking')
    def handle_connect():
        logger.info('Client connected to tracking stream')
    
    @socketio.on('disconnect', namespace='/tracking')
    def handle_disconnect():
        logger.info('Client disconnected from tracking stream')
    
    @socketio.on('subscribe_bus', namespace='/tracking')
    def handle_subscribe(data):
        bus_id = data.get('bus_id')
        if bus_id:
            join_room(f'bus_{bus_id}')
            logger.info(f'Client subscribed to bus {bus_id}')
    
    @socketio.on('unsubscribe_bus', namespace='/tracking')
    def handle_unsubscribe(data):
        bus_id = data.get('bus_id')
        if bus_id:
            leave_room(f'bus_{bus_id}')
            logger.info(f'Client unsubscribed from bus {bus_id}')
