"""Switch-specific request validators for VeSync mock server."""

from typing import Dict, Any, Tuple
from fastapi import Request
from response_utils import get_success_response, get_error_response

async def validate_switch_request(request: Request, data: Dict[str, Any], path: str, method: str, model: str, device_id: str, spec: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Handle switch-specific request validation."""
    
    # Handle device status endpoint
    if path.endswith("/devicestatus") or "/inwallswitch/v1/device/devicestatus" in path:
        if method.lower() == "put":
            # Get device status from request
            device_status = "on"
            if data and isinstance(data, dict):
                device_status = data.get("status", "on")
            
            result = {
                "status": "ok",
                "deviceStatus": device_status
            }
            return True, get_success_response(result)
        elif method.lower() == "get":
            result = {
                "deviceStatus": "on",
                "connectionStatus": "online",
                "power": 50.0,
                "voltage": 120.0,
                "energy": 1.5,
                "activeTime": 3600,
                "deviceName": f"Mock {model}",
                "deviceImg": "",
                "connectionType": "wifi",
                "cid": device_id,
                "deviceType": model,
                "type": model,
                "uuid": device_id,
                "configModule": spec.get("get_status", {}).get("json_object", {}).get("configModule", "ConfigModule"),
                "macID": "52:54:00:00:00:00",
                "mode": "auto",
                "speed": 1,
                "currentFirmVersion": "1.0.0",
                "deviceRegion": "US",
                "subDeviceNo": 0
            }
            return True, get_success_response(result)

    # Handle in-wall switch detail endpoint
    if "/inwallswitch/v1/device/devicedetail" in path:
        result = {
            "deviceStatus": "on",
            "connectionStatus": "online",
            "power": 50.0,
            "voltage": 120.0,
            "energy": 1.5,
            "activeTime": 3600,
            "deviceName": f"Mock {model}",
            "deviceImg": "",
            "connectionType": "wifi",
            "cid": device_id,
            "deviceType": model,
            "type": model,
            "uuid": device_id,
            "configModule": spec.get("get_status", {}).get("json_object", {}).get("configModule", "ConfigModule"),
            "macID": "52:54:00:00:00:00",
            "mode": "auto",
            "speed": 1,
            "currentFirmVersion": "1.0.0",
            "deviceRegion": "US",
            "subDeviceNo": 0
        }
        return True, get_success_response(result)

    return True, get_success_response({
        "status": "ok"
    })
