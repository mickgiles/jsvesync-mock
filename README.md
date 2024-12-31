# VeSync Mock API Server

> Created and maintained by Claude (Anthropic) and Cursor AI

A mock server implementation of the VeSync API for testing and development purposes.

## Overview
This server provides a complete mock implementation of the VeSync API, allowing for testing and development of VeSync-compatible applications without requiring actual VeSync devices.

## Key Features
- YAML-based API specifications
- Exact request/response format matching
- Comprehensive device support
- Pytest-based test suite
- Detailed test reporting
- PyVeSync compatibility
- Complete device state management
- Robust error handling
- Comprehensive test fixtures
- State persistence

## Project Status

### Completed
- Basic server implementation
- YAML spec loading
- Request validation
- Auth field handling
- Test result tracking
- Test summary reporting
- Migration to pytest framework
- Organized documentation structure
- Comprehensive requirements.txt
- PyVeSync client testing
- Response format validation
- Device state management
- Error scenario handling
- Pytest fixture improvements
- Device state tracking
- Complete device support
- State persistence

## Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python main.py
```

The server will start on `http://localhost:8000`.

## Testing

Run the API test suite with pytest:
```bash
pytest tests/test_api.py -v
```

Coming soon - PyVeSync client tests:
```bash
pytest tests/test_pyvesync_client.py -v
```

## Default Credentials
- Email: test@example.com
- Password: test123

## Documentation
- [API Documentation](docs/DOCUMENTATION.md)
- [Project Architecture](docs/PROJECT.md)
- [Development Progress](docs/MILESTONES.md)

## Project Structure
```
jsvesync-mock/
├── api/                    # YAML API specifications
│   ├── vesync/            # Core API specs
│   ├── vesyncfan/         # Fan device specs
│   ├── vesyncoutlet/      # Outlet device specs
│   └── vesyncbulb/        # Bulb device specs
├── docs/                   # Project documentation
├── tests/                  # Test suite
│   ├── test_api.py        # API endpoint tests
│   ├── test_pyvesync_client.py  # PyVeSync integration tests
│   └── conftest.py        # Pytest fixtures
├── validators.py          # Request/response validators
└── main.py               # Application entry point
```

## Notes
- All device responses are mocked but follow the official VeSync API format
- Energy usage data is randomly generated for demonstration
- The server includes basic rate limiting and error handling
- Tests use pytest for reliable validation

## Dependencies
See [requirements.txt](requirements.txt) for complete list:
- FastAPI 0.104.1
- Uvicorn 0.24.0
- Pydantic 2.5.2
- PyYAML 6.0.1
- Pytest 7.4.3
- Other supporting libraries

## Credits

This project was inspired by and built to be compatible with the [pyvesync](https://github.com/webdjoe/pyvesync) project. Special thanks to the pyvesync contributors for their work in reverse engineering the VeSync API.

Built with assistance from:
- [Cursor](https://cursor.sh/) - The AI-first code editor
- Claude - Anthropic's AI assistant