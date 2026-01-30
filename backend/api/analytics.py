"""
API routes for analytics and demand forecasting
"""
from flask import Blueprint, request, jsonify
from services.demand_forecasting import DemandForecaster
from services.analytics_service import AnalyticsService
import logging

bp = Blueprint('analytics', __name__)
logger = logging.getLogger(__name__)

analytics_service = AnalyticsService()
demand_forecaster = DemandForecaster()

@bp.route('/efficiency', methods=['GET'])
def get_efficiency_metrics():
    """Get route efficiency metrics"""
    try:
        route_id = request.args.get('route_id', type=int)
        time_period = request.args.get('period', 'week')  # day, week, month
        
        metrics = analytics_service.calculate_efficiency(route_id, time_period)
        
        return jsonify({
            'success': True,
            'metrics': metrics
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating efficiency: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/forecast', methods=['GET'])
def get_demand_forecast():
    """
    Get demand forecast for stops
    Query params: stop_id, days_ahead (default: 7)
    """
    try:
        stop_id = request.args.get('stop_id', type=int)
        days_ahead = request.args.get('days_ahead', 7, type=int)
        
        if stop_id:
            forecast = demand_forecaster.predict_for_stop(stop_id, days_ahead)
        else:
            forecast = demand_forecaster.predict_all_stops(days_ahead)
        
        return jsonify({
            'success': True,
            'forecast': forecast
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating forecast: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/fuel-consumption', methods=['GET'])
def get_fuel_consumption():
    """Get fuel consumption analytics"""
    try:
        bus_id = request.args.get('bus_id', type=int)
        time_period = request.args.get('period', 'month')
        
        consumption = analytics_service.calculate_fuel_consumption(bus_id, time_period)
        
        return jsonify({
            'success': True,
            'consumption': consumption
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating fuel consumption: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/delays', methods=['GET'])
def get_delay_analysis():
    """Analyze delays and predict future delays"""
    try:
        route_id = request.args.get('route_id', type=int)
        
        analysis = analytics_service.analyze_delays(route_id)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing delays: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get comprehensive dashboard data"""
    try:
        dashboard_data = {
            'total_buses': analytics_service.get_total_buses(),
            'active_routes': analytics_service.get_active_routes_count(),
            'total_students': analytics_service.get_total_students(),
            'avg_efficiency': analytics_service.get_avg_efficiency(),
            'recent_alerts': analytics_service.get_recent_alerts(),
            'daily_stats': analytics_service.get_daily_stats()
        }
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/optimization-history', methods=['GET'])
def get_optimization_history():
    """Get history of optimization runs"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        history = analytics_service.get_optimization_history(limit)
        
        return jsonify({
            'success': True,
            'history': history
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching optimization history: {str(e)}")
        return jsonify({'error': str(e)}), 500
