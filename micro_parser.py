#!/usr/bin/env python3
"""Micro-step CV parser with tiny, fast queries for real-time updates."""

import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Generator


class MicroCVParser:
    """CV parser that uses many small, fast queries for real-time updates."""
    
    def __init__(self, cv_text: str, filename: str):
        self.cv_text = cv_text
        self.filename = filename
        self.candidate_data = {}
        
    def emit_progress(self, step: str, status: str, data: Any = None, error: str = None) -> Dict[str, Any]:
        """Emit a progress event."""
        return {
            'step': step,
            'status': status,
            'data': data,
            'error': error,
            'timestamp': time.time()
        }
    
    def query_claude_micro(self, prompt: str, timeout: int = 15) -> str:
        """Quick Claude query with short timeout for micro-tasks."""
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
                # Clean response
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
    
    def extract_name(self) -> Generator[Dict[str, Any], None, None]:
        """Extract just the candidate name."""
        yield self.emit_progress("basic_info", "processing", {"message": "👤 Finding candidate name..."})
        
        prompt = f"""Find the candidate's full name from this CV text and return ONLY the name:

{self.cv_text[:1000]}  

Return only the full name, nothing else."""

        try:
            name = self.query_claude_micro(prompt).strip().strip('"').strip("'")
            self.candidate_data['name'] = name
            
            yield self.emit_progress("basic_info", "processing", {
                "partial_data": {"name": name},
                "message": f"✅ Found name: {name}"
            })
            
        except Exception as e:
            yield self.emit_progress("basic_info", "processing", {"message": f"⚠️ Could not find name: {str(e)}"})
            self.candidate_data['name'] = "Unknown"
    
    def extract_email(self) -> Generator[Dict[str, Any], None, None]:
        """Extract just the email address."""
        yield self.emit_progress("basic_info", "processing", {"message": "📧 Finding email address..."})
        
        prompt = f"""Find the candidate's email address from this CV text and return ONLY the email:

{self.cv_text[:1000]}

Return only the email address, nothing else."""

        try:
            email = self.query_claude_micro(prompt).strip().strip('"').strip("'")
            self.candidate_data['email'] = email
            
            yield self.emit_progress("basic_info", "processing", {
                "partial_data": {"email": email},
                "message": f"✅ Found email: {email}"
            })
            
        except Exception as e:
            yield self.emit_progress("basic_info", "processing", {"message": f"⚠️ Could not find email: {str(e)}"})
            self.candidate_data['email'] = None
    
    def extract_phone(self) -> Generator[Dict[str, Any], None, None]:
        """Extract just the phone number."""
        yield self.emit_progress("basic_info", "processing", {"message": "📱 Finding phone number..."})
        
        prompt = f"""Find the candidate's phone number from this CV text and return ONLY the phone number:

{self.cv_text[:1000]}

Return only the phone number, nothing else."""

        try:
            phone = self.query_claude_micro(prompt).strip().strip('"').strip("'")
            self.candidate_data['phone'] = phone
            
            yield self.emit_progress("basic_info", "processing", {
                "partial_data": {"phone": phone},
                "message": f"✅ Found phone: {phone}"
            })
            
        except Exception as e:
            yield self.emit_progress("basic_info", "processing", {"message": f"⚠️ Could not find phone: {str(e)}"})
            self.candidate_data['phone'] = None
    
    def extract_summary(self) -> Generator[Dict[str, Any], None, None]:
        """Extract just the professional summary."""
        yield self.emit_progress("basic_info", "processing", {"message": "📝 Extracting professional summary..."})
        
        prompt = f"""Write a brief 2-sentence professional summary for this candidate based on their CV:

{self.cv_text[:2000]}

Return only the summary, nothing else."""

        try:
            summary = self.query_claude_micro(prompt, timeout=20).strip().strip('"').strip("'")
            self.candidate_data['summary'] = summary
            
            yield self.emit_progress("basic_info", "processing", {
                "partial_data": {"summary": summary},
                "message": "✅ Generated professional summary"
            })
            
        except Exception as e:
            yield self.emit_progress("basic_info", "processing", {"message": f"⚠️ Could not generate summary: {str(e)}"})
            self.candidate_data['summary'] = None
    
    def extract_basic_info_micro(self) -> Generator[Dict[str, Any], None, None]:
        """Extract basic info with micro-steps."""
        yield self.emit_progress("basic_info", "starting")
        time.sleep(0.1)
        
        # Step-by-step micro extractions
        yield from self.extract_name()
        time.sleep(0.2)
        
        yield from self.extract_email()
        time.sleep(0.2)
        
        yield from self.extract_phone()
        time.sleep(0.2)
        
        yield from self.extract_summary()
        time.sleep(0.2)
        
        # Complete basic info
        basic_info = {
            "name": self.candidate_data.get('name'),
            "email": self.candidate_data.get('email'),
            "phone": self.candidate_data.get('phone'),
            "summary": self.candidate_data.get('summary')
        }
        
        yield self.emit_progress("basic_info", "completed", basic_info)
    
    def extract_skills_micro(self) -> Generator[Dict[str, Any], None, None]:
        """Extract skills with real-time updates."""
        yield self.emit_progress("skills", "starting")
        time.sleep(0.1)
        
        yield self.emit_progress("skills", "processing", {"message": "🔍 Scanning for programming languages..."})
        
        # Extract programming languages first
        prompt = f"""List programming languages mentioned in this CV as a JSON array:

{self.cv_text[:1500]}

Return format: ["Python", "JavaScript", etc]
Return ONLY the JSON array."""

        languages = []
        frameworks = []
        
        try:
            # Extract programming languages first
            languages_str = self.query_claude_micro(prompt, timeout=25)
            languages = json.loads(languages_str)
            
            yield self.emit_progress("skills", "processing", {
                "partial_data": {"languages": languages},
                "message": f"✅ Found {len(languages)} programming languages"
            })
            
            time.sleep(0.3)
            
        except Exception as e:
            yield self.emit_progress("skills", "processing", {"message": f"⚠️ Error extracting languages: {str(e)}"})
        
        try:
            # Extract frameworks and tools
            yield self.emit_progress("skills", "processing", {"message": "🛠️ Finding frameworks and tools..."})
            
            prompt2 = f"""List frameworks, libraries, and tools mentioned in this CV as a JSON array:

{self.cv_text[:1500]}

Return format: ["React", "Django", "Docker", etc]
Return ONLY the JSON array."""
            
            frameworks_str = self.query_claude_micro(prompt2, timeout=25)
            frameworks = json.loads(frameworks_str)
            
            yield self.emit_progress("skills", "processing", {
                "partial_data": {"frameworks": frameworks},
                "message": f"✅ Found {len(frameworks)} frameworks/tools"
            })
            
        except Exception as e:
            yield self.emit_progress("skills", "processing", {"message": f"⚠️ Error extracting frameworks: {str(e)}"})
        
        # Combine all skills (even if one extraction failed)
        all_skills = languages + frameworks
        skills_data = {"skills": all_skills}
        self.candidate_data.update(skills_data)
        
        if all_skills:
            yield self.emit_progress("skills", "completed", skills_data)
        else:
            yield self.emit_progress("skills", "error", error="No skills could be extracted")
    
    def extract_experience_micro(self) -> Generator[Dict[str, Any], None, None]:
        """Extract experience one job at a time."""
        yield self.emit_progress("experience", "starting")
        time.sleep(0.1)
        
        yield self.emit_progress("experience", "processing", {"message": "🏢 Finding number of jobs..."})
        
        # First, find how many jobs  
        prompt = f"""Look at this CV and count ONLY the number of different work positions/jobs.

{self.cv_text[:2000]}

Count only professional work positions (not education, projects, or certifications).
Return ONLY a single digit number. Examples:
- If you see 2 jobs: 2
- If you see 4 jobs: 4

Your response must be ONLY ONE NUMBER:"""
        
        try:
            job_count_str = self.query_claude_micro(prompt, timeout=20)
            # Extract just the number from the response
            import re
            numbers = re.findall(r'\d+', job_count_str.strip())
            job_count = int(numbers[0]) if numbers else 3  # Default to 3 if no number found
            
            yield self.emit_progress("experience", "processing", {"message": f"📊 Found {job_count} work positions"})
            
            # Extract each job one by one
            experience_list = []
            
            for i in range(min(job_count, 5)):  # Limit to 5 jobs max
                yield self.emit_progress("experience", "processing", {"message": f"📝 Extracting job #{i+1}..."})
                
                prompt = f"""Extract job #{i+1} from this CV and return as JSON:

{self.cv_text}

Return format:
{{
  "company": "Company Name",
  "position": "Job Title",
  "dates": "Date Range",
  "description": "Brief description"
}}

Return ONLY the JSON for job #{i+1}."""
                
                try:
                    job_str = self.query_claude_micro(prompt, timeout=20)
                    job_data = json.loads(job_str)
                    experience_list.append(job_data)
                    
                    yield self.emit_progress("experience", "processing", {
                        "partial_data": {"current_job": job_data},
                        "message": f"✅ Added: {job_data.get('position', 'Unknown')} at {job_data.get('company', 'Unknown')}"
                    })
                    
                    time.sleep(0.3)
                    
                except Exception as e:
                    yield self.emit_progress("experience", "processing", {"message": f"⚠️ Could not extract job #{i+1}: {str(e)}"})
            
            # Save experience data even if some jobs failed
            experience_data = {"experience": experience_list}
            self.candidate_data.update(experience_data)
            
            if experience_list:
                yield self.emit_progress("experience", "completed", experience_data)
            else:
                yield self.emit_progress("experience", "error", error="No work experience could be extracted")
            
        except Exception as e:
            yield self.emit_progress("experience", "error", error=str(e))
    
    def extract_education_micro(self) -> Generator[Dict[str, Any], None, None]:
        """Extract education quickly."""
        yield self.emit_progress("education", "starting")
        time.sleep(0.1)
        
        yield self.emit_progress("education", "processing", {"message": "🎓 Finding education details..."})
        
        prompt = f"""Extract education information from this CV and return as JSON:

{self.cv_text[:1500]}

Return format:
{{
  "education": [
    {{
      "institution": "University Name",
      "degree": "Degree Name", 
      "dates": "Date Range"
    }}
  ]
}}

Return ONLY the JSON."""

        try:
            education_str = self.query_claude_micro(prompt, timeout=20)
            education_data = json.loads(education_str)
            
            self.candidate_data.update(education_data)
            
            edu_count = len(education_data.get('education', []))
            yield self.emit_progress("education", "processing", {"message": f"✅ Found {edu_count} education entries"})
            
            yield self.emit_progress("education", "completed", education_data)
            
        except Exception as e:
            yield self.emit_progress("education", "error", error=str(e))
    
    def finalize_micro(self) -> Generator[Dict[str, Any], None, None]:
        """Quick finalization."""
        yield self.emit_progress("finalize", "starting")
        
        yield self.emit_progress("finalize", "processing", {"message": "💾 Saving candidate profile..."})
        time.sleep(0.2)
        
        try:
            # Add contact_info structure
            contact_info = {
                "email": self.candidate_data.get('email'),
                "phone": self.candidate_data.get('phone'),
                "linkedin": None,
                "github": None
            }
            
            self.candidate_data['contact_info'] = contact_info
            
            # Save to file
            output_dir = Path("parsed")
            output_dir.mkdir(exist_ok=True)
            
            filename_stem = Path(self.filename).stem
            json_file = output_dir / f"{filename_stem}_structured.json"
            
            with open(json_file, 'w') as f:
                json.dump(self.candidate_data, f, indent=2)
            
            yield self.emit_progress("finalize", "completed", {
                "candidate_data": self.candidate_data,
                "file_saved": str(json_file),
                "message": "🎉 CV parsing completed!"
            })
            
        except Exception as e:
            yield self.emit_progress("finalize", "error", error=str(e))
    
    def parse_micro_progressive(self) -> Generator[Dict[str, Any], None, None]:
        """Run micro-progressive parsing."""
        yield from self.extract_basic_info_micro()
        time.sleep(0.2)
        
        yield from self.extract_skills_micro()
        time.sleep(0.2)
        
        yield from self.extract_experience_micro()
        time.sleep(0.2)
        
        yield from self.extract_education_micro()
        time.sleep(0.2)
        
        yield from self.finalize_micro()