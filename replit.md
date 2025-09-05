# Consent Management System

## Overview
A Flask-based medical consent form management system that enables healthcare providers to upload, send, and track consent forms through multiple delivery channels. The system provides a complete workflow from form upload to signature completion with comprehensive audit trails.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask with blueprint-based modular architecture
- **ORM**: SQLAlchemy with declarative base model pattern
- **Database**: SQLite for local development (designed to support PostgreSQL)
- **File Storage**: Local filesystem with organized directory structure (`uploads/` and `signed/`)
- **Service Layer**: Dedicated service classes for business logic separation

### Frontend Architecture
- **Template Engine**: Jinja2 with base template inheritance
- **CSS Framework**: Bootstrap 5 with Replit's dark theme integration
- **JavaScript**: jQuery for AJAX interactions and DOM manipulation
- **File Upload**: Drag-and-drop interface with client-side validation

### Data Model Design
- **Consent**: Core entity tracking patient information, form status, and timestamps
- **Transmission**: Audit trail for delivery attempts with method and status tracking
- **Enums**: Type-safe status management (ConsentStatus, DeliveryMethod, TransmissionStatus)

### API Structure
- RESTful endpoints organized by blueprint modules
- Separation of concerns: main (UI), upload (file handling), consent (business logic)
- JSON-based API responses with proper error handling

### File Management Strategy
- Secure filename handling with duplicate prevention
- Organized storage separation (uploads vs signed documents)
- File validation and size restrictions (16MB PDF limit)

### Security Considerations
- CSRF protection through Flask's secret key configuration
- Secure filename sanitization
- File type validation (PDF only)
- Proxy-aware configuration for deployment flexibility

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web application framework
- **SQLAlchemy**: Database ORM and query builder
- **Werkzeug**: WSGI utilities and secure filename handling

### Frontend Dependencies
- **Bootstrap 5**: UI component library and responsive design
- **jQuery**: JavaScript library for DOM manipulation and AJAX
- **Font Awesome**: Icon library for UI enhancement

### Development Tools
- **Python unittest**: Testing framework for unit tests
- **Logging**: Built-in Python logging for debugging and monitoring

### Simulated Integrations
- **DocuSeal**: Signature completion workflow (mocked for testing)
- **Email/SMS/Fax**: Multi-channel delivery simulation (ready for real service integration)

### Future Integration Points
- Database migration path to PostgreSQL
- Real email service integration (AWS SES, SendGrid)
- SMS service integration (AWS Pinpoint, Twilio)
- Fax service integration
- Document signing service (DocuSign, Adobe Sign)