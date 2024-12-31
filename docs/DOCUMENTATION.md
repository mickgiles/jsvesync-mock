# PyVeSync Mock Server Documentation

> Created and maintained by Claude (Anthropic) and Cursor AI

## Purpose
This is a mock server that validates PyVeSync library requests - it is NOT a full implementation:
- Only validates requests against YAML specs
- Returns minimal responses to satisfy PyVeSync
- Does not implement actual device functionality
- Enables testing without real devices

## Immutable Rules

### 1. API Specifications are Gospel
- YAML specs in `/api` directory define valid requests
- Specs cannot be modified under any circumstances
- All validation must exactly match spec requirements
- No deviations or extensions to specs allowed

### 2. PyVeSync Source is Gospel
- PyVeSync library source code defines expected response format
- Response data must be minimal but valid
- No modifications to PyVeSync source allowed
- Must adapt mock responses to satisfy PyVeSync

## Primary Directives

### 1. Request Validation
All requests must be validated exactly against YAML specifications:
- Field names must match exactly (case-sensitive)
- Required headers must be present and valid
- Auth fields (accountID/token) must be in correct format
- Request payload structure must match spec
- URL patterns must match exactly
- This validation must be done dynamically against the YAML specs and not hardcoded

### 2. Minimal Response Generation
Responses must be minimal but valid:
- Return only fields required by PyVeSync
- No actual device functionality or state
- Success responses must have `code: 0`
- Error responses must match PyVeSync codes
- Response format must match PyVeSync expectations

## API Documentation

### Authentication Endpoints

#### Login
- **Endpoint**: `/cloud/v1/user/login`
- **Method**: POST
- **Headers**:
  ```json
  {
    "Content-Type": "application/json; charset=UTF-8",
    "User-Agent": "okhttp/3.12.1"
  }
  ```
- **Request Format**:
  ```json
  {
    "acceptLanguage": "en",
    "appVersion": "2.8.6",
    "devToken": "",
    "email": "EMAIL",
    "method": "login",
    "password": "PASSWORD",
    "phoneBrand": "SM N9005",
    "phoneOS": "Android",
    "timeZone": "America/New_York",
    "traceId": "TRACE_ID",
    "userType": "1"
  }
  ```
- **Response Format**:
  ```json
  {
    "code": 0,
    "msg": null,
    "result": {
      "accountID": "mock_account_id",
      "token": "mock_token",
      "nickName": "Mock User",
      "acceptLanguage": "en"
    }
  }
  ```

### Device Management Endpoints

#### List Devices
- **Endpoint**: `/cloud/v1/deviceManaged/devices`
- **Method**: POST
- **Headers**:
  ```json
  {
    "Content-Type": "application/json; charset=UTF-8",
    "User-Agent": "okhttp/3.12.1",
    "tk": "token",
    "accountID": "account_id"
  }
  ```
- **Request Format**:
  ```json
  {
    "acceptLanguage": "en",
    "accountID": "account_id",
    "appVersion": "2.8.6",
    "method": "devices",
    "pageNo": "1",
    "pageSize": "100",
    "phoneBrand": "SM N9005",
    "phoneOS": "Android",
    "timeZone": "America/New_York",
    "token": "token",
    "traceId": "TRACE_ID"
  }
  ```
- **Response Format**:
  ```json
  {
    "code": 0,
    "msg": null,
    "result": {
      "total": number,
      "pageSize": number,
      "pageNo": 1,
      "list": Device[]
    }
  }
  ```

### Device Control Endpoints

#### Common Headers
All device control endpoints require these headers:
```json
{
  "Content-Type": "application/json; charset=UTF-8",
  "User-Agent": "okhttp/3.12.1",
  "tz": "America/New_York",
  "accept-language": "en"
}
```

Plus one of these auth combinations:
```json
{
  "tk": "token",
  "accountID": "account_id"
}
```
OR
```json
{
  "token": "token",
  "accountId": "account_id"
}
```

#### Device-Specific Endpoints

