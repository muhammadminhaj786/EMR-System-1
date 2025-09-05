from datetime import datetime
from app import db
from sqlalchemy import String, Integer, DateTime, Enum as SQLEnum, Text
from enum import Enum

class ConsentStatus(Enum):
    DRAFT = "draft"
    SENT = "sent"
    SIGNED = "signed"
    EXPIRED = "expired"

class DeliveryMethod(Enum):
    EMAIL = "email"
    SMS = "sms"
    FAX = "fax"

class TransmissionStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"

class Consent(db.Model):
    __tablename__ = 'consents'
    
    id = db.Column(Integer, primary_key=True)
    patient_name = db.Column(String(255), nullable=False)
    patient_email = db.Column(String(255), nullable=True)
    patient_phone = db.Column(String(50), nullable=True)
    patient_fax = db.Column(String(50), nullable=True)
    form_name = db.Column(String(255), nullable=False)
    file_path = db.Column(String(500), nullable=False)
    signed_file_path = db.Column(String(500), nullable=True)
    status = db.Column(SQLEnum(ConsentStatus), default=ConsentStatus.DRAFT, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    sent_at = db.Column(DateTime, nullable=True)
    signed_at = db.Column(DateTime, nullable=True)
    
    # Relationship to transmissions
    transmissions = db.relationship('Transmission', backref='consent', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_name': self.patient_name,
            'patient_email': self.patient_email,
            'patient_phone': self.patient_phone,
            'patient_fax': self.patient_fax,
            'form_name': self.form_name,
            'file_path': self.file_path,
            'signed_file_path': self.signed_file_path,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'signed_at': self.signed_at.isoformat() if self.signed_at else None
        }

class Transmission(db.Model):
    __tablename__ = 'transmissions'
    
    id = db.Column(Integer, primary_key=True)
    consent_id = db.Column(Integer, db.ForeignKey('consents.id'), nullable=False)
    method = db.Column(SQLEnum(DeliveryMethod), nullable=False)
    recipient = db.Column(String(255), nullable=False)  # email, phone, or fax number
    status = db.Column(SQLEnum(TransmissionStatus), default=TransmissionStatus.PENDING, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    sent_at = db.Column(DateTime, nullable=True)
    delivered_at = db.Column(DateTime, nullable=True)
    error_message = db.Column(Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'consent_id': self.consent_id,
            'method': self.method.value,
            'recipient': self.recipient,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'error_message': self.error_message
        }
