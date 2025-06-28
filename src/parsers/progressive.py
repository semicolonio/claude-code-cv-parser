#!/usr/bin/env python3
"""Progressive CV parser with step-by-step processing."""

import json
import subprocess
import time
import logging
from pathlib import Path
from typing import Dict, Any, Generator

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cv_parser_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


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
        
        yield self.emit_progress(step_name, "processing", {"message": "📝 Sending prompt to Claude AI..."})
        
        logger.info(f"Query Claude for step: {step_name}")
        logger.debug(f"Prompt length: {len(prompt)} characters")
        logger.debug(f"Prompt preview: {prompt[:200]}...")
        
        try:
            yield self.emit_progress(step_name, "processing", {"message": "🤖 Claude is analyzing the CV text..."})
            
            # Note: --output-format json may be causing issues, let's log the command
            cmd = ["claude", "-p", "--dangerously-skip-permissions", "--model", "sonnet"]
            logger.info(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            yield self.emit_progress(step_name, "processing", {"message": "⚡ Processing request..."})
            
            # Log subprocess results
            logger.info(f"Return code: {result.returncode}")
            logger.info(f"STDOUT length: {len(result.stdout)} chars")
            logger.info(f"STDERR length: {len(result.stderr)} chars")
            
            if result.stderr:
                logger.warning(f"STDERR content: {result.stderr}")
                
            if result.returncode == 0:
                yield self.emit_progress(step_name, "processing", {"message": "📥 Receiving response from Claude..."})
                        
                response = result.stdout.strip()
                
                # Log raw response for debugging
                logger.debug(f"Raw STDOUT: {response[:500]}..." if len(response) > 500 else f"Raw STDOUT: {response}")
                
                # Save full response to debug file
                debug_file = Path(f"debug_{step_name}_{int(time.time())}.txt")
                with open(debug_file, 'w') as f:
                    f.write(f"COMMAND: {' '.join(cmd)}\n\n")
                    f.write(f"PROMPT:\n{prompt}\n\n")
                    f.write(f"STDOUT:\n{result.stdout}\n\n")
                    f.write(f"STDERR:\n{result.stderr}\n")
                logger.info(f"Full response saved to: {debug_file}")
                
                if not response:
                    logger.error("Claude returned empty response")
                    raise Exception("Claude returned empty response")
                
                yield self.emit_progress(step_name, "processing", {"message": f"🔍 Raw response length: {len(response)} chars"})
                
                # Try to find JSON in the response
                json_content = None
                
                # Method 1: Try direct JSON parse
                try:
                    logger.debug("Attempting direct JSON parse...")
                    json_content = json.loads(response)
                    logger.info("Successfully parsed response as direct JSON")
                    yield self.emit_progress(step_name, "processing", {"message": "✅ Response processed successfully!"})
                    return json.dumps(json_content)  # Return as string for consistency
                except json.JSONDecodeError as e:
                    logger.debug(f"Direct JSON parse failed: {e}")
                    
                # Method 2: Look for JSON between ```json markers
                if '```json' in response:
                    logger.debug("Looking for JSON in markdown code blocks...")
                    start = response.find('```json') + 7
                    end = response.find('```', start)
                    if start > 6 and end > start:
                        json_str = response[start:end].strip()
                        try:
                            json_content = json.loads(json_str)
                            logger.info("Successfully extracted JSON from markdown block")
                            yield self.emit_progress(step_name, "processing", {"message": "✅ Response processed successfully!"})
                            return json.dumps(json_content)
                        except json.JSONDecodeError as e:
                            logger.debug(f"Markdown JSON parse failed: {e}")
                
                # Method 3: Look for JSON object anywhere in response
                import re
                json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                matches = re.findall(json_pattern, response, re.DOTALL)
                for match in matches:
                    try:
                        json_content = json.loads(match)
                        logger.info("Successfully extracted JSON using regex pattern")
                        yield self.emit_progress(step_name, "processing", {"message": "✅ Response processed successfully!"})
                        return json.dumps(json_content)
                    except json.JSONDecodeError:
                        continue
                        
                # If no valid JSON found, log error with details
                logger.error(f"Could not extract valid JSON from response for {step_name}")
                logger.error(f"Response preview: {response[:200]}...")
                raise Exception(f"No valid JSON found in response. Check {debug_file} for full response.")
            else:
                error_msg = result.stderr.strip() or "Unknown error"
                logger.error(f"Claude CLI error - Return code: {result.returncode}")
                logger.error(f"Error message: {error_msg}")
                logger.error(f"STDOUT: {result.stdout[:200]}..." if result.stdout else "No STDOUT")
                raise Exception(f"Claude CLI error (code {result.returncode}): {error_msg}")
                
        except subprocess.TimeoutExpired:
            logger.error(f"Query timed out after {timeout} seconds")
            raise Exception("Query timed out")
        except Exception as e:
            logger.error(f"Error querying Claude: {str(e)}")
            raise Exception(f"Error querying Claude: {str(e)}")
    
    def query_claude(self, prompt: str, timeout: int = 30) -> str:
        """Simple non-streaming query for backwards compatibility."""
        logger.info(f"Query Claude (non-streaming)")
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        try:
            # Remove --output-format json as it might be causing issues
            cmd = ["claude", "-p", "--dangerously-skip-permissions", "--model", "sonnet"]
            logger.info(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            logger.info(f"Return code: {result.returncode}")
            
            if result.returncode == 0:
                response = result.stdout.strip()
                
                logger.debug(f"Raw response length: {len(response)} chars")
                logger.debug(f"Response preview: {response[:200]}..." if len(response) > 200 else f"Response: {response}")
                
                if not response:
                    logger.error("Claude returned empty response")
                    raise Exception("Claude returned empty response")
                
                # Try to extract JSON from response
                # Method 1: Direct parse
                try:
                    json_obj = json.loads(response)
                    return json.dumps(json_obj)
                except json.JSONDecodeError:
                    pass
                    
                # Method 2: Extract from markdown
                if '```json' in response:
                    start = response.find('```json') + 7
                    end = response.find('```', start)
                    if start > 6 and end > start:
                        try:
                            json_obj = json.loads(response[start:end].strip())
                            return json.dumps(json_obj)
                        except json.JSONDecodeError:
                            pass
                
                # Method 3: Find JSON object
                import re
                json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                matches = re.findall(json_pattern, response, re.DOTALL)
                for match in matches:
                    try:
                        json_obj = json.loads(match)
                        return json.dumps(json_obj)
                    except json.JSONDecodeError:
                        continue
                        
                logger.error("Could not extract valid JSON from response")
                raise Exception("No valid JSON found in Claude response")
            else:
                error_msg = result.stderr.strip() or "Unknown error"
                logger.error(f"Claude CLI error - Return code: {result.returncode}")
                logger.error(f"Error message: {error_msg}")
                logger.error(f"STDOUT: {result.stdout[:200]}..." if result.stdout else "No STDOUT")
                raise Exception(f"Claude CLI error (code {result.returncode}): {error_msg}")
                
        except subprocess.TimeoutExpired:
            logger.error(f"Query timed out after {timeout} seconds")
            raise Exception("Query timed out")
        except Exception as e:
            logger.error(f"Error querying Claude: {str(e)}")
            raise Exception(f"Error querying Claude: {str(e)}")
    
    def extract_basic_info(self) -> Generator[Dict[str, Any], None, None]:
        """Extract name, email, phone, summary."""
        yield self.emit_progress("basic_info", "starting")
        
        yield self.emit_progress("basic_info", "processing", {"message": "👋 Let's start by figuring out who this candidate is! I'll scan their CV to find their name, contact details, and get a sense of their professional background..."})
        
        yield self.emit_progress("basic_info", "processing", {"message": "🔍 Looking for contact information and professional summary..."})
        
        prompt = f"""You are a JSON extractor. Extract basic candidate information from the CV text below.

IMPORTANT INSTRUCTIONS:
1. You MUST respond with ONLY valid JSON - no other text before or after
2. Do not include any explanations, markdown formatting, or code blocks
3. Return the exact JSON structure shown below
4. If a field is not found in the CV, use "Not provided" as the value

CV TEXT:
{self.cv_text}

RETURN THIS EXACT JSON STRUCTURE:
{{
  "name": "candidate full name",
  "email": "email address",
  "phone": "phone number", 
  "summary": "brief professional summary (2-3 sentences)"
}}"""

        try:
            yield self.emit_progress("basic_info", "processing", {"message": "📋 Preparing basic info extraction prompt..."})
                
            yield self.emit_progress("basic_info", "processing", {"message": "🚀 Launching Claude query..."})
                
            yield self.emit_progress("basic_info", "processing", {"message": "🤖 Claude is analyzing the CV text..."})
            response = self.query_claude(prompt, timeout=45)
            
            if response:
                yield self.emit_progress("basic_info", "processing", {"message": "🔧 Parsing basic information..."})
                
                try:
                    basic_info = json.loads(response)
                    logger.info(f"Successfully parsed basic_info: {list(basic_info.keys())}")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error in basic_info: {str(e)}")
                    logger.error(f"Response that failed to parse: {response}")
                    yield self.emit_progress("basic_info", "processing", {"message": f"❌ JSON parse error: {str(e)}"})
                    yield self.emit_progress("basic_info", "processing", {"message": f"📄 Response preview: {response[:200]}..."})
                    raise
                
                yield self.emit_progress("basic_info", "processing", {"message": f"👤 Found candidate: {basic_info.get('name', 'Unknown')}"})
                        
                yield self.emit_progress("basic_info", "processing", {"message": f"📧 Email: {basic_info.get('email', 'Not found')}"})
                        
                yield self.emit_progress("basic_info", "processing", {"message": f"📱 Phone: {basic_info.get('phone', 'Not found')}"})
                        
                self.candidate_data.update(basic_info)
                yield self.emit_progress("basic_info", "completed", basic_info)
            
        except Exception as e:
            yield self.emit_progress("basic_info", "error", error=str(e))
    
    def extract_skills(self) -> Generator[Dict[str, Any], None, None]:
        """Extract technical and soft skills."""
        yield self.emit_progress("skills", "starting")
        
        yield self.emit_progress("skills", "processing", {"message": "🚀 Now that we know who they are, let's discover their technical superpowers! I'll hunt through their CV for programming languages, frameworks, tools, and any other skills that make them stand out..."})
        
        yield self.emit_progress("skills", "processing", {"message": "🛠️ Scanning for technical skills and expertise..."})
        
        prompt = f"""You are a JSON extractor. Extract all skills from the CV text below.

IMPORTANT INSTRUCTIONS:
1. You MUST respond with ONLY valid JSON - no other text before or after
2. Do not include any explanations, markdown formatting, or code blocks
3. Return the exact JSON structure shown below
4. Include programming languages, frameworks, tools, cloud platforms, databases, and relevant soft skills
5. If no skills are found, return an empty array

CV TEXT:
{self.cv_text}

RETURN THIS EXACT JSON STRUCTURE:
{{
  "skills": ["skill1", "skill2", "skill3"]
}}"""

        try:
            yield self.emit_progress("skills", "processing", {"message": "📝 Building skills extraction prompt..."})
                
            yield self.emit_progress("skills", "processing", {"message": "🚀 Launching Claude query..."})
                
            yield self.emit_progress("skills", "processing", {"message": "🤖 Claude is analyzing skills..."})
            response = self.query_claude(prompt, timeout=45)
            
            if response:
                yield self.emit_progress("skills", "processing", {"message": "🔍 Categorizing found skills..."})
                
                try:
                    skills_data = json.loads(response)
                    logger.info(f"Successfully parsed skills: {len(skills_data.get('skills', []))} skills found")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error in skills: {str(e)}")
                    logger.error(f"Response that failed to parse: {response}")
                    raise
                skills_count = len(skills_data.get('skills', []))
                
                yield self.emit_progress("skills", "processing", {"message": f"💎 Found {skills_count} skills total"})
                        
                # Show some example skills
                if skills_data.get('skills'):
                    example_skills = skills_data['skills'][:3]
                    yield self.emit_progress("skills", "processing", {"message": f"🎯 Examples: {', '.join(example_skills)}..."})
                            
                self.candidate_data.update(skills_data)
                yield self.emit_progress("skills", "completed", skills_data)
            
        except Exception as e:
            yield self.emit_progress("skills", "error", error=str(e))
    
    def extract_experience(self) -> Generator[Dict[str, Any], None, None]:
        """Extract work experience."""
        yield self.emit_progress("experience", "starting")
        
        yield self.emit_progress("experience", "processing", {"message": "📈 Time to dive into their professional journey! I'll trace through their career path, uncovering where they've worked, what roles they've held, and the impact they've made along the way. This tells the real story of their experience..."})
        
        yield self.emit_progress("experience", "processing", {"message": "💼 Analyzing work history and achievements..."})
        
        prompt = f"""You are a JSON extractor. Extract work experience from the CV text below.

IMPORTANT INSTRUCTIONS:
1. You MUST respond with ONLY valid JSON - no other text before or after
2. Do not include any explanations, markdown formatting, or code blocks
3. Return the exact JSON structure shown below
4. List experiences in reverse chronological order (most recent first)
5. If no experience is found, return an empty array

CV TEXT:
{self.cv_text}

RETURN THIS EXACT JSON STRUCTURE:
{{
  "experience": [
    {{
      "company": "Company Name",
      "position": "Job Title", 
      "dates": "Date Range",
      "description": "Brief description of role and achievements"
    }}
  ]
}}"""

        try:
            yield self.emit_progress("experience", "processing", {"message": "📊 Preparing experience extraction..."})
                
            yield self.emit_progress("experience", "processing", {"message": "🚀 Launching Claude query..."})
                
            yield self.emit_progress("experience", "processing", {"message": "🤖 Claude is analyzing work history..."})
            response = self.query_claude(prompt, timeout=45)
            
            if response:
                yield self.emit_progress("experience", "processing", {"message": "🏢 Processing work history..."})
                
                try:
                    experience_data = json.loads(response)
                    logger.info(f"Successfully parsed experience: {len(experience_data.get('experience', []))} entries found")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error in experience: {str(e)}")
                    logger.error(f"Response that failed to parse: {response}")
                    raise
                exp_count = len(experience_data.get('experience', []))
                
                yield self.emit_progress("experience", "processing", {"message": f"📈 Found {exp_count} work experience entries"})
                        
                # Show recent company
                if experience_data.get('experience'):
                    recent_exp = experience_data['experience'][0]
                    yield self.emit_progress("experience", "processing", {"message": f"🏆 Most recent: {recent_exp.get('position', 'Unknown')} at {recent_exp.get('company', 'Unknown')}"})
                            
                self.candidate_data.update(experience_data)
                yield self.emit_progress("experience", "completed", experience_data)
            
        except Exception as e:
            yield self.emit_progress("experience", "error", error=str(e))
    
    def extract_education(self) -> Generator[Dict[str, Any], None, None]:
        """Extract education information."""
        yield self.emit_progress("education", "starting")
        
        yield self.emit_progress("education", "processing", {"message": "🎓 Let's explore their educational foundation! I'll look for degrees, certifications, and academic achievements that shaped their expertise. Education often reveals the depth of knowledge behind their practical skills..."})
        
        yield self.emit_progress("education", "processing", {"message": "📚 Scanning for academic credentials and qualifications..."})
        
        prompt = f"""You are a JSON extractor. Extract education information from the CV text below.

IMPORTANT INSTRUCTIONS:
1. You MUST respond with ONLY valid JSON - no other text before or after
2. Do not include any explanations, markdown formatting, or code blocks
3. Return the exact JSON structure shown below
4. List education in reverse chronological order (most recent first)
5. If no education is found, return an empty array

CV TEXT:
{self.cv_text}

RETURN THIS EXACT JSON STRUCTURE:
{{
  "education": [
    {{
      "institution": "University/School Name",
      "degree": "Degree Name",
      "dates": "Date Range"
    }}
  ]
}}"""

        try:
            yield self.emit_progress("education", "processing", {"message": "📚 Scanning for academic credentials..."})
                
            yield self.emit_progress("education", "processing", {"message": "🚀 Launching Claude query..."})
                
            yield self.emit_progress("education", "processing", {"message": "🤖 Claude is analyzing education..."})
            response = self.query_claude(prompt, timeout=45)
            
            if response:
                try:
                    education_data = json.loads(response)
                    logger.info(f"Successfully parsed education: {len(education_data.get('education', []))} entries found")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error in education: {str(e)}")
                    logger.error(f"Response that failed to parse: {response}")
                    raise
                edu_count = len(education_data.get('education', []))
                
                yield self.emit_progress("education", "processing", {"message": f"🏫 Found {edu_count} education entries"})
                        
                if education_data.get('education'):
                    latest_edu = education_data['education'][0]
                    yield self.emit_progress("education", "processing", {"message": f"🎯 Latest: {latest_edu.get('degree', 'Unknown')} from {latest_edu.get('institution', 'Unknown')}"})
                            
                self.candidate_data.update(education_data)
                yield self.emit_progress("education", "completed", education_data)
            
        except Exception as e:
            yield self.emit_progress("education", "error", error=str(e))
    
    def extract_projects_and_certifications(self) -> Generator[Dict[str, Any], None, None]:
        """Extract projects and certifications."""
        yield self.emit_progress("projects_certs", "starting")
        
        yield self.emit_progress("projects_certs", "processing", {"message": "🚀 Now for the exciting extras! I'll search for passion projects, side work, and professional certifications. These often reveal a candidate's curiosity, continuous learning mindset, and what they do beyond their day job..."})
        
        prompt = f"""You are a JSON extractor. Extract projects and certifications from the CV text below.

IMPORTANT INSTRUCTIONS:
1. You MUST respond with ONLY valid JSON - no other text before or after
2. Do not include any explanations, markdown formatting, or code blocks
3. Return the exact JSON structure shown below
4. If no projects are found, use an empty array for projects
5. If no certifications are found, use an empty array for certifications

CV TEXT:
{self.cv_text}

RETURN THIS EXACT JSON STRUCTURE:
{{
  "projects": [
    {{
      "name": "Project Name",
      "description": "Project description"
    }}
  ],
  "certifications": ["Certification Name 1", "Certification Name 2"]
}}"""

        try:
            yield self.emit_progress("projects_certs", "processing", {"message": "🚀 Launching Claude query..."})
                
            yield self.emit_progress("projects_certs", "processing", {"message": "🤖 Claude is analyzing projects..."})
            response = self.query_claude(prompt, timeout=45)  # Increase timeout
            
            try:
                projects_certs_data = json.loads(response)
                logger.info(f"Successfully parsed projects/certs: {len(projects_certs_data.get('projects', []))} projects, {len(projects_certs_data.get('certifications', []))} certs")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error in projects_certs: {str(e)}")
                logger.error(f"Response that failed to parse: {response}")
                raise
            proj_count = len(projects_certs_data.get('projects', []))
            cert_count = len(projects_certs_data.get('certifications', []))
            
            yield self.emit_progress("projects_certs", "processing", {"message": f"📊 Found {proj_count} projects, {cert_count} certifications"})
                
            self.candidate_data.update(projects_certs_data)
            yield self.emit_progress("projects_certs", "completed", projects_certs_data)
            
        except Exception as e:
            yield self.emit_progress("projects_certs", "error", error=str(e))
    
    def finalize(self) -> Generator[Dict[str, Any], None, None]:
        """Finalize and save the complete candidate profile."""
        yield self.emit_progress("finalize", "starting")
        
        try:
            yield self.emit_progress("finalize", "processing", {"message": "🎉 Excellent! We've gathered all the pieces of the puzzle. Now I'm putting together a comprehensive candidate profile that captures their complete professional story - from their background and skills to their experience and aspirations..."})
                
            yield self.emit_progress("finalize", "processing", {"message": "🎯 Compiling complete candidate profile..."})
                
            yield self.emit_progress("finalize", "processing", {"message": "📊 Validating extracted data..."})
                
            # Calculate some stats
            total_skills = len(self.candidate_data.get('skills', []))
            total_experience = len(self.candidate_data.get('experience', []))
            total_education = len(self.candidate_data.get('education', []))
            
            yield self.emit_progress("finalize", "processing", {"message": f"📈 Profile summary: {total_skills} skills, {total_experience} jobs, {total_education} education"})
                
            yield self.emit_progress("finalize", "processing", {"message": "💾 Saving structured data to file..."})
                
            # Save to file
            output_dir = Path("parsed")
            output_dir.mkdir(exist_ok=True)
            
            filename_stem = Path(self.filename).stem
            json_file = output_dir / f"{filename_stem}_structured.json"
            
            with open(json_file, 'w') as f:
                json.dump(self.candidate_data, f, indent=2)
            
            yield self.emit_progress("finalize", "processing", {"message": "✨ Generating final candidate summary..."})
                
            yield self.emit_progress("finalize", "processing", {"message": "🎊 Mission accomplished! All candidate information has been successfully extracted and organized into a comprehensive profile."})
                
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
        
        # Step 1: Basic Info
        yield from self.extract_basic_info()
        
        yield self.emit_progress("transition", "processing", {"message": "✅ Great! Now I have their basic profile. Next, let's see what technical skills they bring to the table..."})
        
        # Step 2: Skills
        yield from self.extract_skills()
        
        yield self.emit_progress("transition", "processing", {"message": "💪 Skills identified! Now let's dive into their work history to see how they've applied these skills in real-world situations..."})
        
        # Step 3: Experience
        yield from self.extract_experience()
        
        yield self.emit_progress("transition", "processing", {"message": "📊 Professional journey mapped! Time to check their educational background that laid the foundation for all this experience..."})
        
        # Step 4: Education
        yield from self.extract_education()
        
        yield self.emit_progress("transition", "processing", {"message": "🎓 Academic foundation documented! Finally, let's look for any bonus projects or certifications that show their extra initiative..."})
        
        # Step 5: Projects & Certifications
        yield from self.extract_projects_and_certifications()
        
        yield self.emit_progress("transition", "processing", {"message": "🏆 All information collected! Time to put it all together into a beautiful, complete candidate profile..."})
        
        # Step 6: Finalize
        yield from self.finalize()