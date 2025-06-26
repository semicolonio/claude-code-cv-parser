#!/usr/bin/env python3
"""Main application for CV parsing using Claude Code SDK with MCP server."""

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


class CVParserApp:
    """CV Parser application using Claude Code SDK."""
    
    def __init__(self):
        self.uploads_dir = Path("uploads")
        self.parsed_dir = Path("parsed")
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure required directories exist."""
        self.uploads_dir.mkdir(exist_ok=True)
        self.parsed_dir.mkdir(exist_ok=True)
    
    async def upload_cv(self, cv_file_path: str) -> str:
        """Upload a CV file to the processing directory."""
        source_path = Path(cv_file_path)
        
        if not source_path.exists():
            raise FileNotFoundError(f"CV file not found: {cv_file_path}")
        
        # Copy file to uploads directory
        destination = self.uploads_dir / source_path.name
        shutil.copy2(source_path, destination)
        
        print(f"✅ CV uploaded: {source_path.name}")
        return source_path.name
    
    async def parse_cv_with_claude(self, cv_filename: str) -> Optional[CandidateProfile]:
        """Parse CV using Claude Code SDK with MCP server tools."""
        
        # Configure Claude Code options with MCP server tools
        options = ClaudeCodeOptions(
            system_prompt="""You are an expert CV parser. Your job is to extract structured candidate information from CV text.

You have access to specialized CV parsing tools through the MCP server. Use these tools to:
1. Read the CV file content
2. Extract contact information, experience, education, skills, and other relevant data
3. Structure the information according to the CandidateProfile model

Be thorough and accurate in your extraction. Pay attention to:
- Names, contact details (email, phone, LinkedIn, etc.)
- Work experience with companies, positions, dates, and descriptions
- Education with institutions, degrees, dates
- Technical and soft skills
- Projects and achievements
- Certifications and languages

Provide the extracted information in a structured JSON format that matches the CandidateProfile model.""",
            max_turns=5,
        )
        
        prompt = f"""Please parse the CV file '{cv_filename}' and extract all candidate information.

Follow these steps:
1. Read the CV content from the file
2. Extract and structure all relevant information
3. Return the complete candidate profile as JSON

The CV file is located in the uploads directory. Please be thorough and extract all available information."""

        print(f"🤖 Parsing CV with Claude: {cv_filename}")
        
        candidate_data = None
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")
                        
                        # Try to extract JSON from Claude's response
                        try:
                            # Look for JSON in the response
                            text = block.text
                            if '{' in text and '}' in text:
                                # Extract the JSON part
                                start = text.find('{')
                                end = text.rfind('}') + 1
                                json_str = text[start:end]
                                
                                candidate_dict = json.loads(json_str)
                                candidate_data = CandidateProfile(**candidate_dict)
                        except (json.JSONDecodeError, ValueError) as e:
                            print(f"⚠️  Could not parse candidate data: {e}")
            
            elif isinstance(message, ResultMessage):
                # Check if cost information is available
                if hasattr(message, 'cost_usd') and message.cost_usd > 0:
                    print(f"💰 Cost: ${message.cost_usd:.4f}")
                elif hasattr(message, 'usage'):
                    print(f"📊 Usage: {message.usage}")
                else:
                    print("✅ Query completed")
        
        return candidate_data
    
    async def save_parsed_data(self, candidate_profile: CandidateProfile, cv_filename: str) -> str:
        """Save parsed candidate profile to JSON file."""
        # Create output filename based on original CV filename
        cv_name = Path(cv_filename).stem
        output_filename = f"{cv_name}_parsed.json"
        output_path = self.parsed_dir / output_filename
        
        # Save as JSON
        with open(output_path, 'w') as f:
            f.write(candidate_profile.model_dump_json(indent=2))
        
        print(f"💾 Saved parsed data: {output_path}")
        return str(output_path)
    
    async def process_cv(self, cv_file_path: str) -> Optional[str]:
        """Complete CV processing pipeline."""
        try:
            # Step 1: Upload CV
            cv_filename = await self.upload_cv(cv_file_path)
            
            # Step 2: Parse with Claude
            candidate_profile = await self.parse_cv_with_claude(cv_filename)
            
            if candidate_profile:
                # Step 3: Save parsed data
                output_path = await self.save_parsed_data(candidate_profile, cv_filename)
                
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
    """Main application entry point."""
    print("🚀 CV Parser App - Using Claude Code SDK with MCP Server")
    print("=" * 60)
    
    app = CVParserApp()
    
    # Example usage - you can modify this to accept command line arguments
    # or create a web interface
    
    # For demo purposes, let's use the sample CV
    sample_cv_path = "sample_cv.txt"  # You would replace this with actual CV path
    
    if Path(sample_cv_path).exists():
        result = await app.process_cv(sample_cv_path)
        if result:
            print(f"\n🎉 Success! Parsed CV saved to: {result}")
        else:
            print("\n💥 Failed to process CV")
    else:
        print(f"⚠️  Sample CV not found: {sample_cv_path}")
        print("\nTo use this app:")
        print("1. Place your CV file in the current directory")
        print("2. Update the sample_cv_path variable with your CV filename")
        print("3. Run the app again")


if __name__ == "__main__":
    anyio.run(main)