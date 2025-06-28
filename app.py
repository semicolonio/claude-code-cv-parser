#!/usr/bin/env python3
"""Flask web application for CV parsing with file upload."""

import json
import subprocess
import time
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Response, session

# Import from our organized modules
from src.config.settings import (
    SECRET_KEY, UPLOAD_FOLDER, PARSED_FOLDER, 
    MAX_FILE_SIZE, CLAUDE_MODEL, CLAUDE_TIMEOUT
)
from src.utils.file_processing import extract_text_from_file, allowed_file
from src.parsers.progressive import ProgressiveCVParser

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Configuration
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE



def parse_cv_with_claude(cv_file_path):
    """Parse CV using Claude CLI with text extraction."""
    
    cv_path = Path(cv_file_path)
    if not cv_path.exists():
        return None, f"File not found: {cv_file_path}"
    
    # Extract text from file first
    cv_text = extract_text_from_file(cv_path)
    
    if cv_text.startswith("Error") or cv_text.startswith("Unsupported"):
        return None, cv_text
    
    # Create parsing prompt with extracted text - using regular string to avoid f-string conflicts
    prompt = """Extract candidate information from this CV text and return ONLY a JSON object. Do not include any other text, explanations, or comments.

CV TEXT:
""" + cv_text + """

Return ONLY a JSON object with these fields (no other text):
{
  "name": "candidate full name",
  "email": "email address",  
  "phone": "phone number",
  "summary": "brief professional summary",
  "skills": ["skill1", "skill2", "skill3"],
  "experience": [
    {
      "company": "Company Name",
      "position": "Job Title",
      "dates": "Date Range", 
      "description": "Job description"
    }
  ],
  "education": [
    {
      "institution": "University Name",
      "degree": "Degree Name",
      "dates": "Date Range"
    }
  ],
  "projects": [
    {
      "name": "Project Name",
      "description": "Project description"
    }
  ],
  "certifications": ["Certification Name"]
}

IMPORTANT: Return ONLY the JSON object, no other text whatsoever."""

    try:
        # Use Claude CLI with text input (not file upload)
        result = subprocess.run(
            ["claude", "-p", "--dangerously-skip-permissions", "--model", CLAUDE_MODEL],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=CLAUDE_TIMEOUT
        )
        
        if result.returncode == 0:
            response = result.stdout.strip()
            
            # Debug: Save the raw response to check what Claude returned
            debug_file = PARSED_FOLDER / f"{cv_path.stem}_debug_response.txt"
            with open(debug_file, 'w') as f:
                f.write(f"STDOUT:\n{response}\n\nSTDERR:\n{result.stderr}")
            
            # Check if Claude created a JSON file (it sometimes does this)
            possible_files = [
                Path("parsed_cv.json"),
                Path(f"{cv_path.stem}.json"),
                PARSED_FOLDER / f"{cv_path.stem}.json"
            ]
            
            for json_file_path in possible_files:
                if json_file_path.exists():
                    try:
                        with open(json_file_path, 'r') as f:
                            candidate_data = json.load(f)
                        
                        # Save to our expected location
                        final_json_file = PARSED_FOLDER / f"{cv_path.stem}_structured.json"
                        with open(final_json_file, 'w') as f:
                            json.dump(candidate_data, f, indent=2)
                        
                        return candidate_data, None
                    except json.JSONDecodeError:
                        continue
            
            if response and not response.startswith("Execution error"):
                # Look for JSON in the response - try multiple patterns
                json_patterns = [
                    (response.find('{'), response.rfind('}') + 1),  # Standard JSON
                    (response.find('```json') + 7, response.find('```', response.find('```json') + 7)),  # Markdown JSON
                ]
                
                for start, end in json_patterns:
                    if start >= 0 and end > start and start < len(response):
                        try:
                            json_str = response[start:end].strip()
                            if json_str.startswith('```'):
                                json_str = json_str[3:].strip()
                            if json_str.endswith('```'):
                                json_str = json_str[:-3].strip()
                            
                            candidate_data = json.loads(json_str)
                            
                            # Save structured data
                            json_file = PARSED_FOLDER / f"{cv_path.stem}_structured.json"
                            with open(json_file, 'w') as f:
                                json.dump(candidate_data, f, indent=2)
                            
                            return candidate_data, None
                        except json.JSONDecodeError:
                            continue
                
                # If no JSON found, check if there's already a good file and use it
                existing_file = Path("parsed_cv.json")
                if existing_file.exists():
                    try:
                        with open(existing_file, 'r') as f:
                            candidate_data = json.load(f)
                        return candidate_data, None
                    except:
                        pass
                
                # If no JSON found, return the raw response for debugging
                return None, f"No valid JSON found. Raw response saved to {debug_file}. Response preview: {response[:200]}..."
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


@app.route('/upload_progressive', methods=['POST'])
def upload_progressive():
    """Handle file upload and redirect to progressive parsing."""
    
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Save uploaded file
        file_path = app.config['UPLOAD_FOLDER'] / filename
        file.save(file_path)
        
        # Store filename in session for the progressive parsing
        session['parsing_file'] = filename
        
        return render_template('progressive.html', filename=filename)
    
    else:
        flash('Invalid file type. Please upload TXT, PDF, DOC, or DOCX files.')
        return redirect(url_for('index'))


