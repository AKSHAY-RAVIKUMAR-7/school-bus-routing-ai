"""
API routes for Explainable AI (XAI) features
"""
from flask import Blueprint, request, jsonify
from services.xai_service import XAIService
import logging

bp = Blueprint('xai', __name__)
logger = logging.getLogger(__name__)

xai_service = XAIService()

@bp.route('/explain/route/<int:route_id>', methods=['GET'])
def explain_route(route_id):
    """
    Explain why a specific route was generated
    Uses SHAP values to show feature importance
    """
    try:
        explanation = xai_service.explain_route_decision(route_id)
        
        return jsonify({
            'success': True,
            'route_id': route_id,
            'explanation': explanation
        }), 200
        
    except Exception as e:
        logger.error(f"Error explaining route: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/explain/optimization', methods=['POST'])
def explain_optimization():
    """
    Explain optimization decision using SHAP/LIME
    
    Request body:
    {
        "optimization_id": 123,
        "method": "shap|lime"
    }
    """
    try:
        data = request.json
        optimization_id = data.get('optimization_id')
        method = data.get('method', 'shap')
        
        if method == 'shap':
            explanation = xai_service.generate_shap_explanation(optimization_id)
        elif method == 'lime':
            explanation = xai_service.generate_lime_explanation(optimization_id)
        else:
            return jsonify({'error': 'Invalid explanation method'}), 400
        
        return jsonify({
            'success': True,
            'method': method,
            'explanation': explanation
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/feature-importance', methods=['GET'])
def get_feature_importance():
    """Get global feature importance for route optimization"""
    try:
        model_type = request.args.get('model', 'genetic')  # genetic, rl, dl
        
        importance = xai_service.get_feature_importance(model_type)
        
        return jsonify({
            'success': True,
            'model': model_type,
            'features': importance
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating feature importance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/decision-tree', methods=['GET'])
def get_decision_tree():
    """Get surrogate decision tree for interpretability"""
    try:
        route_id = request.args.get('route_id', type=int)
        
        tree = xai_service.generate_decision_tree_surrogate(route_id)
        
        return jsonify({
            'success': True,
            'tree': tree
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating decision tree: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/counterfactual', methods=['POST'])
def generate_counterfactual():
    """
    Generate counterfactual explanation
    "What would need to change for a different route?"
    
    Request body:
    {
        "current_route_id": 123,
        "desired_outcome": {"distance": 45, "time": 60}
    }
    """
    try:
        data = request.json
        
        counterfactual = xai_service.generate_counterfactual(
            current_route_id=data['current_route_id'],
            desired_outcome=data['desired_outcome']
        )
        
        return jsonify({
            'success': True,
            'counterfactual': counterfactual
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating counterfactual: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/model-confidence', methods=['GET'])
def get_model_confidence():
    """Get model confidence scores for predictions"""
    try:
        prediction_type = request.args.get('type', 'route')  # route, demand, delay
        
        confidence = xai_service.calculate_confidence(prediction_type)
        
        return jsonify({
            'success': True,
            'type': prediction_type,
            'confidence': confidence
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating confidence: {str(e)}")
        return jsonify({'error': str(e)}), 500
