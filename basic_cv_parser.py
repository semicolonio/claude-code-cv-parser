#!/usr/bin/env python3
"""Basic CV parser using Claude Code SDK - minimal version."""

import json
import sys
from pathlib import Path
from typing import Optional

import anyio
from claude_code_sdk import query, ClaudeCodeOptions
from models import CandidateProfile


async def parse_cv_file(cv_file_path: str) -> Optional[dict]:
    """Parse CV file and return candidate data as dictionary."""
    
    # Read the CV content
    cv_path = Path(cv_file_path)
    if not cv_path.exists():
        print(f"❌ File not found: {cv_file_path}")
        return None
    
    if cv_path.suffix.lower() != '.txt':
        print(f"❌ Only .txt files supported in this basic version")
        return None
    
    cv_content = cv_path.read_text(encoding='utf-8')
    print(f"📄 Reading CV: {cv_path.name}")
    
    # Configure Claude options
    options = ClaudeCodeOptions(
        system_prompt="You are a CV parser. Extract candidate information and return it as clean JSON only.",
        max_turns=1,
    )
    
    prompt = f"""Extract candidate information from this CV and return ONLY a JSON object with this structure:

{{
  "name": "candidate name",
  "contact_info": {{
    "email": "email@example.com",
    "phone": "phone number",
    "linkedin": "linkedin url",
    "github": "github url"
  }},
  "summary": "professional summary",
  "skills": ["skill1", "skill2"],
  "experience": [
    {{
      "company": "Company Name",
      "position": "Job Title",
      "start_date": "2021",
      "end_date": "Present",
      "is_current": true,
      "description": "job description"
    }}
  ],
  "education": [
    {{
      "institution": "University",
      "degree": "Degree",
      "field_of_study": "Field",
      "start_date": "2014",
      "end_date": "2018"
    }}
  ],
  "projects": [],
  "certifications": [],
  "languages": ["English"]
}}

CV Content:
{cv_content}

Return ONLY the JSON, no other text."""

    print("🤖 Processing with Claude...")
    
    response_text = ""
    try:
        async for message in query(prompt=prompt, options=options):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        response_text += block.text
    except Exception as e:
        print(f"❌ Error during query: {e}")
        return None
    
    # Extract JSON from response
    try:
        # Find JSON boundaries
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start >= 0 and end > start:
            json_str = response_text[start:end]
            candidate_data = json.loads(json_str)
            print(f"✅ Extracted data for: {candidate_data.get('name', 'Unknown')}")
            return candidate_data
        else:
            print(f"❌ No JSON found in response")
            print(f"Response: {response_text}")
            return None
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"Response: {response_text}")
        return None


async def main():
    """Main function."""
    if len(sys.argv) > 1:
        cv_file = sys.argv[1]
    else:
        cv_file = "sample_cv.txt"
    
    print(f"🚀 Parsing CV: {cv_file}")
    
    candidate_data = await parse_cv_file(cv_file)
    
    if candidate_data:
        # Save to file
        output_file = Path("parsed") / f"{Path(cv_file).stem}_parsed.json"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(candidate_data, f, indent=2)
        
        print(f"💾 Saved to: {output_file}")
        
        # Print summary
        print(f"\n📊 Summary:")
        print(f"   Name: {candidate_data.get('name', 'N/A')}")
        print(f"   Email: {candidate_data.get('contact_info', {}).get('email', 'N/A')}")
        print(f"   Skills: {len(candidate_data.get('skills', []))}")
        print(f"   Experience: {len(candidate_data.get('experience', []))}")
        print(f"   Education: {len(candidate_data.get('education', []))}")
    else:
        print("💥 Failed to parse CV")


if __name__ == "__main__":
    anyio.run(main)