##### Core/Classic/Dual/LUH/LAP/LEH/XYD/ESL Devices
- **Base URL**: `/cloud/v2/deviceManaged/bypassV2`
- **Method**: POST
- **Request Format**:
  ```json
  {
    "acceptLanguage": "en",
    "accountID": "account_id",
    "appVersion": "2.8.6",
    "cid": "device_uuid",
    "configModule": "ConfigModule",
    "deviceRegion": "US",
    "method": "bypassV2",
    "phoneBrand": "SM N9005",
    "phoneOS": "Android",
    "timeZone": "America/New_York",
    "token": "token",
    "traceId": "TRACE_ID",
    "payload": {
      "data": {
        // Device-specific data
      },
      "method": "setSwitch",
      "source": "APP"
    }
  }
  ```

##### Outlet Devices (ESW15-USA, ESW03-USA, etc)
- **Base URL**: Varies by model (e.g., `/15a/v1/device/devicestatus`)
- **Method**: PUT/POST
- **Request Format**:
  ```json
  {
    "acceptLanguage": "en",
    "accountID": "account_id",
    "timeZone": "America/New_York",
    "token": "token",
    "uuid": "device_uuid",
    // Additional device-specific fields
  }
  ```

##### WiFi Switch 1.3
- **Base URLs**: 
  - `/v1/device/{uuid}/energy/month`
  - `/v1/wifi-switch-1.3/{uuid}/status/on`
  - `/v1/device/{uuid}/detail`
- **Methods**: GET/PUT
- **Headers Only**: No request body for GET/PUT methods

##### Air Purifier Devices

###### LV-PUR131S Air Purifier
- **Base URLs**: 
  - `/131airPurifier/v1/device/updateMode`
  - `/131airPurifier/v1/device/getPurifierStatus`
- **Methods**: PUT/GET
- **Response Format for Status**:
  ```json
  {
    "code": 0,
    "msg": "request success",
    "result": {
      "enabled": true,
      "filter_life": 100,
      "mode": "manual",
      "level": 1,
      "air_quality": "excellent",
      "display": true,
      "child_lock": false,
      "night_light": "off",
      "display_forever": false
    }
  }
  ```
- **Response Format for Mode Update**:
  ```json
  {
    "code": 0,
    "msg": "request success",
    "result": {
      "enabled": true,
      "mode": "sleep",
      "display": true,
      "display_forever": false
    }
  }
  ```
Note: Sleep mode does not require a level parameter, while manual mode requires it.

##### Humidifier Devices

###### Classic200S/Classic300S/Dual200S Humidifiers
- **Base URL**: `/cloud/v2/deviceManaged/bypassV2`
- **Method**: POST
- **Supported Methods**:
  - `getHumidifierStatus`
  - `setAutomaticStop`
  - `setHumidityMode`
  - `setTargetHumidity`
  - `setVirtualLevel`
  - `setSwitch`
  - `setDisplay`
- **Response Format for Status**:
  ```json
  {
    "code": 0,
    "msg": "request success",
    "result": {
      "code": 0,
      "result": {
        "enabled": true,
        "humidity": 45,
        "mist_virtual_level": 1,
        "mist_level": 1,
        "mode": "manual",
        "water_lacks": false,
        "humidity_high": false,
        "water_tank_lifted": false,
        "display": true,
        "automatic_stop_reach_target": false,
        "screenState": 1,
        "configuration": {
          "auto_target_humidity": 45,
          "display": true,
          "automatic_stop": false
        }
      }
    }
  }
  ```
- **Request Format for setAutomaticStop**:
  ```json
  {
    "method": "bypassV2",
    "cid": "device_uuid",
    "configModule": "VeSyncHumid200300S",
    "payload": {
      "method": "setAutomaticStop",
      "source": "APP",
      "data": {
        "enabled": true
      }
    }
  }
  ```
- **Request Format for setHumidityMode**:
  ```json
  {
    "method": "bypassV2",
    "cid": "device_uuid",
    "configModule": "VeSyncHumid200300S",
    "payload": {
      "method": "setHumidityMode",
      "source": "APP",
      "data": {
        "mode": "auto"
      }
    }
  }
  ```
