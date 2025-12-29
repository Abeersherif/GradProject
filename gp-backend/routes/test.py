"""
Test routes - no authentication required
For debugging purposes only
"""

from flask import Blueprint, jsonify

test_bp = Blueprint('test', __name__)

@test_bp.route('/ping', methods=['GET'])
def ping():
    """Simple ping endpoint"""
    return jsonify({'ok': True, 'message': 'Backend is running!'}), 200

@test_bp.route('/echo', methods=['POST'])
def echo():
    """Echo back the request"""
    from flask import request
    return jsonify({
        'ok': True,
        'headers': dict(request.headers),
        'body': request.get_json()
    }), 200
