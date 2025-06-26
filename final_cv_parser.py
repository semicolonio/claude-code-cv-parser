#!/usr/bin/env python3
"""Final working CV parser using Claude Code SDK."""

import sys
from pathlib import Path

import anyio
from claude_code_sdk import query, AssistantMessage, TextBlock, ClaudeCodeOptions


async def parse_cv(cv_file_path: str):
    """Parse CV file and extract information."""
    
    # Read CV file
    cv_path = Path(cv_file_path)
    if not cv_path.exists():
        print(f"❌ File not found: {cv_file_path}")
        return
    
    cv_content = cv_path.read_text(encoding='utf-8')
    print(f"📄 Processing CV: {cv_path.name}")
    
    # Configure options
    options = ClaudeCodeOptions(
        system_prompt="You are a professional CV parser. Extract key information clearly and concisely.",
        max_turns=1
    )
    
    # Create a focused prompt
    prompt = f"""Parse this CV and extract the key information:

{cv_content}

Extract:
1. Name and contact details
2. Professional summary
3. Top skills
4. Work experience (company, role, dates)
5. Education
6. Notable projects or certifications"""

    print("🤖 Analyzing with Claude...")
    
    try:
        response_parts = []
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_parts.append(block.text)
                        print(block.text)
        
        # Save full response
        full_response = "\n".join(response_parts)
        
        if full_response:
            output_dir = Path("parsed")
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / f"{cv_path.stem}_extracted.txt"
            with open(output_file, 'w') as f:
                f.write(f"CV Analysis for: {cv_path.name}\n")
                f.write("=" * 50 + "\n\n")
                f.write(full_response)
            
            print(f"\n💾 Analysis saved to: {output_file}")
            print("✅ CV parsing completed successfully!")
        else:
            print("❌ No response received from Claude")
            
    except Exception as e:
        print(f"❌ Error during parsing: {e}")


async def main():
    """Main function."""
    if len(sys.argv) > 1:
        cv_file = sys.argv[1]
    else:
        cv_file = "sample_cv.txt"
    
    print("🚀 CV Parser - Claude Code SDK")
    print("=" * 40)
    
    await parse_cv(cv_file)


if __name__ == "__main__":
    anyio.run(main)