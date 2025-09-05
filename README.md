# Consent Management System

A Flask-based medical consent form management system with drag-and-drop uploads, patient tracking, and simulated signature workflow.

## Features

- **Drag & Drop Upload**: Upload PDF consent forms with intuitive drag-and-drop interface
- **Patient Management**: Track patient information including name, email, phone, and fax
- **Multi-Channel Delivery**: Send consent forms via Email, SMS, or Fax
- **Status Tracking**: Monitor consent forms in Outgoing (sent but not signed) and Received (signed) states
- **Transmission History**: Complete audit trail of all delivery attempts
- **Signature Simulation**: Mock DocuSeal integration for testing signature completion
- **Responsive Design**: Bootstrap-based UI that works on desktop and mobile

## Technology Stack

- **Backend**: Flask, SQLAlchemy, SQLite
- **Frontend**: HTML5, Bootstrap 5, jQuery
- **File Storage**: Local filesystem (uploads/ and signed/ directories)
- **Database**: SQLite for demo purposes
- **Testing**: Python unittest framework

## Project Structure

