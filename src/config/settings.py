#!/usr/bin/env python3
"""Application configuration settings."""

import os
from pathlib import Path

# Application settings
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# File upload settings
UPLOAD_FOLDER = Path('uploads')
PARSED_FOLDER = Path('parsed')
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}

# Claude AI settings
CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'sonnet')
CLAUDE_TIMEOUT = int(os.getenv('CLAUDE_TIMEOUT', '120'))

# Ensure directories exist
UPLOAD_FOLDER.mkdir(exist_ok=True)
PARSED_FOLDER.mkdir(exist_ok=True)