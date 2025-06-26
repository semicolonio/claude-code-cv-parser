# CV Parser System

A sophisticated CV parsing system that combines Claude Code SDK with MCP (Model Context Protocol) servers to extract structured candidate information from uploaded CVs.

## Architecture

- **MCP Server** (`cv_parser_server.py`): Specialized CV processing server with file reading and parsing tools
- **Main Application** (`cv_parser_app.py`): Orchestrates parsing using Claude Code SDK
- **Data Models** (`models.py`): Pydantic models for structured candidate data
- **Command Line Interface** (`run_cv_parser.py`): Simple CLI for processing CVs

## Features

- ✅ **Multi-format Support**: PDF, DOCX, and TXT files
- ✅ **Structured Extraction**: Contact info, experience, education, skills, projects, certifications
- ✅ **AI-Powered Parsing**: Uses Claude's advanced language understanding
- ✅ **JSON Output**: Clean, structured candidate profiles
- ✅ **Modular Design**: Separates concerns between parsing logic and AI orchestration

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have Claude Code CLI installed:
```bash
npm install -g @anthropic-ai/claude-code
```

## Usage

### Quick Start
```bash
python run_cv_parser.py sample_cv.txt
```

### Programmatic Usage
```python
from cv_parser_app import CVParserApp
import anyio

async def parse_cv():
    app = CVParserApp()
    result = await app.process_cv("path/to/cv.pdf")
    return result

anyio.run(parse_cv)
```

## Data Structure

The system extracts candidate information into the following structure:

```python
CandidateProfile(
    name: str
    contact_info: ContactInfo
    summary: Optional[str]
    skills: List[str]
    experience: List[Experience]
    education: List[Education]
    projects: List[Project]
    certifications: List[Certification]
    languages: List[str]
)
```

## File Organization

```
├── models.py              # Pydantic data models
├── cv_parser_server.py    # MCP server for CV processing
├── cv_parser_app.py       # Main application using Claude Code SDK
├── run_cv_parser.py       # CLI interface
├── sample_cv.txt          # Example CV for testing
├── uploads/               # Directory for uploaded CVs
└── parsed/                # Directory for parsed JSON outputs
```

## How It Works

1. **Upload**: CV file is copied to `uploads/` directory
2. **MCP Server**: Provides specialized tools for file reading and text extraction
3. **Claude Processing**: Uses Claude Code SDK to intelligently parse CV content
4. **Structured Output**: Extracts information into Pydantic models
5. **JSON Export**: Saves structured candidate profile as JSON

## Example Output

```json
{
  "name": "John Smith",
  "contact_info": {
    "email": "john.smith@email.com",
    "phone": "(555) 123-4567",
    "linkedin": "linkedin.com/in/johnsmith",
    "github": "github.com/johnsmith"
  },
  "skills": ["Python", "JavaScript", "AWS", "Docker"],
  "experience": [
    {
      "company": "TechCorp Inc.",
      "position": "Senior Software Engineer",
      "start_date": "2021",
      "is_current": true,
      "description": "Led development of microservices architecture"
    }
  ]
}
```

## Next Steps

- Add web interface for file uploads
- Implement batch processing for multiple CVs
- Add export formats (Excel, CSV)
- Create candidate ranking/scoring system
- Add multilingual support