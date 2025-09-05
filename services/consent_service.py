import logging
from datetime import datetime
from models import Consent, Transmission, ConsentStatus, DeliveryMethod, TransmissionStatus
from services.file_service import FileService
from app import db

logger = logging.getLogger(__name__)

class ConsentService:
    """Service for handling consent operations"""
    
    @staticmethod
    def send_consent(consent, method, recipient):
        """Send consent form to patient via specified method"""
        try:
            # Create transmission record
            transmission = Transmission()
            transmission.consent_id = consent.id
            transmission.method = method
            transmission.recipient = recipient
            transmission.status = TransmissionStatus.PENDING
            
            db.session.add(transmission)
            
            # Update consent status and sent timestamp
            consent.status = ConsentStatus.SENT
            consent.sent_at = datetime.utcnow()
            
            # Simulate sending (in real implementation, this would integrate with actual services)
            transmission.status = TransmissionStatus.SENT
            transmission.sent_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Consent {consent.id} sent via {method.value} to {recipient}")
            
            return transmission
            
        except Exception as e:
            logger.error(f"Error sending consent: {str(e)}")
            db.session.rollback()
            raise
    
    @staticmethod
    def complete_signature(consent):
        """Complete the signature process for a consent"""
        try:
            # Move file to signed directory
            signed_path = FileService.move_to_signed(consent.file_path, consent.id)
            
            # Update consent record
            consent.status = ConsentStatus.SIGNED
            consent.signed_at = datetime.utcnow()
            consent.signed_file_path = signed_path
            
            # Update any pending transmissions to delivered
            for transmission in consent.transmissions:
                if transmission.status == TransmissionStatus.SENT:
                    transmission.status = TransmissionStatus.DELIVERED
                    transmission.delivered_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Signature completed for consent {consent.id}")
            
            return consent
            
        except Exception as e:
            logger.error(f"Error completing signature: {str(e)}")
            db.session.rollback()
            raise
    
    @staticmethod
    def get_outgoing_consents():
        """Get all consents that have been sent but not signed"""
        return Consent.query.filter(Consent.status == ConsentStatus.SENT).all()
    
    @staticmethod
    def get_received_consents():
        """Get all consents that have been signed"""
        return Consent.query.filter(Consent.status == ConsentStatus.SIGNED).all()
    
    @staticmethod
    def get_transmission_history():
        """Get all transmission attempts"""
        return Transmission.query.order_by(Transmission.created_at.desc()).all()
