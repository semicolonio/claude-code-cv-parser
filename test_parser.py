#!/usr/bin/env python3
"""Test script for CV parser debugging."""

import json
import sys
from pathlib import Path
from src.parsers.progressive import ProgressiveCVParser

# Sample CV text for testing
sample_cv = """
John Doe
Senior Software Engineer
Email: john.doe@example.com
Phone: +1 (555) 123-4567

Professional Summary:
Experienced software engineer with 8+ years of expertise in full-stack development, 
specializing in Python, JavaScript, and cloud technologies. Proven track record of 
delivering scalable solutions and leading development teams.

Skills:
- Programming Languages: Python, JavaScript, TypeScript, Java, Go
- Frontend: React, Vue.js, Angular, HTML5, CSS3, SASS
- Backend: Django, Flask, Node.js, Express, FastAPI
- Databases: PostgreSQL, MySQL, MongoDB, Redis
- Cloud: AWS, Google Cloud, Docker, Kubernetes
- Tools: Git, Jenkins, JIRA, Agile/Scrum

Experience:

Tech Solutions Inc. | Senior Software Engineer | 2020 - Present
- Led development of microservices architecture serving 1M+ users
- Reduced API response times by 60% through optimization
- Mentored team of 5 junior developers

StartupXYZ | Full Stack Developer | 2018 - 2020  
- Built real-time collaboration features using WebSockets
- Implemented CI/CD pipeline reducing deployment time by 80%
- Developed RESTful APIs handling 10K+ requests/minute

CodeCraft Ltd. | Junior Developer | 2016 - 2018
- Developed and maintained e-commerce platform
- Implemented payment gateway integrations
- Wrote comprehensive unit tests achieving 85% code coverage

Education:

University of Technology | Bachelor of Science in Computer Science | 2012 - 2016
- GPA: 3.8/4.0
- Dean's List recipient

Projects:

Open Source Contributor - ReactiveDB
- Contributed to popular open-source database ORM
- Implemented query optimization features

Personal Portfolio Website
- Built responsive portfolio using Next.js and Tailwind CSS
- Deployed on Vercel with custom domain

Certifications:
- AWS Certified Solutions Architect
- Google Cloud Professional Developer
- Certified Kubernetes Administrator (CKA)
"""

def test_parser():
    """Test the CV parser with sample data."""
    print("Testing CV Parser with sample data...\n")
    
    parser = ProgressiveCVParser(sample_cv, "test_cv.txt")
    
    # Test individual methods
    print("1. Testing Basic Info Extraction:")
    print("-" * 50)
    try:
        for event in parser.extract_basic_info():
            if event['status'] == 'completed':
                print("SUCCESS: Basic info extracted")
                print(json.dumps(event['data'], indent=2))
            elif event['status'] == 'error':
                print(f"ERROR: {event['error']}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    print("\n2. Testing Skills Extraction:")
    print("-" * 50)
    try:
        for event in parser.extract_skills():
            if event['status'] == 'completed':
                print("SUCCESS: Skills extracted")
                print(f"Found {len(event['data']['skills'])} skills")
                print("First 5 skills:", event['data']['skills'][:5])
            elif event['status'] == 'error':
                print(f"ERROR: {event['error']}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    print("\n3. Testing Experience Extraction:")
    print("-" * 50)
    try:
        for event in parser.extract_experience():
            if event['status'] == 'completed':
                print("SUCCESS: Experience extracted")
                print(f"Found {len(event['data']['experience'])} positions")
                for exp in event['data']['experience']:
                    print(f"- {exp['position']} at {exp['company']}")
            elif event['status'] == 'error':
                print(f"ERROR: {event['error']}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    print("\n4. Testing Education Extraction:")
    print("-" * 50)
    try:
        for event in parser.extract_education():
            if event['status'] == 'completed':
                print("SUCCESS: Education extracted")
                print(f"Found {len(event['data']['education'])} education entries")
                for edu in event['data']['education']:
                    print(f"- {edu['degree']} from {edu['institution']}")
            elif event['status'] == 'error':
                print(f"ERROR: {event['error']}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    print("\n5. Testing Projects & Certifications Extraction:")
    print("-" * 50)
    try:
        for event in parser.extract_projects_and_certifications():
            if event['status'] == 'completed':
                print("SUCCESS: Projects & Certifications extracted")
                print(f"Found {len(event['data']['projects'])} projects")
                print(f"Found {len(event['data']['certifications'])} certifications")
            elif event['status'] == 'error':
                print(f"ERROR: {event['error']}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    print("\nTest completed. Check cv_parser_debug.log for detailed logs.")

if __name__ == "__main__":
    test_parser()