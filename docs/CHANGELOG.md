# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2023-12-30

### Added
- Initial implementation of VeSync mock server
- Support for all PyVeSync device types:
  - Air purifiers (Core200S, Core300S, Core400S, Core600S, LV-PUR131S, etc.)
  - Humidifiers (Classic200S, Classic300S, Dual200S, etc.)
  - Outlets (ESW15-USA, ESW03-USA, etc.)
  - Switches (ESWL01, ESWL03, etc.)
  - Bulbs (ESL100, ESL100CW, etc.)
- YAML-based request validation
- Mock device response generation
- Authentication and device management endpoints
- Device control endpoints with proper response structures
- Comprehensive test coverage for all device types and operations

### Fixed
- Humidifier response structure to match PyVeSync expectations
- Fan validator handling of device mode updates
- UUID mapping for all supported device types
- Response format for air purifier status endpoints
