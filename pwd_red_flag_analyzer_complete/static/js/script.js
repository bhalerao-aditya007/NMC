// JavaScript for PWD Red Flag Analyzer

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const fileName = document.getElementById('fileName');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const uploadSection = document.getElementById('uploadSection');
    const resultsSection = document.getElementById('resultsSection');

    // File input change handler
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            fileName.textContent = file.name;
            fileName.style.color = '#667eea';
        }
    });

    // Form submit handler
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Validate file
        if (!fileInput.files || fileInput.files.length === 0) {
            showAlert('Please select a file', 'error');
            return;
        }

        // Validate format selection
        const formats = document.querySelectorAll('input[name="formats"]:checked');
        if (formats.length === 0) {
            showAlert('Please select at least one output format', 'error');
            return;
        }

        // Show loading
        loadingOverlay.classList.add('active');

        try {
            // Prepare form data
            const formData = new FormData(uploadForm);

            // Send request
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            // Hide loading
            loadingOverlay.classList.remove('active');

            if (result.success) {
                // Show results
                displayResults(result);
            } else {
                showAlert(result.error || 'Analysis failed', 'error');
            }

        } catch (error) {
            loadingOverlay.classList.remove('active');
            showAlert('Network error: ' + error.message, 'error');
            console.error('Error:', error);
        }
    });
});

function displayResults(result) {
    const uploadSection = document.getElementById('uploadSection');
    const resultsSection = document.getElementById('resultsSection');

    // Hide upload, show results
    uploadSection.style.display = 'none';
    resultsSection.classList.remove('hidden');

    // Display summary
    displaySummary(result.summary);

    // Display data quality
    displayDataQuality(result.data_quality);

    // Display download links
    displayDownloadLinks(result.output_files);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function displaySummary(summary) {
    const summaryGrid = document.getElementById('summaryGrid');
    
    const totalRecords = summary.total_records || 0;
    const redFlagged = summary.red_flagged || 0;
    const greenFlagged = summary.green_flagged || 0;

    const redPercentage = totalRecords > 0 ? (redFlagged / totalRecords * 100).toFixed(1) : 0;
    const greenPercentage = totalRecords > 0 ? (greenFlagged / totalRecords * 100).toFixed(1) : 0;

    summaryGrid.innerHTML = `
        <div class="summary-card total">
            <h3>Total Records</h3>
            <div class="summary-value">${totalRecords}</div>
            <div class="summary-detail">Analyzed</div>
        </div>

        <div class="summary-card red">
            <h3>Red Flagged</h3>
            <div class="summary-value">${redFlagged}</div>
            <div class="summary-detail">${redPercentage}% of total</div>
        </div>

        <div class="summary-card green">
            <h3>Green Flagged</h3>
            <div class="summary-value">${greenFlagged}</div>
            <div class="summary-detail">${greenPercentage}% of total</div>
        </div>
    `;
}

function displayDataQuality(quality) {
    const qualitySection = document.getElementById('qualitySection');
    
    if (!quality) {
        qualitySection.style.display = 'none';
        return;
    }

    const score = quality.quality_score || 0;
    let scoreClass = 'quality-good';
    let scoreLabel = 'Excellent';

    if (score < 50) {
        scoreClass = 'quality-bad';
        scoreLabel = 'Poor';
    } else if (score < 75) {
        scoreClass = 'quality-warning';
        scoreLabel = 'Fair';
    }

    let issuesHtml = '';
    if (quality.issues && quality.issues.length > 0) {
        issuesHtml = `
            <h4 style="margin-top: 15px; margin-bottom: 10px;">Data Quality Issues:</h4>
            <ul style="margin-left: 20px; color: #666;">
                ${quality.issues.map(issue => `
                    <li>${issue.type}: ${issue.column || 'N/A'} (${issue.count} records, ${issue.percentage}%)</li>
                `).join('')}
            </ul>
        `;
    }

    qualitySection.innerHTML = `
        <h3>📈 Data Quality Assessment</h3>
        <div class="quality-score ${scoreClass}">
            Score: ${score}/100 (${scoreLabel})
        </div>
        ${issuesHtml}
    `;
}

function displayDownloadLinks(outputFiles) {
    const downloadGrid = document.getElementById('downloadGrid');
    
    if (!outputFiles || Object.keys(outputFiles).length === 0) {
        downloadGrid.innerHTML = '<p>No files available for download</p>';
        return;
    }

    const icons = {
        'excel': '📊',
        'html': '🌐',
        'json': '📄'
    };

    const labels = {
        'excel': 'Excel Report',
        'html': 'HTML Report',
        'json': 'JSON Data'
    };

    downloadGrid.innerHTML = Object.entries(outputFiles).map(([format, fileInfo]) => `
        <a href="${fileInfo.url}" class="download-btn" download>
            <span>${icons[format] || '📥'}</span>
            <span>${labels[format] || format}</span>
        </a>
    `).join('');
}

function resetForm() {
    const uploadSection = document.getElementById('uploadSection');
    const resultsSection = document.getElementById('resultsSection');
    const uploadForm = document.getElementById('uploadForm');
    const fileName = document.getElementById('fileName');

    // Reset form
    uploadForm.reset();
    fileName.textContent = 'Choose Excel File';
    fileName.style.color = '';

    // Hide results, show upload
    resultsSection.classList.add('hidden');
    uploadSection.style.display = 'block';

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    const uploadSection = document.getElementById('uploadSection');
    const card = uploadSection.querySelector('.card');
    card.insertBefore(alertDiv, card.firstChild);

    // Auto remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Drag and drop functionality
const fileUploadLabel = document.querySelector('.file-upload-label');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    fileUploadLabel.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    fileUploadLabel.addEventListener(eventName, () => {
        fileUploadLabel.style.borderColor = '#667eea';
        fileUploadLabel.style.background = '#f0f4ff';
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    fileUploadLabel.addEventListener(eventName, () => {
        fileUploadLabel.style.borderColor = '';
        fileUploadLabel.style.background = '';
    }, false);
});

fileUploadLabel.addEventListener('drop', function(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        const fileInput = document.getElementById('fileInput');
        fileInput.files = files;
        
        const fileName = document.getElementById('fileName');
        fileName.textContent = files[0].name;
        fileName.style.color = '#667eea';
    }
}, false);
