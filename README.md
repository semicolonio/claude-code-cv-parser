# 🚀 AI-Powered CV Parser

An intelligent CV parsing system that uses **Claude AI** to extract and structure candidate information from resumes with a beautiful, real-time web interface.

![CV Parser Demo](https://img.shields.io/badge/Demo-Live-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Claude AI](https://img.shields.io/badge/Claude-AI-purple) ![License](https://img.shields.io/badge/License-MIT-green)

## 🎬 Demo Video

Watch the CV Parser in action with real-time progressive parsing:

<video width="100%" controls>
  <source src="docs/media/cv-parser.mp4" type="video/mp4">
  <p>Your browser doesn't support embedded videos. <a href="docs/media/cv-parser.mp4">Download the demo video</a> to see the CV Parser in action!</p>
</video>

> **✨ See how the parser extracts candidate information step-by-step with beautiful animations and real-time updates!**

*Note: If the video doesn't play in your browser, you can [download it here](docs/media/cv-parser.mp4) or view it directly in the repository.*

## ✨ Features

### 🎯 **Smart Extraction**
- **Multi-format support**: PDF, DOC, DOCX, TXT files
- **Structured output**: Clean JSON with standardized fields
- **High accuracy**: Powered by Claude 3.5 Sonnet
- **Context-aware**: Understands CV patterns and formats

### 🎨 **Beautiful Interface** 
- **Progressive parsing**: Real-time step-by-step visualization
- **Live updates**: Watch as information gets extracted
- **Smooth animations**: Engaging visual feedback
- **Responsive design**: Works on desktop and mobile

### 🔄 **Real-time Experience**
- **Step-by-step progress**: See each parsing stage
- **Visual previews**: Know what's being processed
- **Auto-scrolling**: Follows the parsing progress
- **Completion celebration**: Clear success indication

## 🏗️ What Gets Extracted

The system intelligently extracts:

- 👤 **Basic Information**: Name, email, phone, professional summary
- 🛠️ **Technical Skills**: Programming languages, frameworks, tools
- 💼 **Work Experience**: Companies, positions, dates, achievements  
- 🎓 **Education**: Degrees, institutions, dates
- 🚀 **Projects & Certifications**: Side projects, professional certifications

## 🛠️ Technology Stack

- **Backend**: Python, Flask, Server-Sent Events (SSE)
- **AI**: Claude 3.5 Sonnet via Claude CLI
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **File Processing**: PyPDF2, python-docx
- **Data Validation**: Pydantic
- **Package Management**: uv (fast Python package installer and resolver)

## 📋 Prerequisites

- **Python 3.8+**
- **Claude CLI** installed and configured ([Setup Guide](https://docs.anthropic.com/en/docs/claude-code))
- **uv** package manager ([Install uv](https://docs.astral.sh/uv/getting-started/installation/))

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/cv-parser.git
   cd cv-parser
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure Claude CLI**
   ```bash
   # Make sure Claude CLI is installed and authenticated
   claude config
   ```

4. **Run the application**
   ```bash
   uv run python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8080`

## 🎮 Usage

### 📤 **Upload & Parse**
1. **Upload a CV file** (drag & drop or click to select)
2. **Choose parsing mode**:
   - **Instant**: Quick one-step parsing
   - **Progressive**: Step-by-step with live visualization (recommended)
3. **Watch the magic happen** ✨

### 📊 **View Results**
- **Live progress**: See real-time parsing steps
- **Structured data**: Clean, organized candidate information
- **Export options**: JSON format for integration

## 📁 Project Structure

```
cv-parser/
├── app.py                  # Main Flask application
├── src/                    # Organized source code
│   ├── config/            # Configuration management
│   ├── models/            # Data models and validation
│   ├── parsers/           # CV parsing engines
│   └── utils/             # Utility functions
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Upload interface
│   ├── progressive.html  # Live parsing UI
│   └── results.html      # Results display
├── static/               # Static assets
├── examples/             # Sample files for testing
├── docs/                 # Documentation
└── pyproject.toml        # Dependencies and config
```

## ⚙️ Configuration

### Claude Model Selection
The system uses Claude 3.5 Sonnet by default. You can modify the model using environment variables:

```bash
export CLAUDE_MODEL="sonnet"
export CLAUDE_TIMEOUT="120"
```

### File Upload Limits
Configure in environment or `src/config/settings.py`:
```python
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}
```

## 📦 Why uv?

This project uses [uv](https://github.com/astral-sh/uv) for dependency management because it's:
- **⚡ 10-100x faster** than pip
- **🔒 Reliable** with deterministic dependency resolution
- **🎯 Simple** - drop-in replacement for pip
- **🔄 Compatible** with standard Python packaging

## 🔒 Security & Privacy

- **No data persistence**: Uploaded files are processed and can be automatically cleaned up
- **Local processing**: All parsing happens on your machine
- **Configurable retention**: Set your own file cleanup policies
- **Secure uploads**: File type validation and size limits

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/cv-parser.git
cd cv-parser

# Install development dependencies
uv sync

# Run in development mode
uv run python app.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Anthropic** for the powerful Claude AI
- **Claude Code** for the excellent CLI interface
- **Tailwind CSS** for the beautiful styling
- **Flask** for the robust web framework

## 🐛 Issues & Support

Found a bug or need help? 

- **Create an issue**: [GitHub Issues](https://github.com/yourusername/cv-parser/issues)
- **Check existing issues**: Search before creating new ones
- **Provide details**: Include error messages, CV formats, and steps to reproduce

## 🎯 Roadmap

- [ ] **Batch processing**: Handle multiple CVs at once
- [ ] **API endpoints**: RESTful API for integration
- [ ] **Export formats**: PDF, Excel, CSV outputs
- [ ] **Custom fields**: User-defined extraction fields
- [ ] **Templates**: CV format templates and matching
- [ ] **Analytics**: Parsing statistics and insights

---

**⭐ Star this repo if it helped you!** | **🔗 Share with your network** | **🐛 Report issues**