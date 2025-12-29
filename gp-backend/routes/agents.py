"""
Agent Routes for MedTwin
Handles AI agent interactions including lab results interpretation
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from agents import get_lab_results_agent

agents_bp = Blueprint('agents', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'txt'}
UPLOAD_FOLDER = 'uploads/lab_results'

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@agents_bp.route('/lab-results/interpret', methods=['POST'])
# @jwt_required()  # Uncomment when JWT is fully implemented
def interpret_lab_results():
    """
    Upload a lab document (PDF, image, or text) for OCR analysis and medical interpretation.
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: PDF, PNG, JPG, JPEG, TXT'}), 400
        
        # Read file content
        content = file.read()
        
        # Get lab results agent
        lab_agent = get_lab_results_agent()
        
        # Analyze document using LabResultsAgent
        result = lab_agent.analyze_document(content, file.filename, file.content_type)
        
        # Check if analysis was successful
        if result.get("status") == "error":
            return jsonify({
                'error': result.get("message"),
                'tip': result.get("tip", "Please try uploading a text file")
            }), 400
        
        return jsonify({
            'ok': True,
            'interpretation': result.get('interpretation', ''),
            'abnormal_values': result.get('abnormal_values', []),
            'recommendations': result.get('recommendations', ''),
            'follow_up_required': result.get('follow_up_required', False),
            'follow_up_message': result.get('follow_up_message', ''),
            'extracted_text_length': len(result.get('extracted_text', ''))
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Lab results interpretation failed: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({'error': f'Failed to process document: {str(e)}'}), 500
