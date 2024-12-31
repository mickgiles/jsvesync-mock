"""Request validators for VeSync mock server."""

from typing import Dict, Any, Tuple, Optional
import yaml
import uuid
import re
import hashlib
from fastapi import Request
from pathlib import Path
from constants import (
    MOCK_ACCOUNT_ID, 
    MOCK_TOKEN, 
    DEVICE_UUIDS,
    VALID_EMAIL,
    VALID_PASSWORD,
    ERROR_CODES
)
from outlet_validator import validate_outlet_request
from switch_validator import validate_switch_request
from bulb_validator import validate_bulb_request
from fan_validator import validate_fan_request
from response_utils import get_success_response, get_error_response

# Common headers required for all endpoints
COMMON_HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "User-Agent": "okhttp/3.12.1"
}

def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent

def _load_device_specs() -> Dict[str, Any]:
    """Load and analyze all device YAML specs.
    
    Returns:
        Dictionary containing device configurations and mappings
    """
    api_dir = get_project_root() / "api"
    specs = {}
    url_to_model = {}
    
    # Load all device specs
    for device_type in ["vesyncoutlet", "vesyncfan", "vesyncbulb", "vesyncswitch"]:
        device_dir = api_dir / device_type
        if device_dir.exists():
            for spec_file in device_dir.glob("*.yaml"):
                with open(spec_file) as f:
                    spec = yaml.safe_load(f)
                    model = spec_file.stem
                    specs[model] = {
                        "spec": spec,
                        "dir": device_type,
                        "base_paths": set()
                    }
                    
                    # Extract base paths from URLs
                    for op_name, op_spec in spec.items():
                        if "url" in op_spec:
                            url = op_spec["url"]
                            # Extract base path (first part of URL)
                            base_path = url.split("/")[1] if url.startswith("/") else url.split("/")[0]
                            specs[model]["base_paths"].add(base_path)
                            url_to_model[base_path] = model
                            
                            # Also map full paths for more specific matches
                            path_parts = url.split("/")
                            if len(path_parts) > 2:
                                full_path = "/".join(path_parts[:3])
                                url_to_model[full_path] = model
                                
                                # For deviceManaged endpoints, also map the full path
                                if "deviceManaged" in path_parts:
                                    full_path = "/".join(path_parts)
                                    url_to_model[full_path] = model
    
    return {
        "specs": specs,
        "url_to_model": url_to_model
    }

# Load specs at module initialization
DEVICE_SPECS = _load_device_specs()

