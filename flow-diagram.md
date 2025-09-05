# Consent Management System Flow Diagram

This document illustrates the key workflows in the Consent Management System using Mermaid.js diagrams.

## 1. Upload Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Frontend UI
    participant F as Flask Backend
    participant FS as File System
    participant DB as Database

    U->>UI: Drag & drop PDF file
    UI->>UI: Validate file (PDF, <16MB)
    UI->>F: POST /api/upload (FormData)
    F->>F: Secure filename
    F->>FS: Save to uploads/ directory
    FS-->>F: File path
    F-->>UI: Upload success response
    UI->>UI: Show PDF preview
    UI->>U: Display "Send" button
