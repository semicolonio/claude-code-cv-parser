# Security Guidelines

This document outlines security best practices for the CV Parser project.

## 🔒 Data Privacy

### Sensitive Data Handling
- **NEVER commit real CV files** or personal data to the repository
- All uploads are automatically excluded via `.gitignore`
- Parsed results containing personal information are never committed
- Use only fictional test data in examples

### File Upload Security
- File type validation for all uploads
- Size limits enforced (16MB maximum)
- Secure filename handling with `werkzeug.secure_filename`
- Files are processed locally, not sent to external services

## 🛡️ Application Security

### Environment Variables
```bash
# Use environment variables for sensitive configuration
export SECRET_KEY="your-production-secret-key"
export CLAUDE_MODEL="sonnet"
export DEBUG="false"
```

### Production Deployment
- Change default secret key before production deployment
- Set `DEBUG=False` in production
- Use HTTPS for web deployment
- Implement proper session management
- Set up proper file cleanup policies

### Claude AI Integration
- Claude processing happens locally via CLI
- No data is sent to external APIs beyond Claude's standard usage
- Ensure Claude CLI is properly authenticated and configured

## 🚨 Security Checklist

Before deploying:
- [ ] Changed default secret key
- [ ] Set `DEBUG=False`
- [ ] Configured proper file cleanup
- [ ] Reviewed `.gitignore` coverage
- [ ] Tested with non-sensitive data only
- [ ] Verified no hardcoded credentials

## 📋 Incident Response

If sensitive data is accidentally committed:
1. **Immediately** change any exposed credentials
2. Remove sensitive files from git history using `git filter-branch` or BFG Repo-Cleaner
3. Force push to overwrite history
4. Notify all team members
5. Review and strengthen `.gitignore` rules

## 🔍 Regular Security Reviews

- Audit dependencies regularly for vulnerabilities
- Review file upload handling
- Check for any hardcoded secrets in code
- Verify `.gitignore` effectiveness
- Test with sample data only

## 📞 Reporting Security Issues

If you discover a security vulnerability:
1. **DO NOT** open a public issue
2. Email the maintainers directly
3. Provide detailed description of the issue
4. Allow time for responsible disclosure