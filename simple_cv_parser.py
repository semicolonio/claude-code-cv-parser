#!/usr/bin/env python3
"""Simplified CV parser using Claude Code SDK without MCP server."""

import json
import shutil
from pathlib import Path
from typing import Optional

import anyio
from claude_code_sdk import (
    AssistantMessage,
    ClaudeCodeOptions,
    ResultMessage,
    TextBlock,
    query,
)

from models import CandidateProfile


class SimpleCVParser:
    """Simplified CV Parser using Claude Code SDK directly."""
    
    def __init__(self):
        self.uploads_dir = Path("uploads")
        self.parsed_dir = Path("parsed")
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure required directories exist."""
        self.uploads_dir.mkdir(exist_ok=True)
        self.parsed_dir.mkdir(exist_ok=True)
    
    def upload_cv(self, cv_file_path: str) -> str:
        """Upload a CV file to the processing directory."""
        source_path = Path(cv_file_path)
        
        if not source_path.exists():
            raise FileNotFoundError(f"CV file not found: {cv_file_path}")
        
        # Copy file to uploads directory
        destination = self.uploads_dir / source_path.name
        shutil.copy2(source_path, destination)
        
        print(f"✅ CV uploaded: {source_path.name}")
        return source_path.name
    
    def read_cv_content(self, cv_filename: str) -> str:
        """Read CV content from file."""
        cv_path = self.uploads_dir / cv_filename
        
        if cv_path.suffix.lower() == '.txt':
            return cv_path.read_text(encoding='utf-8')
        
        # For now, only support text files in the simple version
        # You can extend this to support PDF/DOCX later
        raise ValueError(f"Unsupported file format: {cv_path.suffix}")
    
    async def parse_cv_with_claude(self, cv_filename: str) -> Optional[CandidateProfile]:
        """Parse CV using Claude Code SDK directly."""
        
        # Read CV content
        try:
            cv_content = self.read_cv_content(cv_filename)
        except Exception as e:
            print(f"❌ Error reading CV: {e}")
            return None
        
        # Configure Claude Code options
        options = ClaudeCodeOptions(
            system_prompt="""You are an expert CV parser. Extract structured candidate information from the provided CV text.

Return the extracted information as a JSON object that matches this structure:
{
  "name": "Full Name",
  "contact_info": {
    "email": "email@example.com",
    "phone": "phone number",
    "linkedin": "linkedin url",
    "github": "github url",
    "portfolio": "portfolio url",
    "address": "address"
  },
  "summary": "professional summary",
  "skills": ["skill1", "skill2", "skill3"],
  "experience": [
    {
      "company": "Company Name",
      "position": "Job Title",
      "start_date": "YYYY or MM/YYYY",
      "end_date": "YYYY or MM/YYYY or Present",
      "is_current": false,
      "description": "job description",
      "achievements": ["achievement1", "achievement2"]
    }
  ],
  "education": [
    {
      "institution": "University Name",
      "degree": "Degree Name",
      "field_of_study": "Field",
      "start_date": "YYYY",
      "end_date": "YYYY",
      "gpa": "GPA if available",
      "achievements": ["achievement1"]
    }
  ],
  "projects": [
    {
      "name": "Project Name",
      "description": "Project description",
      "technologies": ["tech1", "tech2"],
      "url": "project url if available",
      "date": "project date"
    }
  ],
  "certifications": [
    {
      "name": "Certification Name",
      "issuer": "Issuing Organization",
      "date_issued": "YYYY",
      "expiry_date": "YYYY if applicable",
      "credential_id": "ID if available"
    }
  ],
  "languages": ["language1", "language2"]
}

Be thorough and extract all available information. If a field is not present, use null or empty array as appropriate.""",
            max_turns=3,
        )
        
        prompt = f"""Please parse this CV and extract all candidate information as JSON:

CV Content:
{cv_content}

Please provide ONLY the JSON response, no additional text or explanation."""

        print(f"🤖 Parsing CV with Claude: {cv_filename}")
        
        json_response = ""
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        json_response += block.text
            
            elif isinstance(message, ResultMessage):
                if hasattr(message, 'cost_usd') and message.cost_usd > 0:
                    print(f"💰 Cost: ${message.cost_usd:.4f}")
                else:
                    print("✅ Query completed")
        
        # Parse the JSON response
        try:
            # Clean up the response to extract just the JSON
            json_response = json_response.strip()
            
            # Find JSON boundaries
            if '{' in json_response:
                start = json_response.find('{')
                end = json_response.rfind('}') + 1
                json_str = json_response[start:end]
                
                candidate_dict = json.loads(json_str)
                candidate_profile = CandidateProfile(**candidate_dict)
                
                print(f"✅ Successfully parsed candidate: {candidate_profile.name}")
                return candidate_profile
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ Error parsing JSON response: {e}")
            print(f"Raw response: {json_response}")
        
        return None
    
    def save_parsed_data(self, candidate_profile: CandidateProfile, cv_filename: str) -> str:
        """Save parsed candidate profile to JSON file."""
        cv_name = Path(cv_filename).stem
        output_filename = f"{cv_name}_parsed.json"
        output_path = self.parsed_dir / output_filename
        
        with open(output_path, 'w') as f:
            f.write(candidate_profile.model_dump_json(indent=2))
        
        print(f"💾 Saved parsed data: {output_path}")
        return str(output_path)
    
    async def process_cv(self, cv_file_path: str) -> Optional[str]:
        """Complete CV processing pipeline."""
        try:
            # Step 1: Upload CV
            cv_filename = self.upload_cv(cv_file_path)
            
            # Step 2: Parse with Claude
            candidate_profile = await self.parse_cv_with_claude(cv_filename)
            
            if candidate_profile:
                # Step 3: Save parsed data
                output_path = self.save_parsed_data(candidate_profile, cv_filename)
                
                print("\n✨ CV Processing Complete!")
                print(f"📄 Original CV: {cv_file_path}")
                print(f"👤 Candidate: {candidate_profile.name}")
                print(f"📧 Email: {candidate_profile.contact_info.email}")
                print(f"💼 Experience entries: {len(candidate_profile.experience)}")
                print(f"🎓 Education entries: {len(candidate_profile.education)}")
                print(f"🛠️  Skills: {len(candidate_profile.skills)}")
                print(f"💾 Parsed data saved to: {output_path}")
                
                return output_path
            else:
                print("❌ Failed to parse CV - no candidate data extracted")
                return None
                
        except Exception as e:
            print(f"❌ Error processing CV: {e}")
            return None


async def main():
    """Main function for testing."""
    parser = SimpleCVParser()
    result = await parser.process_cv("sample_cv.txt")
    
    if result:
        print(f"\n🎉 Success! Check the parsed result at: {result}")
    else:
        print("\n💥 Processing failed")


if __name__ == "__main__":
    anyio.run(main)