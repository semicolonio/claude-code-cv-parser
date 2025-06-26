#!/usr/bin/env python3
"""Final working CV parser using Claude CLI with proper permissions."""

import json
import subprocess
import sys
from pathlib import Path


def parse_cv_with_claude(cv_file_path: str):
    """Parse CV using Claude CLI with permissions handled."""
    
    # Read CV file
    cv_path = Path(cv_file_path)
    if not cv_path.exists():
        print(f"❌ File not found: {cv_file_path}")
        return
    
    cv_content = cv_path.read_text(encoding='utf-8')
    print(f"📄 Processing CV: {cv_path.name}")
    
    # Create a focused parsing prompt
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

    print("🤖 Processing with Claude...")
    
    try:
        # Use Claude CLI with --dangerously-skip-permissions for automation
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
                # Try to extract JSON from response
                try:
                    # Look for JSON in the response
                    start = response.find('{')
                    end = response.rfind('}') + 1
                    
                    if start >= 0 and end > start:
                        json_str = response[start:end]
                        candidate_data = json.loads(json_str)
                        
                        # Save structured data
                        output_dir = Path("parsed")
                        output_dir.mkdir(exist_ok=True)
                        
                        json_file = output_dir / f"{cv_path.stem}_structured.json"
                        with open(json_file, 'w') as f:
                            json.dump(candidate_data, f, indent=2)
                        
                        # Save full response
                        text_file = output_dir / f"{cv_path.stem}_analysis.txt"
                        with open(text_file, 'w') as f:
                            f.write(f"CV Analysis: {cv_path.name}\n")
                            f.write("=" * 50 + "\n\n")
                            f.write(response)
                        
                        # Display summary
                        print(f"\n✅ Successfully parsed CV!")
                        print(f"👤 Name: {candidate_data.get('name', 'N/A')}")
                        print(f"📧 Email: {candidate_data.get('email', 'N/A')}")
                        print(f"📱 Phone: {candidate_data.get('phone', 'N/A')}")
                        print(f"🛠️  Skills: {len(candidate_data.get('skills', []))} skills found")
                        print(f"💼 Experience: {len(candidate_data.get('experience', []))} positions")
                        print(f"🎓 Education: {len(candidate_data.get('education', []))} entries")
                        
                        print(f"\n💾 Files saved:")
                        print(f"   JSON: {json_file}")
                        print(f"   Analysis: {text_file}")
                        
                        return candidate_data
                        
                    else:
                        print("❌ No valid JSON found in response")
                        print(f"Response: {response}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing error: {e}")
                    print(f"Response: {response}")
            else:
                print(f"❌ Error in response: {response}")
                print(f"stderr: {result.stderr}")
        else:
            print(f"❌ CLI error (code {result.returncode}): {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Processing timed out (2 minutes)")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    return None


def main():
    """Main function."""
    if len(sys.argv) > 1:
        cv_file = sys.argv[1]
    else:
        cv_file = "sample_cv.txt"
    
    print("🚀 CV Parser - Claude CLI Edition")
    print("=" * 45)
    
    result = parse_cv_with_claude(cv_file)
    
    if result:
        print("\n🎉 CV parsing completed successfully!")
    else:
        print("\n💥 CV parsing failed")


if __name__ == "__main__":
    main()