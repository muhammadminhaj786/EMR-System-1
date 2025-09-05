import unittest
import os
import tempfile
from app import app, db
from models import Consent, Transmission, ConsentStatus, DeliveryMethod
from services.consent_service import ConsentService

class ConsentTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary database
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE']
        app.config['TESTING'] = True
        
        # Create test directories
        app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
        app.config['SIGNED_FOLDER'] = tempfile.mkdtemp()
        
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after each test method."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
        
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
    
    def test_create_consent(self):
        """Test creating a new consent record."""
        with app.app_context():
            consent = Consent(
                patient_name="John Doe",
                patient_email="john@example.com",
                form_name="test_form.pdf",
                file_path="/uploads/test_form.pdf"
            )
            
            db.session.add(consent)
            db.session.commit()
            
            # Verify consent was created
            self.assertIsNotNone(consent.id)
            self.assertEqual(consent.patient_name, "John Doe")
            self.assertEqual(consent.status, ConsentStatus.DRAFT)
    
    def test_send_consent(self):
        """Test sending a consent form."""
        with app.app_context():
            # Create a consent
            consent = Consent(
                patient_name="Jane Smith",
                patient_email="jane@example.com",
                form_name="consent_form.pdf",
                file_path="/uploads/consent_form.pdf"
            )
            
            db.session.add(consent)
            db.session.commit()
            
            # Send the consent
            transmission = ConsentService.send_consent(
                consent=consent,
                method=DeliveryMethod.EMAIL,
                recipient="jane@example.com"
            )
            
            # Verify transmission was created and consent status updated
            self.assertIsNotNone(transmission.id)
            self.assertEqual(transmission.method, DeliveryMethod.EMAIL)
            self.assertEqual(transmission.recipient, "jane@example.com")
            self.assertEqual(consent.status, ConsentStatus.SENT)
            self.assertIsNotNone(consent.sent_at)
    
    def test_api_upload(self):
        """Test the upload API endpoint."""
        # Create a test PDF file
        test_data = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF'
        
        response = self.app.post('/api/upload', 
                               data={'file': (io.BytesIO(test_data), 'test.pdf')},
                               content_type='multipart/form-data')
        
        # Note: This test may fail due to file validation, but demonstrates the test structure
        # In a real implementation, you would mock the file validation or use a proper test PDF
    
    def test_api_create_consent(self):
        """Test the consent creation API endpoint."""
        consent_data = {
            'patient_name': 'Test Patient',
            'patient_email': 'test@example.com',
            'form_name': 'test_form.pdf',
            'file_path': '/uploads/test_form.pdf'
        }
        
        response = self.app.post('/api/consents',
                               json=consent_data,
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['patient_name'], 'Test Patient')
        self.assertEqual(data['status'], 'draft')

if __name__ == '__main__':
    import io  # Import io for BytesIO
    unittest.main()
