#!/usr/bin/env python3
"""Working CV parser using Claude Code SDK - simplified approach."""

import json
import sys
from pathlib import Path

import anyio
from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, ResultMessage, TextBlock


async def parse_cv_simple(cv_file_path: str):
    """Parse CV file using Claude Code SDK."""
    
    # Read the CV content
    cv_path = Path(cv_file_path)
    if not cv_path.exists():
        print(f"❌ File not found: {cv_file_path}")
        return
    
    if cv_path.suffix.lower() != '.txt':
        print(f"❌ Only .txt files supported in this version")
        return
    
    cv_content = cv_path.read_text(encoding='utf-8')
    print(f"📄 Reading CV: {cv_path.name}")
    
    # Simple prompt for CV parsing
    prompt = f"""Extract and organize information from this CV:

{cv_content}

Format the output as:
NAME: [name]
EMAIL: [email]
PHONE: [phone]
LINKEDIN: [linkedin]
GITHUB: [github]

SUMMARY: [professional summary]

SKILLS: [list all skills]

EXPERIENCE:
- [Company] | [Position] | [Dates]
  [Description]

EDUCATION:
- [Institution] | [Degree] | [Dates]

PROJECTS:
- [Project name]: [Description]

CERTIFICATIONS:
- [Certification]: [Issuer] ([Date])

LANGUAGES: [languages]"""

    print("🤖 Processing with Claude...")
    
    # Process with Claude
    options = ClaudeCodeOptions(max_turns=1)
    
    full_response = ""
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    full_response += block.text
                    print(f"Claude: {block.text}")
        elif isinstance(message, ResultMessage):
            if hasattr(message, 'cost_usd') and message.cost_usd > 0:
                print(f"\n💰 Cost: ${message.cost_usd:.4f}")
            else:
                print(f"\n✅ Query completed")
    
    # Save the response
    output_dir = Path("parsed")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{cv_path.stem}_analysis.txt"
    with open(output_file, 'w') as f:
        f.write(full_response)
    
    print(f"\n💾 Analysis saved to: {output_file}")


async def main():
    """Main function."""
    if len(sys.argv) > 1:
        cv_file = sys.argv[1]
    else:
        cv_file = "sample_cv.txt"
    
    print(f"🚀 CV Parser - Processing: {cv_file}")
    print("=" * 50)
    
    await parse_cv_simple(cv_file)
    
    print("\n🎉 Processing complete!")


if __name__ == "__main__":
    anyio.run(main)