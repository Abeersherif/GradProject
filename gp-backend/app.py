"""
MedTwin Flask Backend
Main application file
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# Import database instance
from database import db

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///medtwin.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT Configuration
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 604800 # 7 days
app.config['PROPAGATE_EXCEPTIONS'] = True

# Initialize extensions
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins for development
jwt = JWTManager(app)

@jwt.invalid_token_loader
def my_invalid_token_callback(expired_token):
    print(f"[JWT DEBUG] Invalid token: {expired_token}")
    return jsonify({"error": "Invalid token", "detail": expired_token}), 422

@jwt.unauthorized_loader
def my_unauthorized_callback(reason):
    print(f"[JWT DEBUG] Unauthorized: {reason}")
    return jsonify({"error": "Unauthorized", "detail": reason}), 401

@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    print(f"[JWT DEBUG] Expired token: {jwt_payload}")
    return jsonify({"error": "Token expired", "detail": "Token has expired"}), 401

@app.before_request
def log_request_info():
    if request.path.startswith('/api/'):
        print(f"[DEBUG] Request to {request.path}")
        print(f"[DEBUG] Headers: {dict(request.headers)}")
        # Don't print body for auth/login to avoid leaking passwords
        if 'login' not in request.path:
            try:
                print(f"[DEBUG] Body: {request.get_data().decode('utf-8')[:1000]}")
            except:
                pass

db.init_app(app)

# Import models (after db initialization)
from models.user import User
from models.consultation import Consultation
from models.ticket import Ticket
from models.medication import Medication

# Import routes
from routes.auth import auth_bp
from routes.consultation import consultation_bp
from routes.notification import notification_bp
from routes.medication import medication_bp
from routes.doctor import doctor_bp
from routes.patient_export import patient_export_bp
from routes.agents import agents_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(consultation_bp, url_prefix='/api/consultation')
app.register_blueprint(notification_bp, url_prefix='/api/notification')
app.register_blueprint(medication_bp, url_prefix='/api/medications')
app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
app.register_blueprint(patient_export_bp, url_prefix='/api/patient')
app.register_blueprint(agents_bp, url_prefix='/api/agents')


# Create database tables
with app.app_context():
    db.create_all()
    print("[OK] Database tables created successfully!")

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'MedTwin Backend is running!',
        'version': '1.0.0'
    }), 200

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'Welcome to MedTwin API',
        'endpoints': {
            'health': '/api/health',
            'auth': '/api/auth/*',
            'consultation': '/api/consultation/*'
        }
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"\n[MedTwin Backend Starting...]")
    print(f"[Running on: http://localhost:{port}]")
    print(f"[Debug mode: {debug}]\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
