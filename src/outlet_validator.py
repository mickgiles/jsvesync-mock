"""Outlet-specific request validators for VeSync mock server."""

from typing import Dict, Any, Tuple
from fastapi import Request
from response_utils import get_success_response, get_error_response

async def validate_outlet_request(request: Request, data: Dict[str, Any], path: str, method: str, model: str, device_id: str, spec: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Handle outlet-specific request validation."""
    
    # Handle wifi-switch-1.3 status
    if "/wifi-switch-1.3/" in path and "/status/" in path:
        status = path.split("/")[-1]
        if status in ["on", "off"]:
            result = {
                "status": "ok",
                "deviceStatus": status
            }
            return True, get_success_response(result)
    
    # Handle device status endpoint
    if path.endswith("/devicestatus") or "/15a/v1/device/devicestatus" in path:
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
                "nightLightStatus": "auto",
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

    # Handle 15A outlet detail endpoint
    if "/15a/v1/device/devicedetail" in path:
        result = {
            "deviceStatus": "on",
            "connectionStatus": "online",
            "power": 50.0,
            "voltage": 120.0,
            "energy": 1.5,
            "nightLightStatus": "auto",
            "nightLightAutomode": "auto",
            "nightLightBrightness": 50,
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

    # Handle outdoor socket detail endpoint
    if "/outdoorsocket15a/v1/device/devicedetail" in path:
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
            "subDeviceNo": 0,
            "subDevices": [
                {
                    "subDeviceNo": 1,
                    "subDeviceStatus": "on",
                    "power": 50.0,
                    "voltage": 120.0,
                    "energy": 1.5,
                    "energyToday": 1.5,
                    "activeTime": 3600
                }
            ]
        }
        return True, get_success_response(result)

    # Handle energy history endpoints
    if path.endswith("/energyweek") or path.endswith("/energy/week"):
        result = {
            "energyConsumptionOfToday": 1.5,
            "costPerKWH": 0.12,
            "maxEnergy": 10.0,
            "totalEnergy": 7.5,
            "data": [1.0, 1.5, 1.0, 1.0, 1.5, 1.0, 0.5]
        }
        return True, get_success_response(result)
    
    if path.endswith("/energymonth") or path.endswith("/energy/month"):
        result = {
            "energyConsumptionOfToday": 1.5,
            "costPerKWH": 0.12,
            "maxEnergy": 30.0,
            "totalEnergy": 45.0,
            "data": [1.5] * 30
        }
        return True, get_success_response(result)
    
    if path.endswith("/energyyear") or path.endswith("/energy/year"):
        result = {
            "energyConsumptionOfToday": 1.5,
            "costPerKWH": 0.12,
            "maxEnergy": 100.0,
            "totalEnergy": 365.0,
            "data": [1.0] * 12
        }
        return True, get_success_response(result)

    # Handle nightlight status endpoint
    if path.endswith("/nightlightstatus"):
        if method.lower() == "put":
            result = {
                "status": "ok"
            }
            return True, get_success_response(result)

    return True, get_success_response({
        "status": "ok"
    })
