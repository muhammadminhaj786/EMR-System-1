// Main JavaScript file for Consent Management System

// Global variables
let currentUploadedFile = null;
let currentConsent = null;

function initializeUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    
    // Drag and drop events
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // File input change event
    fileInput.addEventListener('change', handleFileSelect);
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

function uploadFile(file) {
    // Validate file type
    if (file.type !== 'application/pdf') {
        showAlert('error', 'Only PDF files are allowed.');
        return;
    }
    
    // Validate file size (16MB limit)
    if (file.size > 16 * 1024 * 1024) {
        showAlert('error', 'File size must be less than 16MB.');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showUploadStatus(true);
    
    $.ajax({
        url: '/api/upload',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            showUploadStatus(false);
            currentUploadedFile = response;
            showPDFPreview(file.name);
            showAlert('success', 'File uploaded successfully!');
        },
        error: function(xhr) {
            showUploadStatus(false);
            const error = xhr.responseJSON ? xhr.responseJSON.error : 'Upload failed';
            showAlert('error', error);
        }
    });
}

function showUploadStatus(show) {
    $('#upload-status').toggle(show);
}

function showPDFPreview(filename) {
    $('#pdf-filename').text(filename);
    $('#pdf-preview').show();
}

function setupEventListeners() {
    // Send consent button
    $('#send-consent-btn').click(function() {
        sendConsent();
    });
    
    // Delivery method change
    $('#delivery-method').change(function() {
        updateRecipientField();
    });
    
    // Auto-populate recipient field based on delivery method
    function updateRecipientField() {
        const method = $('#delivery-method').val();
        const recipientField = $('#recipient');
        const recipientHelp = $('#recipient-help');
        
        switch(method) {
            case 'email':
                recipientField.attr('type', 'email');
                recipientField.attr('placeholder', 'patient@example.com');
                recipientHelp.text('Enter patient email address');
                break;
            case 'sms':
                recipientField.attr('type', 'tel');
                recipientField.attr('placeholder', '+1234567890');
                recipientHelp.text('Enter patient phone number');
                break;
            case 'fax':
                recipientField.attr('type', 'text');
                recipientField.attr('placeholder', '+1234567890');
                recipientHelp.text('Enter patient fax number');
                break;
            default:
                recipientField.attr('type', 'text');
                recipientField.attr('placeholder', '');
                recipientHelp.text('');
        }
    }
}

function sendConsent() {
    if (!currentUploadedFile) {
        showAlert('error', 'Please upload a file first.');
        return;
    }
    
    const formData = {
        patient_name: $('#patient-name').val(),
        patient_email: $('#patient-email').val(),
        patient_phone: $('#patient-phone').val(),
        patient_fax: $('#patient-fax').val(),
        form_name: currentUploadedFile.filename,
        file_path: currentUploadedFile.file_path
    };
    
    // Validate required fields
    if (!formData.patient_name) {
        showAlert('error', 'Patient name is required.');
        return;
    }
    
    const deliveryMethod = $('#delivery-method').val();
    const recipient = $('#recipient').val();
    
    if (!deliveryMethod || !recipient) {
        showAlert('error', 'Delivery method and recipient are required.');
        return;
    }
    
    // Create consent first
    $.ajax({
        url: '/api/consents',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(consent) {
            currentConsent = consent;
            
            // Now send the consent
            $.ajax({
                url: `/api/consents/${consent.id}/send`,
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    delivery_method: deliveryMethod,
                    recipient: recipient
                }),
                success: function(transmission) {
                    $('#sendModal').modal('hide');
                    resetForm();
                    showAlert('success', `Consent sent successfully via ${deliveryMethod}!`);
                    loadDashboardData();
                },
                error: function(xhr) {
                    const error = xhr.responseJSON ? xhr.responseJSON.error : 'Failed to send consent';
                    showAlert('error', error);
                }
            });
        },
        error: function(xhr) {
            const error = xhr.responseJSON ? xhr.responseJSON.error : 'Failed to create consent';
            showAlert('error', error);
        }
    });
}

function resetForm() {
    $('#send-form')[0].reset();
    $('#pdf-preview').hide();
    currentUploadedFile = null;
    currentConsent = null;
    document.getElementById('file-input').value = '';
}

function loadDashboardData() {
    loadOutgoingConsents();
    loadReceivedConsents();
    loadTransmissionHistory();
}

function loadOutgoingConsents() {
    $.ajax({
        url: '/api/consents?status=sent',
        type: 'GET',
        success: function(consents) {
            populateConsentTable('outgoing', consents, true);
            $('#outgoing-count').text(consents.length);
        },
        error: function(xhr) {
            console.error('Failed to load outgoing consents:', xhr);
        }
    });
}

function loadReceivedConsents() {
    $.ajax({
        url: '/api/consents?status=signed',
        type: 'GET',
        success: function(consents) {
            populateConsentTable('received', consents, false);
            $('#received-count').text(consents.length);
        },
        error: function(xhr) {
            console.error('Failed to load received consents:', xhr);
        }
    });
}