- **Request Format for setTargetHumidity**:
  ```json
  {
    "method": "bypassV2",
    "cid": "device_uuid",
    "configModule": "VeSyncHumid200300S",
    "payload": {
      "method": "setTargetHumidity",
      "source": "APP",
      "data": {
        "humidity": 45
      }
    }
  }
  ```
- **Request Format for setVirtualLevel**:
  ```json
  {
    "method": "bypassV2",
    "cid": "device_uuid",
    "configModule": "VeSyncHumid200300S",
    "payload": {
      "method": "setVirtualLevel",
      "source": "APP",
      "data": {
        "level": 1
      }
    }
  }
  ```

###### Other Air Purifiers
- **Base URLs**: Same as LV-PUR131S
- **Methods**: PUT/GET
- **Response Format for Status**:
  ```json
  {
    "code": 0,
    "msg": "request success",
    "result": {
      "code": 0,
      "result": {
        "enabled": true,
        "filter_life": 100,
        "mode": "manual",
        "level": 1,
        "air_quality": 1,
        "display": true,
        "child_lock": false,
        "night_light": "off",
        "configuration": {
          "display": false,
          "display_forever": false
        }
      }
    }
  }
  ```
- **Response Format for Mode Update**:
  ```json
  {
    "code": 0,
    "msg": "request success",
    "result": {
      "code": 0,
      "result": {
        "status": "ok"
      }
    }
  }
  ```
Note: The key difference is that other air purifiers use a nested response format with an additional `code` and `result` wrapper.

## Implementation Details

### YAML Configuration
Device specifications are defined in YAML files:
```yaml
operation_name:
  headers:
    accept-language: en
    accountId: sample_id
    appVersion: 2.8.6
    content-type: application/json
    tk: sample_tk
    tz: America/New_York
  json_object:
    # Operation-specific fields
  method: post/get/put
  url: /endpoint/path
```

### Request Validation
1. Field names must match exactly as specified in YAML (case-sensitive)
2. Auth fields (accountID/token) are validated based on spec requirements
3. Headers and body fields are validated independently
4. Auth fields can appear in headers, body, or both as per spec

### Response Formats

#### Success Response
```json
{
  "code": 0,
  "msg": null,
  "result": {
    // Device-specific data
  }
}
```

#### Error Response
```json
{
  "code": error_code,
  "msg": error_message,
  "result": null
}
```

## Testing Guidelines

### API Testing with Pytest
1. Run the test suite using the following commands:
   ```bash
   # API endpoint tests
   source venv/bin/activate.fish; and python -m pytest tests/test_api.py -vv -s

   # PyVeSync client integration tests
   source venv/bin/activate.fish; and python -m pytest tests/test_pyvesync_api.py -vv -s

   # Full device feature tests
   source venv/bin/activate.fish; and python -m pytest tests/test_pyvesync_full.py -vv -s
   ```
2. Test each endpoint against its YAML spec
3. Verify exact field name matching
4. Test auth field combinations
5. Track test results by device and endpoint
6. Generate formatted test summary

### Test Organization
1. Tests are organized by device type and functionality
2. Fixtures provide common setup and teardown
3. Assertions validate response format and content
4. Test classes group related test cases
5. Clear test naming convention for readability

### Integration Testing
1. Test complete device workflows
2. Verify state transitions
3. Test concurrent operations
4. Validate response formats
5. Use pytest fixtures for common scenarios

## Dependencies
See requirements.txt for complete list:
- FastAPI 0.104.1
- Uvicorn 0.24.0
- Pydantic 2.5.2
- PyYAML 6.0.1
- Pytest 7.4.3
- Other supporting libraries

## Logging Standards
1. Use structured logging
2. Include request/response details
3. Log validation failures
4. Track state changes
5. Use appropriate log levels:
   - DEBUG: Request/response details
   - INFO: State changes
   - WARNING: Validation failures
   - ERROR: Operation failures
   - CRITICAL: System failures
