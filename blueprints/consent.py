import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from models import Consent, Transmission, ConsentStatus, DeliveryMethod, TransmissionStatus
from services.consent_service import ConsentService
from app import db

consent_bp = Blueprint('consent', __name__)
logger = logging.getLogger(__name__)

@consent_bp.route('/consents', methods=['POST'])
def create_consent():
    """Create a new consent form entry"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['patient_name', 'form_name', 'file_path']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create consent record
        consent = Consent(
            patient_name=data['patient_name'],
            patient_email=data.get('patient_email'),
            patient_phone=data.get('patient_phone'),
            patient_fax=data.get('patient_fax'),
            form_name=data['form_name'],
            file_path=data['file_path']
        )
        
        db.session.add(consent)
        db.session.commit()
        
        logger.info(f"Consent created: {consent.id}")
        return jsonify(consent.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating consent: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create consent'}), 500

@consent_bp.route('/consents/<int:consent_id>/send', methods=['POST'])
def send_consent(consent_id):
    """Send a consent form to patient"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('delivery_method') or not data.get('recipient'):
            return jsonify({'error': 'delivery_method and recipient are required'}), 400
        
        # Get consent
        consent = Consent.query.get_or_404(consent_id)
        
        # Create transmission record
        transmission = ConsentService.send_consent(
            consent=consent,
            method=DeliveryMethod(data['delivery_method']),
            recipient=data['recipient']
        )
        
        return jsonify(transmission.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error sending consent: {str(e)}")
        return jsonify({'error': 'Failed to send consent'}), 500

@consent_bp.route('/consents', methods=['GET'])
def get_consents():
    """Get all consents with optional status filter"""
    try:
        status_filter = request.args.get('status')
        
        query = Consent.query
        if status_filter:
            query = query.filter(Consent.status == ConsentStatus(status_filter))
        
        consents = query.order_by(Consent.created_at.desc()).all()
        
        return jsonify([consent.to_dict() for consent in consents]), 200
        
    except Exception as e:
        logger.error(f"Error fetching consents: {str(e)}")
        return jsonify({'error': 'Failed to fetch consents'}), 500

@consent_bp.route('/consents/<int:consent_id>/history', methods=['GET'])
def get_consent_history(consent_id):
    """Get transmission history for a consent"""
    try:
        consent = Consent.query.get_or_404(consent_id)
        transmissions = Transmission.query.filter_by(consent_id=consent_id)\
                                         .order_by(Transmission.created_at.desc()).all()
        
        return jsonify([transmission.to_dict() for transmission in transmissions]), 200
        
    except Exception as e:
        logger.error(f"Error fetching consent history: {str(e)}")
        return jsonify({'error': 'Failed to fetch history'}), 500

@consent_bp.route('/simulate-sign/<int:consent_id>', methods=['POST'])
def simulate_signature(consent_id):
    """Simulate DocuSeal signature completion"""
    try:
        consent = Consent.query.get_or_404(consent_id)
        
        # Simulate signature completion
        signed_consent = ConsentService.complete_signature(consent)
        
        return jsonify({
            'message': 'Signature completed successfully',
            'consent': signed_consent.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error simulating signature: {str(e)}")
        return jsonify({'error': 'Failed to complete signature'}), 500

@consent_bp.route('/docuseal-callback', methods=['POST'])
def docuseal_callback():
    """Mock DocuSeal webhook callback"""
    try:
        data = request.get_json()
        logger.info(f"DocuSeal callback received: {data}")
        
        # In a real implementation, this would process the DocuSeal webhook
        # For now, just log and return success
        
        return jsonify({'status': 'received'}), 200
        
    except Exception as e:
        logger.error(f"Error processing DocuSeal callback: {str(e)}")
        return jsonify({'error': 'Callback processing failed'}), 500