function loadTransmissionHistory() {
    // Load all consents and their transmissions
    $.ajax({
        url: '/api/consents',
        type: 'GET',
        success: function(consents) {
            const allTransmissions = [];
            let loadCount = 0;
            
            if (consents.length === 0) {
                populateHistoryTable([]);
                return;
            }
            
            consents.forEach(consent => {
                $.ajax({
                    url: `/api/consents/${consent.id}/history`,
                    type: 'GET',
                    success: function(transmissions) {
                        transmissions.forEach(transmission => {
                            transmission.patient_name = consent.patient_name;
                        });
                        allTransmissions.push(...transmissions);
                        loadCount++;
                        
                        if (loadCount === consents.length) {
                            // Sort by date descending
                            allTransmissions.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
                            populateHistoryTable(allTransmissions);
                        }
                    },
                    error: function(xhr) {
                        console.error(`Failed to load history for consent ${consent.id}:`, xhr);
                        loadCount++;
                        if (loadCount === consents.length) {
                            populateHistoryTable(allTransmissions);
                        }
                    }
                });
            });
        },
        error: function(xhr) {
            console.error('Failed to load consents for history:', xhr);
        }
    });
}

function populateConsentTable(tableType, consents, includeActions) {
    const tableBody = $(`#${tableType}-table tbody`);
    const emptyRow = $(`#${tableType}-empty`);
    
    // Clear existing rows except empty row
    tableBody.find('tr:not(#' + tableType + '-empty)').remove();
    
    if (consents.length === 0) {
        emptyRow.show();
        return;
    }
    
    emptyRow.hide();
    
    consents.forEach(consent => {
        const row = $('<tr></tr>');
        
        row.append(`<td>${escapeHtml(consent.patient_name)}</td>`);
        row.append(`<td>${escapeHtml(consent.form_name)}</td>`);
        row.append(`<td>${formatDate(consent.sent_at)}</td>`);
        
        if (tableType === 'received') {
            row.append(`<td>${formatDate(consent.signed_at)}</td>`);
        }
        
        row.append(`<td><span class="badge bg-${getStatusColor(consent.status)}">${consent.status}</span></td>`);
        
        if (includeActions) {
            const actionsCell = $('<td></td>');
            const simulateBtn = $(`
                <button type="button" class="btn btn-sm btn-outline-success" onclick="simulateSignature(${consent.id})">
                    <i class="fas fa-signature me-1"></i>Simulate Sign
                </button>
            `);
            actionsCell.append(simulateBtn);
            row.append(actionsCell);
        }
        
        tableBody.append(row);
    });
}

function populateHistoryTable(transmissions) {
    const tableBody = $('#history-table tbody');
    const emptyRow = $('#history-empty');
    
    // Clear existing rows except empty row
    tableBody.find('tr:not(#history-empty)').remove();
    
    if (transmissions.length === 0) {
        emptyRow.show();
        return;
    }
    
    emptyRow.hide();
    
    transmissions.forEach(transmission => {
        const row = $('<tr></tr>');
        
        row.append(`<td><i class="fas fa-${getMethodIcon(transmission.method)} me-2"></i>${transmission.method.toUpperCase()}</td>`);
        row.append(`<td>${escapeHtml(transmission.recipient)}</td>`);
        row.append(`<td>${formatDate(transmission.created_at)}</td>`);
        row.append(`<td><span class="badge bg-${getStatusColor(transmission.status)}">${transmission.status}</span></td>`);
        
        tableBody.append(row);
    });
}

function simulateSignature(consentId) {
    if (!confirm('Are you sure you want to simulate signature completion for this consent?')) {
        return;
    }
    
    $.ajax({
        url: `/api/simulate-sign/${consentId}`,
        type: 'POST',
        success: function(response) {
            showAlert('success', 'Signature completed successfully!');
            loadDashboardData();
        },
        error: function(xhr) {
            const error = xhr.responseJSON ? xhr.responseJSON.error : 'Failed to complete signature';
            showAlert('error', error);
        }
    });
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function getStatusColor(status) {
    const statusColors = {
        'draft': 'secondary',
        'sent': 'warning',
        'signed': 'success',
        'expired': 'danger',
        'pending': 'info',
        'delivered': 'success',
        'failed': 'danger'
    };
    return statusColors[status] || 'secondary';
}

function getMethodIcon(method) {
    const methodIcons = {
        'email': 'envelope',
        'sms': 'mobile-alt',
        'fax': 'fax'
    };
    return methodIcons[method] || 'paper-plane';
}

function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

function showAlert(type, message) {
    // Remove existing alerts
    $('.alert-custom').remove();
    
    const alertClass = type === 'error' ? 'alert-danger' : `alert-${type}`;
    const iconClass = type === 'error' ? 'fas fa-exclamation-circle' : 
                     type === 'success' ? 'fas fa-check-circle' : 'fas fa-info-circle';
    
    const alert = $(`
        <div class="alert ${alertClass} alert-dismissible fade show alert-custom" role="alert" style="position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
            <i class="${iconClass} me-2"></i>
            ${escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('body').append(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.alert('close');
    }, 5000);
}
