#!/usr/bin/env python3
"""Progressive CV parser with step-by-step processing."""

import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Generator


class ProgressiveCVParser:
    """CV parser that processes data step by step with progress updates."""
    
    def __init__(self, cv_text: str, filename: str):
        self.cv_text = cv_text
        self.filename = filename
        self.candidate_data = {}
        
    def emit_progress(self, step: str, status: str, data: Any = None, error: str = None) -> Dict[str, Any]:
        """Emit a progress event."""
        return {
            'step': step,
            'status': status,  # 'starting', 'processing', 'completed', 'error'
            'data': data,
            'error': error,
            'timestamp': time.time()
        }
    
    def query_claude_streaming(self, prompt: str, step_name: str, timeout: int = 30):
        """Query Claude CLI with streaming progress updates."""
        yield self.emit_progress(step_name, "processing", {"message": "🚀 Launching Claude query..."})
        time.sleep(0.2)
        
        yield self.emit_progress(step_name, "processing", {"message": "📝 Sending prompt to Claude AI..."})
        time.sleep(0.3)
        
        try:
            yield self.emit_progress(step_name, "processing", {"message": "🤖 Claude is analyzing the CV text..."})
            
            result = subprocess.run(
                ["claude", "-p", "--dangerously-skip-permissions", "--model", "sonnet"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            yield self.emit_progress(step_name, "processing", {"message": "⚡ Processing request..."})
            time.sleep(0.2)
            
            if result.returncode == 0:
                yield self.emit_progress(step_name, "processing", {"message": "📥 Receiving response from Claude..."})
                time.sleep(0.2)
                
                response = result.stdout.strip()
                
                yield self.emit_progress(step_name, "processing", {"message": "🔍 Parsing Claude's response..."})
                time.sleep(0.1)
                
                # Try to extract JSON if it's wrapped in markdown
                if '```json' in response:
                    yield self.emit_progress(step_name, "processing", {"message": "📋 Extracting JSON from response..."})
                    start = response.find('```json') + 7
                    end = response.find('```', start)
                    if end > start:
                        response = response[start:end].strip()
                elif response.startswith('```') and response.endswith('```'):
                    yield self.emit_progress(step_name, "processing", {"message": "🧹 Cleaning response format..."})
                    response = response[3:-3].strip()
                
                yield self.emit_progress(step_name, "processing", {"message": "✅ Response processed successfully!"})
                return response
            else:
                raise Exception(f"Claude CLI error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("Query timed out")
        except Exception as e:
            raise Exception(f"Error querying Claude: {str(e)}")
    
    def query_claude(self, prompt: str, timeout: int = 30) -> str:
        """Simple non-streaming query for backwards compatibility."""
        try:
            result = subprocess.run(
                ["claude", "-p", "--dangerously-skip-permissions", "--model", "sonnet"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                # Try to extract JSON if it's wrapped in markdown
                if '```json' in response:
                    start = response.find('```json') + 7
                    end = response.find('```', start)
                    if end > start:
                        response = response[start:end].strip()
                elif response.startswith('```') and response.endswith('```'):
                    response = response[3:-3].strip()
                
                return response
            else:
                raise Exception(f"Claude CLI error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("Query timed out")
        except Exception as e:
            raise Exception(f"Error querying Claude: {str(e)}")
    
    def extract_basic_info(self) -> Generator[Dict[str, Any], None, None]:
        """Extract name, email, phone, summary."""
        yield self.emit_progress("basic_info", "starting")
        time.sleep(0.1)
        
        yield self.emit_progress("basic_info", "processing", {"message": "👋 Let's start by figuring out who this candidate is! I'll scan their CV to find their name, contact details, and get a sense of their professional background..."})
        time.sleep(1.0)
        
        yield self.emit_progress("basic_info", "processing", {"message": "🔍 Looking for contact information and professional summary..."})
        time.sleep(0.2)
        
        prompt = f"""Extract basic candidate information from this CV text and return ONLY a JSON object:

{self.cv_text}

Return ONLY this JSON structure (no other text):
{{
  "name": "candidate full name",
  "email": "email address",
  "phone": "phone number", 
  "summary": "brief professional summary (2-3 sentences)"
}}

IMPORTANT: Return ONLY the JSON object, no other text."""

        try:
            yield self.emit_progress("basic_info", "processing", {"message": "📋 Preparing basic info extraction prompt..."})
            time.sleep(0.1)
            
            yield self.emit_progress("basic_info", "processing", {"message": "🚀 Launching Claude query..."})
            time.sleep(0.1)
            
            yield self.emit_progress("basic_info", "processing", {"message": "🤖 Claude is analyzing the CV text..."})
            response = self.query_claude(prompt, timeout=45)
            
            if response:
                yield self.emit_progress("basic_info", "processing", {"message": "🔧 Parsing basic information..."})
                time.sleep(0.1)
                
                basic_info = json.loads(response)
                
                yield self.emit_progress("basic_info", "processing", {"message": f"👤 Found candidate: {basic_info.get('name', 'Unknown')}"})
                time.sleep(0.1)
                
                yield self.emit_progress("basic_info", "processing", {"message": f"📧 Email: {basic_info.get('email', 'Not found')}"})
                time.sleep(0.1)
                
                yield self.emit_progress("basic_info", "processing", {"message": f"📱 Phone: {basic_info.get('phone', 'Not found')}"})
                time.sleep(0.1)
                
                self.candidate_data.update(basic_info)
                yield self.emit_progress("basic_info", "completed", basic_info)
            
        except Exception as e:
            yield self.emit_progress("basic_info", "error", error=str(e))
    
    def extract_skills(self) -> Generator[Dict[str, Any], None, None]:
        """Extract technical and soft skills."""
        yield self.emit_progress("skills", "starting")
        time.sleep(0.1)
        
        yield self.emit_progress("skills", "processing", {"message": "🚀 Now that we know who they are, let's discover their technical superpowers! I'll hunt through their CV for programming languages, frameworks, tools, and any other skills that make them stand out..."})
        time.sleep(1.2)
        
        yield self.emit_progress("skills", "processing", {"message": "🛠️ Scanning for technical skills and expertise..."})
        time.sleep(0.2)
        
        prompt = f"""Extract all skills from this CV text and return ONLY a JSON object:

{self.cv_text}

Return ONLY this JSON structure (no other text):
{{
  "skills": ["skill1", "skill2", "skill3", "etc"]
}}

Include programming languages, frameworks, tools, cloud platforms, databases, and relevant soft skills.
IMPORTANT: Return ONLY the JSON object, no other text."""

        try:
            yield self.emit_progress("skills", "processing", {"message": "📝 Building skills extraction prompt..."})
            time.sleep(0.1)
            
            yield self.emit_progress("skills", "processing", {"message": "🚀 Launching Claude query..."})
            time.sleep(0.1)
            
            yield self.emit_progress("skills", "processing", {"message": "🤖 Claude is analyzing skills..."})
            response = self.query_claude(prompt, timeout=45)
            
            if response:
                yield self.emit_progress("skills", "processing", {"message": "🔍 Categorizing found skills..."})
                time.sleep(0.1)
                
                skills_data = json.loads(response)
                skills_count = len(skills_data.get('skills', []))
                
                yield self.emit_progress("skills", "processing", {"message": f"💎 Found {skills_count} skills total"})
                time.sleep(0.1)
                
                # Show some example skills
                if skills_data.get('skills'):
                    example_skills = skills_data['skills'][:3]
                    yield self.emit_progress("skills", "processing", {"message": f"🎯 Examples: {', '.join(example_skills)}..."})
                    time.sleep(0.1)
                
                self.candidate_data.update(skills_data)
                yield self.emit_progress("skills", "completed", skills_data)
            
        except Exception as e:
            yield self.emit_progress("skills", "error", error=str(e))
    
    def extract_experience(self) -> Generator[Dict[str, Any], None, None]:
        """Extract work experience."""
        yield self.emit_progress("experience", "starting")
        time.sleep(0.1)
        
        yield self.emit_progress("experience", "processing", {"message": "📈 Time to dive into their professional journey! I'll trace through their career path, uncovering where they've worked, what roles they've held, and the impact they've made along the way. This tells the real story of their experience..."})
        time.sleep(1.3)
        
        yield self.emit_progress("experience", "processing", {"message": "💼 Analyzing work history and achievements..."})
        time.sleep(0.2)
        
        prompt = f"""Extract work experience from this CV text and return ONLY a JSON object:

{self.cv_text}

Return ONLY this JSON structure (no other text):
{{
  "experience": [
    {{
      "company": "Company Name",
      "position": "Job Title", 
      "dates": "Date Range",
      "description": "Brief description of role and achievements"
    }}
  ]
}}

IMPORTANT: Return ONLY the JSON object, no other text."""

        try:
            yield self.emit_progress("experience", "processing", {"message": "📊 Preparing experience extraction..."})
            time.sleep(0.1)
            
            yield self.emit_progress("experience", "processing", {"message": "🚀 Launching Claude query..."})
            time.sleep(0.1)
            
            yield self.emit_progress("experience", "processing", {"message": "🤖 Claude is analyzing work history..."})
            response = self.query_claude(prompt, timeout=45)
            
            if response:
                yield self.emit_progress("experience", "processing", {"message": "🏢 Processing work history..."})
                time.sleep(0.1)
                
                experience_data = json.loads(response)
                exp_count = len(experience_data.get('experience', []))
                
                yield self.emit_progress("experience", "processing", {"message": f"📈 Found {exp_count} work experience entries"})
                time.sleep(0.1)
                
                # Show recent company
                if experience_data.get('experience'):
                    recent_exp = experience_data['experience'][0]
                    yield self.emit_progress("experience", "processing", {"message": f"🏆 Most recent: {recent_exp.get('position', 'Unknown')} at {recent_exp.get('company', 'Unknown')}"})
                    time.sleep(0.1)
                
                self.candidate_data.update(experience_data)
                yield self.emit_progress("experience", "completed", experience_data)
            
        except Exception as e:
            yield self.emit_progress("experience", "error", error=str(e))
    
    def extract_education(self) -> Generator[Dict[str, Any], None, None]:
        """Extract education information."""
        yield self.emit_progress("education", "starting")
        time.sleep(0.1)
        
        yield self.emit_progress("education", "processing", {"message": "🎓 Let's explore their educational foundation! I'll look for degrees, certifications, and academic achievements that shaped their expertise. Education often reveals the depth of knowledge behind their practical skills..."})
        time.sleep(1.1)
        
        yield self.emit_progress("education", "processing", {"message": "📚 Scanning for academic credentials and qualifications..."})
        time.sleep(0.2)
        
        prompt = f"""Extract education information from this CV text and return ONLY a JSON object:

{self.cv_text}

Return ONLY this JSON structure (no other text):
{{
  "education": [
    {{
      "institution": "University/School Name",
      "degree": "Degree Name",
      "dates": "Date Range"
    }}
  ]
}}

IMPORTANT: Return ONLY the JSON object, no other text."""

        try:
            yield self.emit_progress("education", "processing", {"message": "📚 Scanning for academic credentials..."})
            time.sleep(0.1)
            
            yield self.emit_progress("education", "processing", {"message": "🚀 Launching Claude query..."})
            time.sleep(0.1)
            
            yield self.emit_progress("education", "processing", {"message": "🤖 Claude is analyzing education..."})
            response = self.query_claude(prompt, timeout=45)
            
            if response:
                education_data = json.loads(response)
                edu_count = len(education_data.get('education', []))
                
                yield self.emit_progress("education", "processing", {"message": f"🏫 Found {edu_count} education entries"})
                time.sleep(0.1)
                
                if education_data.get('education'):
                    latest_edu = education_data['education'][0]
                    yield self.emit_progress("education", "processing", {"message": f"🎯 Latest: {latest_edu.get('degree', 'Unknown')} from {latest_edu.get('institution', 'Unknown')}"})
                    time.sleep(0.1)
                
                self.candidate_data.update(education_data)
                yield self.emit_progress("education", "completed", education_data)
            
        except Exception as e:
            yield self.emit_progress("education", "error", error=str(e))
    
    def extract_projects_and_certifications(self) -> Generator[Dict[str, Any], None, None]:
        """Extract projects and certifications."""
        yield self.emit_progress("projects_certs", "starting")
        time.sleep(0.1)
        
        yield self.emit_progress("projects_certs", "processing", {"message": "🚀 Now for the exciting extras! I'll search for passion projects, side work, and professional certifications. These often reveal a candidate's curiosity, continuous learning mindset, and what they do beyond their day job..."})
        time.sleep(1.4)
        
        prompt = f"""Extract projects and certifications from this CV text and return ONLY a JSON object:

{self.cv_text}

Return ONLY this JSON structure (no other text):
{{
  "projects": [
    {{
      "name": "Project Name",
      "description": "Project description"
    }}
  ],
  "certifications": ["Certification Name 1", "Certification Name 2"]
}}

IMPORTANT: Return ONLY the JSON object, no other text."""

        try:
            yield self.emit_progress("projects_certs", "processing", {"message": "🚀 Launching Claude query..."})
            time.sleep(0.1)
            
            yield self.emit_progress("projects_certs", "processing", {"message": "🤖 Claude is analyzing projects..."})
            response = self.query_claude(prompt, timeout=45)  # Increase timeout
            
            projects_certs_data = json.loads(response)
            proj_count = len(projects_certs_data.get('projects', []))
            cert_count = len(projects_certs_data.get('certifications', []))
            
            yield self.emit_progress("projects_certs", "processing", {"message": f"📊 Found {proj_count} projects, {cert_count} certifications"})
            time.sleep(0.1)
            
            self.candidate_data.update(projects_certs_data)
            yield self.emit_progress("projects_certs", "completed", projects_certs_data)
            
        except Exception as e:
            yield self.emit_progress("projects_certs", "error", error=str(e))
    
    def finalize(self) -> Generator[Dict[str, Any], None, None]:
        """Finalize and save the complete candidate profile."""
        yield self.emit_progress("finalize", "starting")
        time.sleep(0.1)
        
        try:
            yield self.emit_progress("finalize", "processing", {"message": "🎉 Excellent! We've gathered all the pieces of the puzzle. Now I'm putting together a comprehensive candidate profile that captures their complete professional story - from their background and skills to their experience and aspirations..."})
            time.sleep(1.5)
            
            yield self.emit_progress("finalize", "processing", {"message": "🎯 Compiling complete candidate profile..."})
            time.sleep(0.2)
            
            yield self.emit_progress("finalize", "processing", {"message": "📊 Validating extracted data..."})
            time.sleep(0.1)
            
            # Calculate some stats
            total_skills = len(self.candidate_data.get('skills', []))
            total_experience = len(self.candidate_data.get('experience', []))
            total_education = len(self.candidate_data.get('education', []))
            
            yield self.emit_progress("finalize", "processing", {"message": f"📈 Profile summary: {total_skills} skills, {total_experience} jobs, {total_education} education"})
            time.sleep(0.2)
            
            yield self.emit_progress("finalize", "processing", {"message": "💾 Saving structured data to file..."})
            time.sleep(0.1)
            
            # Save to file
            output_dir = Path("parsed")
            output_dir.mkdir(exist_ok=True)
            
            filename_stem = Path(self.filename).stem
            json_file = output_dir / f"{filename_stem}_structured.json"
            
            with open(json_file, 'w') as f:
                json.dump(self.candidate_data, f, indent=2)
            
            yield self.emit_progress("finalize", "processing", {"message": "✨ Generating final candidate summary..."})
            time.sleep(0.2)
            
            yield self.emit_progress("finalize", "processing", {"message": "🎊 Mission accomplished! All candidate information has been successfully extracted and organized into a comprehensive profile."})
            time.sleep(0.5)
            
            yield self.emit_progress("finalize", "completed", {
                "candidate_data": self.candidate_data,
                "file_saved": str(json_file),
                "message": "🎉 CV parsing completed successfully! Ready to review the candidate profile."
            })
            
        except Exception as e:
            yield self.emit_progress("finalize", "error", error=str(e))
    
    def parse_progressive(self) -> Generator[Dict[str, Any], None, None]:
        """Run the complete progressive parsing process."""
        
        # Welcome message
        yield self.emit_progress("initialize", "starting", {"message": "🎯 Welcome to AI-powered CV parsing! I'm about to analyze this candidate's CV and extract all the important information in a structured format. Let me walk you through each step of the process..."})
        time.sleep(2.0)
        
        # Step 1: Basic Info
        yield from self.extract_basic_info()
        time.sleep(0.3)
        
        yield self.emit_progress("transition", "processing", {"message": "✅ Great! Now I have their basic profile. Next, let's see what technical skills they bring to the table..."})
        time.sleep(0.8)
        
        # Step 2: Skills
        yield from self.extract_skills()
        time.sleep(0.3)
        
        yield self.emit_progress("transition", "processing", {"message": "💪 Skills identified! Now let's dive into their work history to see how they've applied these skills in real-world situations..."})
        time.sleep(0.8)
        
        # Step 3: Experience
        yield from self.extract_experience()
        time.sleep(0.3)
        
        yield self.emit_progress("transition", "processing", {"message": "📊 Professional journey mapped! Time to check their educational background that laid the foundation for all this experience..."})
        time.sleep(0.8)
        
        # Step 4: Education
        yield from self.extract_education()
        time.sleep(0.3)
        
        yield self.emit_progress("transition", "processing", {"message": "🎓 Academic foundation documented! Finally, let's look for any bonus projects or certifications that show their extra initiative..."})
        time.sleep(0.8)
        
        # Step 5: Projects & Certifications
        yield from self.extract_projects_and_certifications()
        time.sleep(0.3)
        
        yield self.emit_progress("transition", "processing", {"message": "🏆 All information collected! Time to put it all together into a beautiful, complete candidate profile..."})
        time.sleep(0.8)
        
        # Step 6: Finalize
        yield from self.finalize()