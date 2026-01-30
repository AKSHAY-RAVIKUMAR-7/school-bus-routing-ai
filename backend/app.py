"""
Main Flask Application for School Bus Routing System
"""
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from config.settings import Config
from api import routes, tracking, analytics, xai
from database.connection import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app)
    
    # Initialize SocketIO for real-time updates
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Initialize database
    init_db()
    
    # Register blueprints
    app.register_blueprint(routes.bp, url_prefix='/api/routes')
    app.register_blueprint(tracking.bp, url_prefix='/api/tracking')
    app.register_blueprint(analytics.bp, url_prefix='/api/analytics')
    app.register_blueprint(xai.bp, url_prefix='/api/xai')
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'School Bus Routing System'}
    
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
