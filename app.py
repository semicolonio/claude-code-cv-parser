#!/usr/bin/env python3
"""Flask web application for CV parsing with file upload."""

import json
import os
import subprocess
from pathlib import Path
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Configuration
UPLOAD_FOLDER = Path('uploads')
PARSED_FOLDER = Path('parsed')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Ensure directories exist
UPLOAD_FOLDER.mkdir(exist_ok=True)
PARSED_FOLDER.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_cv_with_claude(cv_file_path):
    """Parse CV using Claude CLI - adapted from final_working_parser.py."""
    
    cv_path = Path(cv_file_path)
    if not cv_path.exists():
        return None, f"File not found: {cv_file_path}"
    
    # For now, only support TXT files in the web app
    if cv_path.suffix.lower() != '.txt':
        return None, "Only .txt files are currently supported"
    
    cv_content = cv_path.read_text(encoding='utf-8')
    
    # Create parsing prompt
    prompt = f"""Extract candidate information from this CV in JSON format:

{cv_content}

Return a JSON object with these fields:
- name: candidate full name
- email: email address  
- phone: phone number
- summary: brief professional summary
- skills: array of technical skills
- experience: array of work experience (company, position, dates, description)
- education: array of education (institution, degree, dates)
- projects: array of notable projects
- certifications: array of certifications

Example format:
{{
  "name": "John Smith",
  "email": "john@example.com", 
  "phone": "(555) 123-4567",
  "summary": "Experienced software engineer...",
  "skills": ["Python", "JavaScript", "AWS"],
  "experience": [
    {{
      "company": "TechCorp",
      "position": "Senior Engineer",
      "dates": "2021-Present", 
      "description": "Led development of..."
    }}
  ],
  "education": [
    {{
      "institution": "University",
      "degree": "BS Computer Science",
      "dates": "2014-2018"
    }}
  ],
  "projects": [],
  "certifications": []
}}"""

    try:
        # Use Claude CLI with skip permissions for automation
        result = subprocess.run(
            ["claude", "-p", "--dangerously-skip-permissions"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            response = result.stdout.strip()
            
            if response and not response.startswith("Execution error"):
                # Extract JSON from response
                start = response.find('{')
                end = response.rfind('}') + 1
                
                if start >= 0 and end > start:
                    json_str = response[start:end]
                    candidate_data = json.loads(json_str)
                    
                    # Save structured data
                    json_file = PARSED_FOLDER / f"{cv_path.stem}_structured.json"
                    with open(json_file, 'w') as f:
                        json.dump(candidate_data, f, indent=2)
                    
                    return candidate_data, None
                else:
                    return None, "No valid JSON found in Claude response"
            else:
                return None, f"Claude error: {response}"
        else:
            return None, f"Claude CLI error: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return None, "Processing timed out"
    except json.JSONDecodeError as e:
        return None, f"JSON parsing error: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"


@app.route('/')
def index():
    """Main upload page."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and parsing."""
    
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Save uploaded file
        file_path = app.config['UPLOAD_FOLDER'] / filename
        file.save(file_path)
        
        # Parse CV with Claude
        candidate_data, error = parse_cv_with_claude(file_path)
        
        if error:
            flash(f'Error parsing CV: {error}')
            return redirect(url_for('index'))
        
        if candidate_data:
            # Store in session or pass to template
            return render_template('results.html', candidate=candidate_data, filename=filename)
        else:
            flash('Failed to parse CV - no data extracted')
            return redirect(url_for('index'))
    
    else:
        flash('Invalid file type. Please upload TXT, PDF, DOC, or DOCX files.')
        return redirect(url_for('index'))


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """API endpoint for file upload (for AJAX requests)."""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    filename = secure_filename(file.filename)
    file_path = app.config['UPLOAD_FOLDER'] / filename
    file.save(file_path)
    
    # Parse CV
    candidate_data, error = parse_cv_with_claude(file_path)
    
    if error:
        return jsonify({'error': error}), 500
    
    if candidate_data:
        return jsonify({
            'success': True,
            'candidate': candidate_data,
            'filename': filename
        })
    else:
        return jsonify({'error': 'Failed to parse CV'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)