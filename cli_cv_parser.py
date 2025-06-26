#!/usr/bin/env python3
"""CV parser using Claude Code CLI directly via subprocess."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def parse_cv_with_cli(cv_file_path: str):
    """Parse CV using Claude Code CLI directly."""
    
    # Read CV file
    cv_path = Path(cv_file_path)
    if not cv_path.exists():
        print(f"❌ File not found: {cv_file_path}")
        return
    
    cv_content = cv_path.read_text(encoding='utf-8')
    print(f"📄 Processing CV: {cv_path.name}")
    
    # Create prompt
    prompt = f"""Please analyze this CV and extract the key information in a structured format:

CV Content:
{cv_content}

Please extract and organize:
- Name and contact information
- Professional summary
- Skills
- Work experience
- Education
- Projects
- Certifications

Present the information clearly and concisely."""

    print("🤖 Processing with Claude Code CLI...")
    
    try:
        # Use Claude CLI with pipe input
        result = subprocess.run(
            ["claude", "-p"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            response = result.stdout.strip()
            
            if response:
                # Save response
                output_dir = Path("parsed")
                output_dir.mkdir(exist_ok=True)
                
                output_file = output_dir / f"{cv_path.stem}_parsed.txt"
                with open(output_file, 'w') as f:
                    f.write(f"CV Analysis: {cv_path.name}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(response)
                
                print(f"\n📊 Extracted Information:")
                print("-" * 30)
                print(response)
                print("-" * 30)
                print(f"\n💾 Full analysis saved to: {output_file}")
                print("✅ CV parsing completed!")
            else:
                print("❌ No response from Claude")
        else:
            print(f"❌ CLI error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Processing timed out")
    except FileNotFoundError:
        print("❌ Claude CLI not found. Please make sure Claude is installed and accessible.")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function."""
    if len(sys.argv) > 1:
        cv_file = sys.argv[1]
    else:
        cv_file = "sample_cv.txt"
    
    print("🚀 CV Parser - Using Claude Code CLI")
    print("=" * 45)
    
    parse_cv_with_cli(cv_file)


if __name__ == "__main__":
    main()