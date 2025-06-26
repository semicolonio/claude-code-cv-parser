#!/usr/bin/env python3
"""Simple script to run CV parser with command line arguments."""

import sys
from pathlib import Path
import anyio
from cv_parser_app import CVParserApp


async def main():
    """Run CV parser with command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python run_cv_parser.py <cv_file_path>")
        print("Example: python run_cv_parser.py sample_cv.txt")
        return
    
    cv_file_path = sys.argv[1]
    
    if not Path(cv_file_path).exists():
        print(f"❌ File not found: {cv_file_path}")
        return
    
    print(f"🚀 Processing CV: {cv_file_path}")
    
    app = CVParserApp()
    result = await app.process_cv(cv_file_path)
    
    if result:
        print(f"\n✅ Success! Parsed CV saved to: {result}")
    else:
        print("\n❌ Failed to process CV")


if __name__ == "__main__":
    anyio.run(main)