async def validate_headers(request: Request, required_headers: Optional[Dict[str, str]] = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Validate request headers against spec.
    
    Args:
        request: The FastAPI request object
        required_headers: Optional dict of required headers from spec
        
    Returns:
        Tuple of (is_valid, error_response)
    """
    headers = request.headers
    
    # Check common headers first
    for header, value in COMMON_HEADERS.items():
        if header not in headers:
            return False, get_error_response(f"Missing required header: {header}")
    
    # If no additional headers required, return success
    if not required_headers:
        return True, None
    
    # Check additional required headers
    for header in required_headers:
        if header not in headers:
            return False, get_error_response(f"Missing required header: {header}")
    
    return True, None

def get_device_id_from_url(url: str, device_id: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Extract device ID from URL or request data.
    
    Args:
        url: The request URL
        device_id: Optional device ID from path parameter
        data: Optional request data that might contain device ID
        
    Returns:
        The extracted device ID or None
    """
    # If device_id is provided from path parameter, use it
    if device_id:
        return device_id
        
    # Try to find UUID pattern in URL
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    if match := re.search(uuid_pattern, url, re.IGNORECASE):
        return match.group(0)
    
    # Try to find CID pattern in wifi switch format
    if 'wifi-switch-1.3' in url:
        # Extract device ID from path parameter format
        parts = url.split('/')
        for i, part in enumerate(parts):
            if part == 'wifi-switch-1.3' and i + 1 < len(parts):
                return parts[i + 1]
    
    # Try to find device ID in request data
    if data:
        # Check for cid in root level
        if "cid" in data:
            return data["cid"]
        # Check for uuid in root level
        if "uuid" in data:
            return data["uuid"]
        # Check for deviceid in root level
        if "deviceid" in data:
            return data["deviceid"]
        # Check for cid in payload
        if "payload" in data and isinstance(data["payload"], dict):
            payload = data["payload"]
            if "data" in payload and isinstance(payload["data"], dict):
                if "cid" in payload["data"]:
                    return payload["data"]["cid"]
                if "uuid" in payload["data"]:
                    return payload["data"]["uuid"]
                if "deviceid" in payload["data"]:
                    return payload["data"]["deviceid"]
    
    return None

def get_yaml_spec_for_model(model: str) -> Optional[Dict]:
    """Load YAML spec for given device model."""
    # If the model is a URL path, map it to actual model
    if model in DEVICE_SPECS["url_to_model"]:
        model = DEVICE_SPECS["url_to_model"][model]
    elif '/' in model:  # If it's a URL path like 'inwallswitch/v1/device/devicestatus'
        base_path = model.split('/')[0]  # Get the first part of the path
        if base_path in DEVICE_SPECS["url_to_model"]:
            model = DEVICE_SPECS["url_to_model"][base_path]
    
    # Get spec for model
    if model in DEVICE_SPECS["specs"]:
        return DEVICE_SPECS["specs"][model]["spec"]
            
    return None

async def validate_login(request: Request, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Validate login request against YAML spec.
    
    Args:
        request: The FastAPI request object
        data: The request JSON data
        
    Returns:
        Tuple of (is_valid, response_dict)
    """
    # Load YAML spec
    vesync_yaml = get_project_root() / "api" / "vesync" / "VeSync.yaml"
    with open(vesync_yaml) as f:
        spec = yaml.safe_load(f)
    
    # Get login spec
    login_spec = spec["login"]
    
    # Check headers
    is_valid, error_response = await validate_headers(request, login_spec.get("headers"))
    if not is_valid:
        return False, error_response

    # Validate request fields match YAML spec
    is_valid, error_response = await validate_request_fields(data, login_spec)
    if not is_valid:
        return False, error_response
    
    # Check all required fields from spec
    for field in login_spec["json_object"]:
        # Check field presence
        if field not in data:
            return False, get_error_response(f"Missing required field: {field}")
        
        # Check field type
        if not isinstance(data[field], str):
            return False, get_error_response(f"Field {field} must be of type str")
    
    # Check for required login fields
    if "email" not in data or not data["email"]:
        return False, get_error_response(ERROR_CODES["missing_email"]["msg"], ERROR_CODES["missing_email"]["code"])
    
    if "password" not in data or not data["password"]:
        return False, get_error_response(ERROR_CODES["missing_password"]["msg"], ERROR_CODES["missing_password"]["code"])
    
    # Validate credentials
    if data["email"] != VALID_EMAIL:
        return False, get_error_response(ERROR_CODES["invalid_credentials"]["msg"], ERROR_CODES["invalid_credentials"]["code"])
    
    # Check hashed password
    if data["password"] != VALID_PASSWORD:
        return False, get_error_response(ERROR_CODES["invalid_credentials"]["msg"], ERROR_CODES["invalid_credentials"]["code"])
            
    # Return successful response with account details
    result = {
        "accountID": MOCK_ACCOUNT_ID,
        "token": MOCK_TOKEN,
        "nickName": "Mock User",
        "avatarIcon": "",
        "acceptLanguage": "en",
        "gdprStatus": True,
        "termsStatus": True,
        "privacyStatus": True,
        "userType": 1
    }
    return True, get_success_response(result)

def get_supported_devices() -> list:
    """Get list of all devices supported by PyVeSync."""
    # Get all device modules
    from pyvesync import vesyncfan, vesyncoutlet, vesyncswitch, vesyncbulb
    
    devices = []
    
    # Clear existing device mappings
    DEVICE_UUIDS.clear()
    
    def create_device(model: str, config_module: str) -> Dict[str, Any]:
        """Create a device with all required fields."""
        # Skip the duplicate CS137-AF/CS158-AF model
        if model == "CS137-AF/CS158-AF":
            return None
        
        # Use a deterministic UUID based on the model name
        device_uuid = str(uuid.UUID(bytes=hashlib.md5(model.encode()).digest()))
        DEVICE_UUIDS[device_uuid] = model
        
        # Base device details
        device = {
            "deviceName": f"Mock {model}",
            "deviceImg": f"https://image.vesync.com/{model}.png",
            "cid": device_uuid,
            "connectionStatus": "online",
            "connectionType": "wifi",
            "deviceType": model,
            "type": model,
            "uuid": device_uuid,
            "configModule": config_module,
            "macID": f"52:54:00:{uuid.uuid4().hex[:6]}",
            "mode": "auto",
            "speed": 1,
            "extension": {
                "fanSpeedLevel": 1,
                "mode": "auto"
            },
            "currentFirmVersion": "1.0.0",
            "deviceRegion": "US",
            "deviceStatus": "on",
            "subDeviceNo": 0,
            "pid": f"pid_{model}"
        }
        return device
    
    # Add fan devices
    for model in vesyncfan.fan_modules:
        device = create_device(model, vesyncfan.fan_modules[model])
        if device:
            devices.append(device)
    
    # Add outlet devices
    for model in vesyncoutlet.outlet_modules:
        device = create_device(model, vesyncoutlet.outlet_modules[model])
        if device:
            devices.append(device)
    
    # Add switch devices
    for model in vesyncswitch.switch_modules:
        device = create_device(model, vesyncswitch.switch_modules[model])
        if device:
            devices.append(device)
    
    # Add bulb devices
    for model in vesyncbulb.bulb_modules:
        device = create_device(model, vesyncbulb.bulb_modules[model])
        if device:
            devices.append(device)
    
    return devices

async def validate_auth(request: Request, data: Dict[str, Any], operation_spec: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Validate accountID and token in request data and headers.
    
    Args:
        request: The FastAPI request object
        data: The request JSON data
        operation_spec: The operation specification from YAML
        
    Returns:
        Tuple of (is_valid, error_response)
    """
    headers = request.headers
    
    # Extract exact field names from spec
    header_account_id = None
    header_tokens = []
    body_account_id = None
    body_tokens = []
    
    # Get header field names from spec
    if operation_spec and "headers" in operation_spec:
        spec_headers = operation_spec["headers"]
        header_account_id = next((h for h in spec_headers if h.lower() == "accountid"), None)
        header_tokens = [h for h in spec_headers if h in ["token", "tk"]]
    
    # Get body field names from spec
    if operation_spec and "json_object" in operation_spec:
        json_obj = operation_spec["json_object"]
        body_account_id = next((f for f in json_obj if f.lower() == "accountid"), None)
        body_tokens = [f for f in json_obj if f in ["token", "tk"]]
    
    # If no auth fields required, skip validation
    if not any([header_account_id, header_tokens, body_account_id, body_tokens]):
        return True, None
    
    # Validate accountID fields
    account_id_values = []
    
    # Check header accountID if required
    if header_account_id and header_account_id in headers:
        account_id_values.append(headers[header_account_id])
    
    # Check body accountID if required
    if body_account_id and body_account_id in data:
        account_id_values.append(data[body_account_id])
    
    # Validate accountID values
    if account_id_values:
        if any(id != MOCK_ACCOUNT_ID for id in account_id_values):
            return False, get_error_response("Invalid accountID")
    
    # Validate token fields
    token_values = []
    
    # Check header tokens if required
    for token_field in header_tokens:
        if token_field in headers:
            token_values.append(headers[token_field])
    
    # Check body tokens if required
    for token_field in body_tokens:
        if token_field in data:
            token_values.append(data[token_field])
    
    # Validate token values
    if token_values:
        if any(tk != MOCK_TOKEN for tk in token_values):
            return False, get_error_response("Invalid token")
    
    return True, None

async def validate_request_fields(data: Dict[str, Any], operation_spec: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Validate that all request fields are defined in the YAML spec."""
    if "json_object" not in operation_spec:
        return True, None

    allowed_fields = set(operation_spec["json_object"].keys())
    request_fields = set(data.keys())

    # Find fields in request that aren't in spec
    undefined_fields = request_fields - allowed_fields
    if undefined_fields:
        return False, get_error_response(f"Undefined fields in request: {', '.join(undefined_fields)}")

    return True, None

async def validate_device_request(request: Request, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Validate device request against spec."""
    # Get device ID from URL or request data
    device_id = get_device_id_from_url(str(request.url), None, data)
    if not device_id:
        return False, get_error_response("Device ID not found in request")
    
    # Get device model from UUID mapping
    model = DEVICE_UUIDS.get(device_id)
    if not model:
        # For bypass V2 endpoint, try to determine model from configModule
        if data.get("method") == "bypassV2" and "configModule" in data:
            config_module = data["configModule"]
            if "VeSyncAirBypass" in config_module:
                model = "Core200S"  # Default to Core200S for air purifiers
            elif "VeSyncHumid200300S" in config_module:
                model = "Classic300S"  # Default to Classic300S for humidifiers
    
    if not model:
        return False, get_error_response(f"Device not found: {device_id}")
    
    # Get YAML spec for model
    spec = get_yaml_spec_for_model(model)
    if not spec:
        return False, get_error_response(f"No spec found for model: {model}")

    # Get path and method
    path = request.url.path
    method = request.method.lower()

    # Check if this is a bulb request
    if model.startswith(("ESL", "XYD")):
        return await validate_bulb_request(request, data, path, method, model, device_id, spec)

    # Check if this is an outlet request
    elif model.startswith(("ESW", "ESO", "wifi-switch-1.3")):
        return await validate_outlet_request(request, data, path, method, model, device_id, spec)
        
    # Check if this is a switch request
    elif model.startswith("ESW"):
        return await validate_switch_request(request, data, path, method, model, device_id, spec)

    # Check if this is a fan/humidifier request
    elif model.startswith(("CLA", "COR", "DUA", "LEH", "LAP", "LUH", "LV-", "LTF", "Core")) or "VeSyncHumid" in str(data.get("configModule", "")):
        return await validate_fan_request(request, data, path, method, model, device_id, spec)

    else:
        print("ERROR, no handler configured")
        return False, get_error_response("No handler configured")
    
async def validate_stored_ids(request: Request, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Validate stored device IDs in request data.
    
    Args:
        request: The FastAPI request object
        data: The request JSON data
        
    Returns:
        Tuple of (is_valid, error_response)
    """
    # Get device IDs from request data
    device_ids = []
    
    # Check for deviceId field
    if "deviceId" in data:
        device_ids.append(data["deviceId"])
    
    # Check for uuid field
    if "uuid" in data:
        device_ids.append(data["uuid"])
    
    # Check for cid field
    if "cid" in data:
        device_ids.append(data["cid"])
    
    # Check for list of device IDs
    if "deviceList" in data and isinstance(data["deviceList"], list):
        for device in data["deviceList"]:
            if isinstance(device, dict):
                if "deviceId" in device:
                    device_ids.append(device["deviceId"])
                if "uuid" in device:
                    device_ids.append(device["uuid"])
                if "cid" in device:
                    device_ids.append(device["cid"])
    
    # If no device IDs found, return success
    if not device_ids:
        return True, None
    
    # Validate all device IDs exist in our mapping
    for device_id in device_ids:
        if device_id not in DEVICE_UUIDS:
            return False, get_error_response(f"Device not found: {device_id}")
    
    return True, None
    
async def validate_devices(request: Request, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Validate devices request against YAML spec.
    
    Args:
        request: The FastAPI request object
        data: The request JSON data
        
    Returns:
        Tuple of (is_valid, response_dict)
    """
    # First validate all stored IDs
    is_valid, error_response = await validate_stored_ids(request, data)
    if not is_valid:
        return False, error_response
        
    # Load YAML spec
    vesync_yaml = get_project_root() / "api" / "vesync" / "VeSync.yaml"
    with open(vesync_yaml) as f:
        spec = yaml.safe_load(f)
    
    # Get devices spec
    devices_spec = spec["get_devices"]
    
    # Check auth first
    is_valid, error_response = await validate_auth(request, data, devices_spec)
    if not is_valid:
        return False, error_response
    
    # Check headers
    is_valid, error_response = await validate_headers(request, devices_spec.get("headers"))
    if not is_valid:
        return False, error_response

    # Validate request fields match YAML spec
    is_valid, error_response = await validate_request_fields(data, devices_spec)
    if not is_valid:
        return False, error_response
    
    # Check all required fields from spec
    for field in devices_spec["json_object"]:
        # Check field presence
        if field not in data:
            return False, get_error_response(f"Missing required field: {field}")
        
        # Check field type
        if not isinstance(data[field], str):
            return False, get_error_response(f"Field {field} must be of type str")
    
    # Get list of supported devices
    device_list = get_supported_devices()
            
    # Return successful response with device list
    result = {
        "total": len(device_list),
        "pageSize": 100,
        "pageNo": 1,
        "list": device_list
    }
    return True, get_success_response(result)
    