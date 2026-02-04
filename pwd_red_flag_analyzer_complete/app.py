"""
Flask Web Application for Red Flag Analysis
Professional web interface for analyzing PWD works
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import json
import logging
from datetime import datetime

from pipeline import RedFlagPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Configure upload folder
UPLOAD_FOLDER = '/home/claude/uploads'
OUTPUT_FOLDER = '/home/claude/outputs'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and analysis"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False, 
                'error': 'Invalid file type. Please upload .xlsx or .xls file'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        logger.info(f"File uploaded: {filepath}")
        
        # Get output formats from request
        output_formats = request.form.getlist('formats')
        if not output_formats:
            output_formats = ['excel', 'html']
        
        # Run analysis pipeline
        pipeline = RedFlagPipeline()
        result = pipeline.run(filepath, output_formats=output_formats)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': f"Analysis failed: {result.get('error', 'Unknown error')}"
            }), 500
        
        # Prepare response with download links
        output_files = {}
        for fmt, file_path in result['output_files'].items():
            # Move files to output folder for download
            output_filename = os.path.basename(file_path)
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            # Copy file to output folder
            import shutil
            shutil.copy2(file_path, output_path)
            
            output_files[fmt] = {
                'filename': output_filename,
                'url': f'/download/{output_filename}'
            }
        
        # Get summary
        summary = pipeline.get_summary()
        
        return jsonify({
            'success': True,
            'summary': summary,
            'output_files': output_files,
            'data_quality': result.get('data_quality', {})
        })
        
    except Exception as e:
        logger.error(f"Error in upload: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/download/<filename>')
def download_file(filename):
    """Download generated report"""
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error in download: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
