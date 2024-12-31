# PyVeSync Mock Server Project

> Created and maintained by Claude (Anthropic) and Cursor AI

## Overview
A mock server that validates PyVeSync library requests against YAML specifications. This is NOT a full implementation - it only validates requests and returns minimal responses to satisfy the PyVeSync library's expectations.

This project operates under 4 immutable rules:

1. **Request Validation**: Exact validation of all requests against YAML specifications in the `/api` directory to satisfy PyVeSync library
2. **Minimal Response**: Return only the essential response fields needed for PyVeSync to function without error
3. **API Specifications are Gospel**: The YAML specs in `/api` directory are the source of truth and cannot be modified
4. **PyVeSync Source is Gospel**: The PyVeSync library's source code defines the expected behavior and cannot be modified

## Purpose
- Validate that requests from PyVeSync library match YAML specs exactly
- Return minimal valid responses that PyVeSync accepts
- Enable testing of PyVeSync integrations without real devices
- NOT intended to implement actual device functionality

## Goals
1. **Primary Directives**
   - Validate requests exactly against YAML specs
   - Return minimal valid responses
   - Never modify API specs or PyVeSync source
   
2. **Supporting Goals**
   - Enable reliable request validation testing
   - Support all PyVeSync request types
   - Maintain clean, maintainable codebase
   - Provide comprehensive test coverage

## Architecture

### Directory Structure
```
vesync-mock/
├── api/                    # YAML API specifications
│   ├── vesync/            # Core API specs (login, device list)
│   ├── vesyncfan/         # Fan and humidifier device specs
│   ├── vesyncoutlet/      # Outlet device specs
│   ├── vesyncswitch/      # Switch device specs
│   └── vesyncbulb/        # Bulb device specs
├── docs/                   # Project documentation
│   ├── PROJECT.md         # Project overview and architecture
│   ├── DOCUMENTATION.md   # API and implementation details
│   ├── CHANGELOG.md       # Version history and changes
│   ├── MILESTONES.md      # Project milestones and progress
│   └── LEARNINGS.md       # Development insights and lessons
├── src/                    # Source code
│   ├── main.py            # FastAPI application entry point
│   ├── routes.py          # API route definitions
│   ├── constants.py       # Global constants and configurations
│   ├── validators.py      # Core validation logic
│   ├── response_utils.py  # Response formatting utilities
│   ├── fan_validator.py   # Fan/humidifier request validation
│   ├── outlet_validator.py # Outlet request validation
│   ├── switch_validator.py # Switch request validation
│   └── bulb_validator.py  # Bulb request validation
├── tests/                  # Test suite
│   ├── test_api.py        # API endpoint tests
│   ├── test_pyvesync_api.py  # PyVeSync client tests
│   ├── test_pyvesync_full.py # Full device feature tests
│   └── conftest.py        # Test configuration and fixtures
├── scripts/               # Utility scripts
├── requirements.txt      # Project dependencies
├── README.md            # Project overview
├── LICENSE             # License information
└── venv/               # Virtual environment
    └── lib/
        └── python3.11/
            └── site-packages/
                └── pyvesync/  # PyVeSync source code
```

### Key Components

1. **API Specifications**
   - YAML files define exact request/response formats
   - Case-sensitive field names and values
   - Strict header and payload validation
   - Auth field handling (accountID/token) in headers and body

2. **Request Validation**
   - Exact field name matching from specs
   - Case-sensitive validation
   - Auth field presence based on spec
   - Payload structure verification

3. **Response Formatting**
   - Match PyVeSync's exact response format
   - Handle device-specific response fields
   - Proper error response formatting
   - Consistent success/failure patterns

4. **Test Framework**
   - Test against YAML specs
   - Track test results by device and endpoint
   - Clear error reporting
   - Formatted test summary output

## Development Guidelines

### Code Standards
1. Use type hints for all functions
2. Document all public methods
3. Follow YAML spec structure exactly
4. Keep validation logic separate
5. Use constants for magic values
6. Follow consistent naming conventions

### Error Handling
1. Match PyVeSync's error codes
2. Include proper error messages
3. Return consistent error responses
4. Log validation failures
5. Track error patterns

### Testing Requirements
1. Test against YAML specs exactly
2. Verify field name case sensitivity
3. Test auth field combinations
4. Validate response formats
5. Test error conditions

## Current Status

### Completed
1. Basic server structure
2. YAML spec loading
3. Request validation
4. Auth field handling
5. Test result tracking
6. Test summary reporting
7. Migration to pytest framework
8. Organized documentation structure
9. Comprehensive requirements.txt
10. PyVeSync client testing
11. Response format validation
12. Device state management
13. Error scenario handling
14. Pytest fixture improvements
15. Device state tracking
16. Complete device support
17. Mock device state persistence

## Security Guidelines
1. Validate all input against specs
2. Sanitize responses
3. Handle sensitive data properly
4. Follow PyVeSync's security model
5. Implement proper rate limiting

### **After Making ANY Code Changes**  
1. **Update Documentation Immediately**:  
   - Add new features/changes to the `[Unreleased]` section of `docs/CHANGELOG.md`.  
   - Update `docs/PROJECT.md` and `docs/DOCUMENTATION.md` if there are changes to architecture, features, or limitations.

2. **Report Documentation Updates**:  
   - Use the following format to report updates:  
     ```
     Updated CHANGELOG.md: [details of what changed]  
     Updated DOCUMENTATION.md: [details of what changed] (if applicable)
     Updated PROJECT.md: [details of what changed] (if applicable)
     ```

3. **Ensure Alignment**:  
   - Verify that all changes align with existing architecture and features.

4. **Document All Changes**:  
   - Include specific details about:
     - New features or improvements
     - Bug fixes
     - Error handling changes
     - UI/UX updates
     - Technical implementation details

5. **Adhere to the Read-First/Write-After Approach**:  
   - Maintain explicit update reporting for consistency and continuity.