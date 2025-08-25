# 🤝 Contributing to 4Runner Hunter

Thank you for your interest in contributing to this learning project! This guide will help you get started.

## 🎯 Project Goals

This project is designed as a **learning tool** for developers to understand:
- Modern Python development practices
- API integration and web scraping
- AI/ML integration with real applications
- Clean code architecture and design patterns

## 🚀 Getting Started

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/4runner-hunter.git
   cd 4runner-hunter
   ```

2. **Set up your environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure your development environment**
   ```bash
   cp .env.example .env
   # Add your AUTO_DEV_API_KEY
   ```

4. **Run the tests**
   ```bash
   python tests/test_api.py
   python tests/test_vin_anal.py
   python tests/test_full_run.py
   ```

## 📝 Types of Contributions

### 🐛 Bug Reports
- Check existing issues first
- Provide clear reproduction steps
- Include your environment details
- Add relevant log output

### ✨ Feature Requests
- Explain the learning value
- Provide implementation ideas
- Consider backward compatibility

### 📚 Documentation
- Fix typos and grammar
- Add code examples
- Improve learning explanations
- Update setup instructions

### 🔧 Code Contributions
- Follow the coding standards below
- Add tests for new features
- Update documentation
- Keep changes focused

## 🎨 Coding Standards

### Python Style
- Follow PEP 8
- Use meaningful variable names
- Add docstrings for classes and functions
- Keep functions focused and small

### Code Organization
```python
# Good: Clear, descriptive function names
def analyze_vin_transmission_type(vin: str) -> Optional[str]:
    """Analyze VIN to determine transmission type."""
    pass

# Good: Proper error handling
try:
    response = api_client.get_listings()
except APIError as e:
    logger.error(f"API call failed: {e}")
    return None
```

### Database Changes
- Always provide migration scripts
- Test with existing data
- Document schema changes

### Web Interface
- Keep responsive design
- Test on multiple browsers
- Maintain accessibility

## 🧪 Testing

### Required Tests
- Add tests for new API endpoints
- Test error conditions
- Verify database operations
- Test VIN analysis patterns

### Running Tests
```bash
# API connectivity
python tests/test_api.py

# VIN analysis
python tests/test_vin_anal.py

# Full system
python tests/test_full_run.py
```

## 📋 Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update relevant documentation

3. **Test your changes**
   ```bash
   python tests/test_api.py
   python tests/test_vin_anal.py
   ```

4. **Commit with clear messages**
   ```bash
   git commit -m "Add: New VIN pattern for 2000-2002 models"
   git commit -m "Fix: Rate limiting edge case in API client"
   git commit -m "Docs: Update installation instructions"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### PR Template
```markdown
## Description
Brief description of changes

## Learning Value
What will learners gain from this change?

## Testing
- [ ] Tested locally
- [ ] Added/updated tests
- [ ] Documentation updated

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
```

## 🌟 Good First Issues

Perfect for new contributors:

### Beginner
- Add new VIN patterns
- Improve error messages
- Add configuration options
- Fix documentation typos

### Intermediate
- Add new filters to web interface
- Implement email notifications
- Add data export features
- Improve API error handling

### Advanced
- Add new API integrations
- Implement caching layer
- Add ML price predictions
- Create mobile app interface

## 📖 Code Review Guidelines

### What We Look For
- **Learning Value**: Does this help others learn?
- **Code Quality**: Is it clean and well-documented?
- **Testing**: Are there appropriate tests?
- **Documentation**: Is it properly documented?

### Review Process
1. Automated checks (linting, tests)
2. Code review by maintainers
3. Feedback incorporation
4. Final approval and merge

## 🐛 Common Issues

### API Rate Limits
```python
# Good: Respect rate limits
self.rate_limiter.wait_if_needed()
response = requests.get(url)

# Bad: No rate limiting
response = requests.get(url)  # Can get blocked
```

### Database Connections
```python
# Good: Proper connection handling
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    # Do work

# Bad: Unclosed connections
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
# Do work (connection never closed)
```

### Environment Variables
```python
# Good: Provide defaults
API_KEY = os.getenv("AUTO_DEV_API_KEY", "")
if not API_KEY:
    raise ValueError("AUTO_DEV_API_KEY is required")

# Bad: No validation
API_KEY = os.getenv("AUTO_DEV_API_KEY")  # Could be None
```

## 📚 Learning Resources

### Project-Specific
- [Auto.dev API Documentation](https://auto.dev/docs)
- [Toyota VIN Guide](https://en.wikipedia.org/wiki/Vehicle_identification_number)

### General Development
- [Python PEP 8](https://pep8.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLite Tutorial](https://www.sqlitetutorial.net/)

## 🎉 Recognition

Contributors will be:
- Listed in the README
- Credited in release notes
- Given priority for mentorship requests

## ❓ Questions?

- 📧 Create an issue for questions
- 💬 Start a discussion for ideas
- 🐛 Report bugs with detailed info

Thank you for helping make this a better learning tool for everyone! 🚀