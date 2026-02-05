"""
Production-Ready Flask Application for Red Flag Analysis
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import json
import logging
from datetime import datetime
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline import RedFlagPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'pwd-red-flag-analyzer-secret-key-change-in-production')

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(__file__), 'outputs')

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)


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
            output_formats = ['excel', 'pdf']
        
        # Run analysis pipeline
        pipeline = RedFlagPipeline()
        result = pipeline.run(filepath, output_formats=output_formats)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': f"Analysis failed: {result.get('error', 'Unknown error')}"
            }), 500
        
        # Prepare response with download links
        output_files = {}
        for fmt, file_path in result['output_files'].items():
            output_filename = os.path.basename(file_path)
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            # Copy file to output folder
            import shutil
            shutil.copy2(file_path, output_path)
            
            # Clean up temp file
            try:
                os.remove(file_path)
            except:
                pass
            
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
    return jsonify({
        'status': 'ok', 
        'timestamp': datetime.now().isoformat(),
        'service': 'PWD Red Flag Analyzer'
    })


@app.route('/api/info')
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'PWD Works Red Flag Analyzer',
        'version': '1.0.0',
        'description': 'Automated audit compliance analysis for PWD works',
        'supported_formats': ['xlsx', 'xls'],
        'max_file_size_mb': 50,
        'red_flags': [
            'Diversion of Funds',
            'Wasteful Survey Expenditure',
            'Excess Expenditure (>10% above AA)',
            'Overlapping Works',
            'Delay in Completion',
            'Splitting of Works',
            'Non-recovery of Centage',
            'Unspent Balance'
        ],
        'output_formats': ['excel', 'pdf', 'html', 'json']
    })


# Error handlers
@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 50MB.'
    }), 413


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {str(e)}", exc_info=True)
    return jsonify({
        'success': False,
        'error': 'Internal server error. Please try again.'
    }), 500


if __name__ == '__main__':
    # Get port from environment variable (for cloud platforms)
    port = int(os.environ.get('PORT', 5000))
    
    # Run app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('DEBUG', 'False').lower() == 'true'
    )
