from typing import Dict, Any, Tuple
from fastapi import Request
from response_utils import get_success_response, get_error_response

async def validate_bulb_request(request: Request, data: Dict[str, Any], path: str, method: str, model: str, device_id: str, spec: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Handle bulb-specific request validation."""
    
    # Handle SmartBulb device detail endpoint
    if "/SmartBulb/v1/device/devicedetail" in path:
        response = {
            "code": 0,
            "msg": "request success",
            "deviceStatus": "on",
            "connectionStatus": "online",
            "brightNess": "100",  # Return as string since PyVeSync expects to parse it
            "colorTemp": 50,
            "colorMode": "white",
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
            "currentFirmVersion": "1.0.0",
            "deviceRegion": "US"
        }
        return True, response

    # Handle brightness update endpoint
    if "/SmartBulb/v1/device/updateBrightness" in path:
        if method.lower() == "put":
            # Get brightness from request
            brightness = data.get("brightNess", "100")  # Note: PyVeSync sends it as brightNess
            return True, {
                "code": 0,
                "msg": "request success"
            }

    # Handle device status endpoint
    if path.endswith("/devicestatus"):
        if method.lower() == "put":
            # Get device status from request
            device_status = "on"
            if data and isinstance(data, dict):
                device_status = data.get("status", "on")
            
            return True, {
                "code": 0,
                "msg": "request success",
                "result": {
                    "status": "ok",
                    "deviceStatus": device_status
                }
            }
        elif method.lower() == "get":
            return True, {
                "code": 0,
                "msg": "request success",
                "result": {
                    "deviceStatus": "on",
                    "connectionStatus": "online",
                    "brightness": 100,
                    "colorTemp": 50,
                    "colorMode": "white",
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
                    "currentFirmVersion": "1.0.0",
                    "deviceRegion": "US"
                }
            }

    # Handle RGB status endpoint
    if path.endswith("/devicergbstatus"):
        if method.lower() == "put":
            # Get RGB values from request if present
            rgb_value = data.get("rgbValue", {
                "red": 255,
                "green": 255,
                "blue": 255
            })
            return True, {
                "code": 0,
                "msg": "request success",
                "result": {
                    "status": "ok",
                    "rgb": {
                        "red": rgb_value.get("red", 255),
                        "green": rgb_value.get("green", 255),
                        "blue": rgb_value.get("blue", 255),
                        "brightness": 100
                    }
                }
            }

    # Handle getLightStatus
    if "getLightStatus" in str(data):
        if "VeSyncBulbValcenoA19MC" in str(data.get("configModule", "")):
            return True, {
                "code": 0,
                "msg": "request success",
                "result": {
                    "result": {
                        "enabled": True,
                        "brightness": 100,
                        "colorTemp": 50,
                        "colorMode": "white",
                        "hue": 0,
                        "saturation": 0,
                        "value": 100
                    }
                }
            }
            
        if "VeSyncBulbESL100MC" in str(data.get("configModule", "")):
            return True, {
                "code": 0,
                "msg": "request success",
                "result" : {
                    "code": 0,
                    "msg": "request success",
                    "result": {
                        "brightness": 100,
                        "colorMode": "color",
                        "red": 255,
                        "green": 0,
                        "blue": 0
                    }
                }
            }
        
        return True, {
            "code": 0,
            "msg": "request success",
            "result": {
                "light": {
                    "action": "on",
                    "brightness": 100,
                    "colorTempe": 50
                }
            }
        }

    # Handle getLightStatusV2
    if "getLightStatusV2" in str(data):
        if "VeSyncBulbValcenoA19MC" in str(data.get("configModule", "")):
            return True, {
                "code": 0,
                "msg": "request success",
                "result": {
                    "enabled": True,
                    "brightness": 100,
                    "colorTemp": 50,
                    "colorMode": "white",
                    "hue": 0,
                    "saturation": 0,
                    "value": 100
                }
            }
            
        return True, {
            "code": 0,
            "msg": "request success",
            "result": {
                "enabled": True,
                "brightness": 100,
                "colorTemp": 50
            }
        }

    # For now, return basic success for other endpoints
    return True, get_success_response({"status": "ok"})
