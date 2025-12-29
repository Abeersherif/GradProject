"""
Notification routes for MedTwin
Handles medication reminders and Google Calendar integration
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from database import db
from utils.google_calendar import calendar_service

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/calendar/connect', methods=['GET'])
@jwt_required()
def get_calendar_auth_url():
    """
    Get Google Calendar authorization URL for user
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate authorization URL
        result = calendar_service.get_authorization_url(user.email)
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify({
            'ok': True,
            'authorization_url': result['authorization_url'],
            'state': result['state']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/calendar/callback', methods=['POST'])
def handle_calendar_callback():
    """
    Handle OAuth callback from Google
    """
    try:
        data = request.get_json()
        code = data.get('code')
        user_email = data.get('email')
        
        if not code or not user_email:
            return jsonify({'error': 'Missing code or email'}), 400
        
        # Handle OAuth callback
        result = calendar_service.handle_oauth_callback(code, user_email)
        
        if result.get('success'):
            return jsonify({
                'ok': True,
                'message': result['message']
            }), 200
        else:
            return jsonify({
                'ok': False,
                'error': result.get('error'),
                'message': result.get('message')
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/calendar/status', methods=['GET'])
@jwt_required()
def check_calendar_status():
    """
    Check if user has connected Google Calendar
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        status = calendar_service.check_calendar_connection(user.email)
        
        return jsonify({
            'ok': True,
            'connected': status['connected'],
            'message': status['message']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/medication/add-reminders', methods=['POST'])
@jwt_required()
def add_medication_reminders():
    """
    Create Google Calendar reminders for a medication
    
    Request body:
    {
        "medication": {
            "name": "Aspirin",
            "dosage": "81mg",
            "timing": ["08:00", "20:00"],
            "instructions": "Take with food"
        },
        "num_days": 30
    }
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        medication = data.get('medication')
        num_days = data.get('num_days', 30)
        
        if not medication:
            return jsonify({'error': 'Medication data required'}), 400
        
        # Create calendar reminders
        result = calendar_service.create_medication_reminders(
            user.email,
            medication,
            num_days
        )
        
        if result.get('success'):
            return jsonify({
                'ok': True,
                'message': result['message'],
                'events': result.get('events', [])
            }), 201
        else:
            return jsonify({
                'ok': False,
                'error': result.get('error'),
                'message': result.get('message')
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/medication/remove-reminders', methods=['POST'])
@jwt_required()
def remove_medication_reminders():
    """
    Delete medication reminders from Google Calendar
    
    Request body:
    {
        "event_ids": ["event_id_1", "event_id_2"]
    }
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        event_ids = data.get('event_ids', [])
        
        if not event_ids:
            return jsonify({'error': 'Event IDs required'}), 400
        
        # Delete reminders
        result = calendar_service.delete_medication_reminders(
            user.email,
            event_ids
        )
        
        if result.get('success'):
            return jsonify({
                'ok': True,
                'message': result['message'],
                'deleted_count': result.get('deleted_count', 0)
            }), 200
        else:
            return jsonify({
                'ok': False,
                'error': result.get('error')
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
