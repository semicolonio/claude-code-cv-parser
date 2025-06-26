# Contributing to CV Parser

Thank you for your interest in contributing to the CV Parser project! 🎉

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Claude CLI installed and configured
- Git
- uv package manager (recommended) or pip

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/cv-parser.git
   cd cv-parser
   ```

2. **Set up development environment**
   ```bash
   # With uv (recommended)
   uv sync --dev
   
   # Or with pip
   pip install -e ".[dev]"
   ```

3. **Configure Claude CLI**
   ```bash
   claude config
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

## 🎯 Ways to Contribute

### 🐛 Bug Reports
- Use the [GitHub Issues](https://github.com/yourusername/cv-parser/issues) page
- Search existing issues before creating new ones
- Include:
  - Clear description of the problem
  - Steps to reproduce
  - Expected vs actual behavior
  - CV file format that caused the issue (without sensitive data)
  - Error messages and logs

### ✨ Feature Requests
- Open an issue with the `enhancement` label
- Describe the feature and its use case
- Explain why it would benefit the project
- Consider implementation complexity

### 🔧 Code Contributions

#### Pull Request Process
1. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**
   ```bash
   # Test with different CV formats
   python app.py
   # Upload test CVs and verify parsing
   ```

4. **Commit with clear messages**
   ```bash
   git commit -m "Add support for European CV format"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/amazing-feature
   ```

## 📝 Code Style Guidelines

### Python Code
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Add docstrings for functions and classes
- Keep functions focused and single-purpose

### Frontend Code
- Use semantic HTML
- Follow Tailwind CSS conventions
- Comment complex JavaScript logic
- Maintain accessibility standards

### Example Code Style
```python
def extract_candidate_info(cv_text: str, timeout: int = 30) -> Dict[str, Any]:
    """Extract structured candidate information from CV text.
    
    Args:
        cv_text: Raw text content from CV
        timeout: Maximum time to wait for Claude response
        
    Returns:
        Dictionary containing structured candidate data
        
    Raises:
        TimeoutError: If Claude response takes too long
        ValueError: If CV text is empty or invalid
    """
    if not cv_text.strip():
        raise ValueError("CV text cannot be empty")
    
    # Implementation here...
```

## 🧪 Testing

### Manual Testing
- Test with various CV formats (PDF, DOC, DOCX, TXT)
- Try different CV layouts and structures
- Test error scenarios (corrupted files, network issues)
- Verify responsive design on different screen sizes

### Test Cases to Cover
- ✅ Basic information extraction
- ✅ Skills parsing with different formats
- ✅ Work experience with various date formats
- ✅ Education parsing
- ✅ File upload validation
- ✅ Error handling and recovery

## 📋 Project Structure

```
cv-parser/
├── app.py                  # Main Flask application
├── progressive_parser.py   # Step-by-step parsing logic
├── models.py              # Data models and validation
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Upload interface
│   ├── progressive.html  # Live parsing UI
│   └── results.html      # Results display
├── static/               # Static assets
├── tests/                # Test files (if added)
└── docs/                 # Additional documentation
```

## 🎨 UI/UX Guidelines

- **Consistency**: Follow existing design patterns
- **Accessibility**: Ensure keyboard navigation and screen reader support
- **Performance**: Optimize animations and loading times
- **Mobile-first**: Design for mobile, enhance for desktop
- **User feedback**: Provide clear status and error messages

## 🔒 Security Considerations

- **File validation**: Ensure uploaded files are safe
- **Input sanitization**: Clean all user inputs
- **Error handling**: Don't expose sensitive information in errors
- **Privacy**: Respect user data and provide cleanup options

## 🌟 Areas We Need Help

### High Priority
- [ ] **Batch CV processing**: Handle multiple files at once
- [ ] **API development**: RESTful endpoints for integration
- [ ] **Export features**: PDF, Excel, CSV output formats
- [ ] **Error recovery**: Better handling of parsing failures

### Medium Priority
- [ ] **Custom fields**: User-defined extraction fields
- [ ] **CV templates**: Support for different CV formats
- [ ] **Analytics**: Parsing statistics and insights
- [ ] **Internationalization**: Multi-language support

### Nice to Have
- [ ] **Docker support**: Containerization
- [ ] **CI/CD pipeline**: Automated testing and deployment
- [ ] **Performance optimization**: Faster parsing
- [ ] **Advanced UI**: Drag-and-drop improvements

## 💬 Communication

- **Questions**: Open an issue with the `question` label
- **Discussions**: Use GitHub Discussions for broader topics
- **Chat**: Consider creating a Discord/Slack for real-time chat

## 📚 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Claude AI Documentation](https://docs.anthropic.com/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 🙏 Recognition

Contributors will be recognized in:
- README.md acknowledgments
- CHANGELOG.md release notes
- GitHub contributor stats

---

**Thank you for contributing to make CV parsing better for everyone!** 🚀