@app.route('/parse_progressive')
def parse_progressive():
    """SSE endpoint for progressive CV parsing."""
    
    filename = session.get('parsing_file')
    if not filename:
        return Response("No file to parse", status=400)
    
    file_path = app.config['UPLOAD_FOLDER'] / filename
    if not file_path.exists():
        return Response("File not found", status=404)
    
    # Extract text from file
    cv_text = extract_text_from_file(file_path)
    if cv_text.startswith("Error") or cv_text.startswith("Unsupported"):
        return Response(f"Error reading file: {cv_text}", status=400)
    
    def generate_progress():
        """Generate SSE progress events with progressive parser."""
        parser = ProgressiveCVParser(cv_text, filename)
        
        try:
            for progress_event in parser.parse_progressive():
                # Format as SSE
                yield f"data: {json.dumps(progress_event)}\n\n"
                
        except Exception as e:
            error_event = {
                'step': 'error',
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return Response(
        generate_progress(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )


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


@app.route('/show_final_results', methods=['POST'])
def show_final_results():
    """Show final results from progressive parsing."""
    candidate_data_json = request.form.get('candidate_data')
    filename = request.form.get('filename')
    
    if not candidate_data_json:
        flash('No candidate data received')
        return redirect(url_for('index'))
    
    try:
        candidate_data = json.loads(candidate_data_json)
        return render_template('results.html', candidate=candidate_data, filename=filename)
    except json.JSONDecodeError:
        flash('Invalid candidate data format')
        return redirect(url_for('index'))


# Store conversation sessions in memory (in production, use Redis or database)
# Format: {conversation_id: [{"role": "user/assistant", "content": "message"}, ...]}
conversation_sessions = {}


@app.route('/api/chat', methods=['POST'])
def chat_with_candidate():
    """Handle chat messages about the candidate."""
    print(f"\n=== Chat Request Received ===")
    
    data = request.json
    user_message = data.get('message', '').strip()
    candidate_data = data.get('candidate', {})
    conversation_id = data.get('conversationId')
    
    print(f"User message: {user_message}")
    print(f"Conversation ID: {conversation_id}")
    print(f"Candidate name: {candidate_data.get('name', 'Unknown')}")
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    if not candidate_data:
        return jsonify({'error': 'No candidate data provided'}), 400
    
    # Generate conversation ID if not provided
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
    
    # Build context about the candidate
    context = f"""You are a helpful assistant answering questions about a candidate's CV. Here is the candidate's information:

Name: {candidate_data.get('name', 'Unknown')}
Email: {candidate_data.get('email', 'Not provided')}
Phone: {candidate_data.get('phone', 'Not provided')}

Professional Summary:
{candidate_data.get('summary', 'No summary provided')}

Skills: {', '.join(candidate_data.get('skills', [])) if candidate_data.get('skills') else 'No skills listed'}

Work Experience:
"""
    
    for exp in candidate_data.get('experience', []):
        context += f"\n- {exp.get('position', 'Unknown Position')} at {exp.get('company', 'Unknown Company')} ({exp.get('dates', 'Dates not specified')})"
        if exp.get('description'):
            context += f"\n  {exp.get('description')}"
    
    context += "\n\nEducation:\n"
    for edu in candidate_data.get('education', []):
        context += f"- {edu.get('degree', 'Unknown Degree')} from {edu.get('institution', 'Unknown Institution')} ({edu.get('dates', 'Dates not specified')})\n"
    
    if candidate_data.get('projects'):
        context += "\n\nProjects:\n"
        for proj in candidate_data.get('projects', []):
            context += f"- {proj.get('name', 'Unnamed Project')}: {proj.get('description', 'No description')}\n"
    
    # Build conversation history
    conversation_history = ""
    if conversation_id in conversation_sessions:
        # Add previous messages to context
        conversation_history = "\n\nConversation History:\n"
        for msg in conversation_sessions[conversation_id]:
            conversation_history += f"{msg['role'].capitalize()}: {msg['content']}\n"
    
    # Build the full prompt with context, history, and current question
    full_prompt = context + conversation_history + f"\n\nUser Question: {user_message}\n\nProvide a helpful, concise answer based on the candidate's information. If the information requested is not available in the CV, politely say so."
    
    try:
        # Call Claude CLI with full context each time
        cmd = ["claude", "-p", "--dangerously-skip-permissions", "--model", CLAUDE_MODEL]
        
        result = subprocess.run(
            cmd,
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            response = result.stdout.strip()
            
            # Clean up response if needed
            if response.startswith("Assistant:"):
                response = response[10:].strip()
            
            # Store conversation history
            if conversation_id not in conversation_sessions:
                conversation_sessions[conversation_id] = []
            
            # Add user message and assistant response to history
            conversation_sessions[conversation_id].append({
                'role': 'user',
                'content': user_message
            })
            conversation_sessions[conversation_id].append({
                'role': 'assistant', 
                'content': response
            })
            
            # Keep only last 10 exchanges to prevent context from growing too large
            if len(conversation_sessions[conversation_id]) > 20:  # 20 = 10 exchanges * 2 messages
                conversation_sessions[conversation_id] = conversation_sessions[conversation_id][-20:]
            
            # Log successful response
            print(f"Chat response generated successfully for conversation {conversation_id}")
            print(f"Conversation history length: {len(conversation_sessions[conversation_id])} messages")
            
            return jsonify({
                'success': True,
                'response': response,
                'conversationId': conversation_id
            })
        else:
            error_msg = f"Claude CLI error: {result.stderr}"
            print(f"ERROR in chat endpoint: {error_msg}")
            print(f"Command: {' '.join(cmd)}")
            print(f"Return code: {result.returncode}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
            
    except subprocess.TimeoutExpired:
        print("ERROR: Chat request timed out")
        return jsonify({
            'success': False,
            'error': 'Request timed out'
        }), 500
    except Exception as e:
        print(f"ERROR in chat endpoint: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)