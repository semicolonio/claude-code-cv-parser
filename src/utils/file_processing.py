#!/usr/bin/env python3
"""File processing utilities for CV parsing."""

from pathlib import Path
from typing import Set

import PyPDF2
import docx

# Configuration
ALLOWED_EXTENSIONS: Set[str] = {'txt', 'pdf', 'docx', 'doc'}


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed.
    
    Args:
        filename: Name of the file to check
        
    Returns:
        True if file extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_file(file_path: str | Path) -> str:
    """Extract text content from different file formats.
    
    Args:
        file_path: Path to the file to extract text from
        
    Returns:
        Extracted text content
        
    Raises:
        ValueError: If file format is unsupported
        IOError: If file cannot be read
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    
    try:
        if suffix == '.txt':
            return file_path.read_text(encoding='utf-8')
        
        elif suffix == '.pdf':
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        
        elif suffix in ['.docx', '.doc']:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
            
    except Exception as e:
        raise IOError(f"Error reading file: {str(e)}")