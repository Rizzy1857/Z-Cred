# Development Setup Guide

This guide will help you set up the Z-Cred development environment.

## Prerequisites

- Python 3.8 or higher
- Git
- pip (Python package manager)

## Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Rizzy1857/Z-Cred.git
   cd Z-Cred
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   make setup-dev
   # OR manually:
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   pre-commit install
   ```

## Development Workflow

### Running Tests
```bash
make test          # Run all tests
make test-cov      # Run tests with coverage
make coverage      # Generate HTML coverage report
```

### Code Quality
```bash
make lint          # Run linting (flake8, mypy)
make format        # Format code (black, isort)
make security      # Run security checks (bandit, safety)
make pre-commit    # Run all pre-commit hooks
```

### Running the Application
```bash
make run           # Run main application
make run-user      # Run user application
make run-admin     # Run admin application
```

### Building and Distribution
```bash
make build         # Build package
make clean         # Clean temporary files
```

## Project Structure

```
Z-Cred/
 src/                    # Source code
    apps/              # Streamlit applications
    core/              # Core functionality
    database/          # Database operations
    models/            # ML models and pipelines
    utils/             # Utility functions
 tests/                 # Test files
 docs/                  # Documentation
 scripts/               # Utility scripts
 .github/               # GitHub Actions workflows
 requirements*.txt      # Dependencies
```

## Configuration Files

- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `pyproject.toml` - Modern Python project configuration
- `setup.py` - Package setup (legacy support)
- `.coveragerc` - Coverage configuration
- `Makefile` - Common development tasks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

For more details, see [CONTRIBUTION.md](docs/CONTRIBUTION.md).

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you've activated your virtual environment
2. **Test Failures**: Ensure all dependencies are installed with `make install-dev`
3. **Linting Errors**: Run `make format` to auto-fix formatting issues

### Getting Help

- Check the [documentation](docs/)
- Open an issue on GitHub
- Review the project's [integration guide](docs/INTEGRATION_GUIDE.md)
