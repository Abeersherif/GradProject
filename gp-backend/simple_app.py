"""
Simple MedTwin Flask Backend - No Database Version
Quick start for testing frontend integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import secrets
import json
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# In-memory storage (for testing only)
users = {}
user_id_counter = 1

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'Welcome to MedTwin API',
        'status': 'running',
        'version': '1.0.0-simple'
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'MedTwin Backend is running!',
        'version': '1.0.0-simple'
    }), 200

@app.route('/api/auth/register/patient', methods=['POST'])
def register_patient():
    global user_id_counter
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('fullName') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Full name, email, and password are required'}), 400
        
        # Check if email already exists
        if any(u['email'] == data['email'] for u in users.values()):
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        user_id = user_id_counter
        user_id_counter += 1
        
        users[user_id] = {
            'id': user_id,
            'role': 'patient',
            'fullName': data.get('fullName'),
            'email': data.get('email'),
            'password': data.get('password'),  # In production, hash this!
            'dob': data.get('dob'),
            'gender': data.get('gender'),
            'phone': data.get('phone'),
            'height': data.get('height'),
            'weight': data.get('weight'),
            'conditionCategory': data.get('conditionCategory'),
            'diabetesType': data.get('diabetesType'),
            'insulin': data.get('insulin'),
            'hba1c': data.get('hba1c'),
            'lastGlucose': data.get('lastGlucose'),
            'endocrinologist': data.get('endocrinologist'),
            'cardiacType': data.get('cardiacType'),
            'cardiologist': data.get('cardiologist'),
            'lastEcgDate': data.get('lastEcgDate'),
            'cardiacMeds': data.get('cardiacMeds'),
            'conditions': data.get('conditions'),
            'createdAt': datetime.now().isoformat()
        }
        
        # Generate a simple token
        access_token = secrets.token_urlsafe(32)
        
        print(f"✅ Patient registered: {data.get('fullName')} ({data.get('email')})")
        
        return jsonify({
            'ok': True,
            'patientId': f'P-{user_id}',
            'userId': user_id,
            'access_token': access_token,
            'message': 'Patient registered successfully'
        }), 201
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/register/doctor', methods=['POST'])
def register_doctor():
    global user_id_counter
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('fullName') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Full name, email, and password are required'}), 400
        
        # Check if email already exists
        if any(u['email'] == data['email'] for u in users.values()):
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        user_id = user_id_counter
        user_id_counter += 1
        
        users[user_id] = {
            'id': user_id,
            'role': 'doctor',
            'fullName': data.get('fullName'),
            'email': data.get('email'),
            'password': data.get('password'),
            'license': data.get('license'),
            'specialty': data.get('specialty'),
            'organization': data.get('organization'),
            'phone': data.get('phone'),
            'createdAt': datetime.now().isoformat()
        }
        
        # Generate a simple token
        access_token = secrets.token_urlsafe(32)
        
        print(f"✅ Doctor registered: {data.get('fullName')} ({data.get('email')})")
        
        return jsonify({
            'ok': True,
            'doctorId': f'D-{user_id}',
            'userId': user_id,
            'access_token': access_token,
            'message': 'Doctor registered successfully'
        }), 201
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = next((u for u in users.values() if u['email'] == email), None)
        
        if not user or user['password'] != password:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token
        access_token = secrets.token_urlsafe(32)
        
        return jsonify({
            'ok': True,
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'fullName': user['fullName'],
                'email': user['email'],
                'role': user['role']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Debug endpoint to see registered users"""
    return jsonify({
        'count': len(users),
        'users': list(users.values())
    }), 200

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🏥 MedTwin Simple Backend Starting...")
    print("="*50)
    print(f"📍 Running on: http://localhost:5000")
    print(f"🔧 Mode: Development (In-Memory Storage)")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
