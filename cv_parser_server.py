#!/usr/bin/env python3
"""MCP server for CV parsing and candidate information extraction."""

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List

import PyPDF2
import docx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextResourceContents, Tool

from models import CandidateProfile, ContactInfo, Experience, Education, Project, Certification


# Initialize the MCP server
server = Server("cv-parser")


@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available CV files in the uploads directory."""
    uploads_dir = Path("uploads")
    if not uploads_dir.exists():
        return []
    
    resources = []
    for file_path in uploads_dir.iterdir():
        if file_path.suffix.lower() in ['.pdf', '.docx', '.txt']:
            resources.append(Resource(
                uri=f"cv://{file_path.name}",
                name=f"CV: {file_path.name}",
                description=f"CV file: {file_path.name}",
                mimeType="text/plain"
            ))
    
    return resources


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read and extract text content from CV files."""
    if not uri.startswith("cv://"):
        raise ValueError("Invalid resource URI")
    
    filename = uri[5:]  # Remove 'cv://' prefix
    file_path = Path("uploads") / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"CV file not found: {filename}")
    
    return await extract_text_from_file(file_path)


async def extract_text_from_file(file_path: Path) -> str:
    """Extract text content from different file formats."""
    suffix = file_path.suffix.lower()
    
    if suffix == '.txt':
        return file_path.read_text(encoding='utf-8')
    
    elif suffix == '.pdf':
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    elif suffix == '.docx':
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


@server.tool()
async def parse_cv(file_path: str) -> CandidateProfile:
    """Parse a CV file and extract structured candidate information."""
    cv_path = Path("uploads") / file_path
    
    if not cv_path.exists():
        raise FileNotFoundError(f"CV file not found: {file_path}")
    
    # Extract text content from the CV
    cv_text = await extract_text_from_file(cv_path)
    
    # This is where Claude Code SDK will help us parse the text
    # For now, return a basic structure that Claude will populate
    return CandidateProfile(
        name="",
        contact_info=ContactInfo(),
        summary="",
        skills=[],
        experience=[],
        education=[],
        projects=[],
        certifications=[],
        languages=[]
    )


@server.tool()
async def extract_contact_info(cv_text: str) -> ContactInfo:
    """Extract contact information from CV text."""
    return ContactInfo()


@server.tool()
async def extract_experience(cv_text: str) -> List[Experience]:
    """Extract work experience from CV text."""
    return []


@server.tool()
async def extract_education(cv_text: str) -> List[Education]:
    """Extract education information from CV text."""
    return []


@server.tool()
async def extract_skills(cv_text: str) -> List[str]:
    """Extract skills from CV text."""
    return []


@server.tool()
async def save_parsed_cv(candidate_profile: CandidateProfile, output_file: str) -> str:
    """Save parsed candidate profile to JSON file."""
    output_path = Path("parsed") / output_file
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(candidate_profile.model_dump_json(indent=2))
    
    return f"Candidate profile saved to {output_path}"


async def main():
    """Run the MCP server."""
    # Ensure required directories exist
    Path("uploads").mkdir(exist_ok=True)
    Path("parsed").mkdir(exist_ok=True)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())