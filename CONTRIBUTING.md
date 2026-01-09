# Contributing to ethos-py

Thanks for your interest in contributing to the unofficial Ethos Network Python SDK!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/kluless13/ethos-python-sdk.git
cd ethos-python-sdk
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=src/ethos --cov-report=html
```

## Code Quality

Format code:
```bash
black src tests
```

Lint:
```bash
ruff check src tests
```

Type check:
```bash
mypy src/ethos
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Code Style

- Follow PEP 8
- Use type hints for all function signatures
- Write docstrings for public functions and classes
- Keep functions focused and small

## Reporting Issues

When reporting issues, please include:
- Python version
- SDK version
- Minimal code to reproduce
- Expected vs actual behavior
- Full error traceback if applicable
