"""Fan device response validators."""

from typing import Dict, Any, Tuple
from fastapi import Request

class BaseDeviceResponse:
    """Base response class for all VeSync devices."""
    
    def __init__(self, model: str, device_id: str):
        """Initialize base response."""
        self.base = {
            "deviceName": f"Mock {model}",
            "cid": device_id,
            "model": model,
            "subDeviceNo": "0",
            "code": 0,
            "msg": "success",
            "deviceStatus": "on",
            "connectionStatus": "online",
            "deviceType": model,
            "deviceId": device_id,
            "uuid": device_id
        }
    
    def get_base(self) -> Dict[str, Any]:
        """Get device base in format matching displayJSON()."""
        return self.base

class AirBypassResponse(BaseDeviceResponse):
    """Response for VeSyncAirBypass devices (Core*, LAP-*)."""
    
    def __init__(self, model: str, device_id: str):
        """Initialize air bypass response."""
        super().__init__(model, device_id)
        self.base.update({            
            "enabled": True,        
            "filter_life": 7,
            "mode": "auto",
            "level": 1,
            "display": False,
            "child_lock": False,
            "night_light": "on",
            "air_quality": 2,
            "air_quality_value": 2,
            "configuration": {
                "display": False,
                "display_forever": False
            }
        })

class AirBaseV2Response(AirBypassResponse):
    """Response for VeSyncAirBaseV2 devices (Vital100S, Vital200S, EverestAir)."""
    
    def __init__(self, model: str, device_id: str):
        """Initialize air base v2 response."""
        super().__init__(model, device_id)


class Air131Response(BaseDeviceResponse):
    """Response for VeSyncAir131 devices (LV-PUR131S, LV-RH131S)."""
    
    def __init__(self, model: str, device_id: str):
        """Initialize air 131 response."""
        super().__init__(model, device_id)
        self.base.update({
            "deviceStatus": "on",
            "connectionStatus": "online",
            "activeTime": 5,
            "filterLife": {
                "percent": 100,
                "timestamp": "2024-01-01"
            },
            "screenStatus": "on",
            "mode": "auto",
            "level": 1,
            "airQuality": "excellent",
            "configuration": {
                "auto_target_humidity": 50,
                "display": True,
                "automatic_stop": True
            }
        })

class TowerFanResponse(AirBaseV2Response):
    """Response for VeSyncTowerFan devices (LTF-F422S series)."""
    
    def __init__(self, model: str, device_id: str):
        """Initialize tower fan response."""
        super().__init__(model, device_id)

class Humid200300SResponse(BaseDeviceResponse):
    """Response for VeSyncHumid200300S devices (Classic300S, LV600S, OASISMIST)."""
    
    def __init__(self, model: str, device_id: str):
        """Initialize humidifier response."""
        super().__init__(model, device_id)
        self.base.update({
            "deviceStatus": "on",
            "connectionStatus": "online",  
            "enabled": True,
            "humidity": 45,
            "mist_virtual_level": 1,
            "mist_level": 1,
            "mode": "auto",
            "water_lacks": False,
            "humidity_high": False,
            "water_tank_lifted": False,
            "automatic_stop_reach_target": True,
            "night_light_brightness": 0,  
            "warm_level": 1,
            "warm_enabled": True,
            "display": True,
            "indicator_light_switch": True,
            "configuration": {
                "auto_target_humidity": 50,
                "display": True,
                "automatic_stop": True
            }
        })

class Humid200SResponse(Humid200300SResponse):
    """Response for VeSyncHumid200S devices (Classic200S)."""
    
    def __init__(self, model: str, device_id: str):
        """Initialize Classic200S response."""
        super().__init__(model, device_id)

class Superior6000SResponse(BaseDeviceResponse):
    """Response for VeSyncSuperior6000S devices (LEH-S601S series)."""
    
    def __init__(self, model: str, device_id: str):
        """Initialize Superior6000S response."""
        super().__init__(model, device_id)
        self.base.update({
            "powerSwitch": 1,
            "workMode": "autoPro",
            "deviceStatus": "on",
            "connectionStatus": "online",  
            "enabled": True,
            "humidity": 45,
            "targetHumidity": 45,
            "virtualLevel": 1,
            "mistLevel": 1,
            "mist_virtual_level": 1,
            "mist_level": 1,
            "mode": "auto",
            "waterLacksState": False,
            "waterTankLifted": False,
            "filterLifePercent": 100,
            "temperature": 25,
            "screenSwitch": True,
            "dryingMode": {},
            "waterLacksState": False,
            "waterTankLifted": False
        })

class Humid1000SResponse(Humid200300SResponse):
    """Response for VeSyncHumid1000S devices (OASISMIST1000S)."""
    
    def __init__(self, model: str, device_id: str):
        """Initialize OASISMIST1000S response."""
        super().__init__(model, device_id)
        self.base.update({
            "powerSwitch": 1,
            "virtualLevel": 1,
            "mistLevel": 1,
            "workMode": "manual",
            "waterLacksState": False,
            "targetHumidity": 45,
            "humidity": 45,
            "waterTankLifted": False,
            "autoStopState": 1,
            "screenState": True,
            "screenSwitch": True,
            "autoStopSwitch": 1
        })

def get_device_response(model: str, device_id: str, method: str = None) -> Dict[str, Any]:
    """Get device response based on model and method."""
    response_class = None
    
    # Map config modules to response classes
    if model == "VeSyncAirBypass":  # Core200S, Core300S, Core400S, Core600S
        response_class = AirBypassResponse
    elif model == "VeSyncAirBaseV2":  # Vital100S, Vital200S, EverestAir
        response_class = AirBaseV2Response
    elif model == "VeSyncAir131":  # LV-PUR131S, LV-RH131S
        response_class = Air131Response
    elif model == "VeSyncTowerFan":  # SmartTowerFan series
        response_class = TowerFanResponse
    elif model == "VeSyncHumid200300S":  # Classic300S, LV600S, OASISMIST
        response_class = Humid200300SResponse
    elif model == "VeSyncHumid200S":  # Classic200S
        response_class = Humid200SResponse
    elif model == "VeSyncSuperior6000S":  # Superior6000S
        response_class = Superior6000SResponse
    elif model == "VeSyncHumid1000S":  # OASISMIST1000S
        response_class = Humid1000SResponse
    else:
        response_class = BaseDeviceResponse
    
    device_response = response_class(model, device_id)
    return device_response.get_base()

async def validate_fan_request(request: Request, data: Dict[str, Any], path: str, method: str, model: str, id: str, spec: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Validate fan request and return appropriate response.
    
    Args:
        request: The FastAPI request object
        data: The request JSON data
        path: The request path
        method: The HTTP method
        model: The device model
        device_id: The device ID
        spec: The device spec from YAML
        
    Returns:
        Tuple of (is_valid, response_dict)
    """
    # Extract required fields
    config_module = data.get("configModule")
    payload = data.get("payload", {})
    request_method = payload.get("method", "")

    # Special handling for Air131 devices
    if config_module == "VeSyncAir131" or path.startswith("/131airPurifier"):

        # Handle device details request
        if path == "/131airPurifier/v1/device/deviceDetail":
            device = Air131Response("LV-PUR131S", id)
            return True, device.get_base()
            
        # Handle speed and mode changes
        else :
            return True, {
                    "code": 0,
                    "msg": "request success"
            }
    else:
        # Validate required fields
        if not all([id, config_module]):
            return False, {"code": 400, "msg": "Missing required fields"}

        return True, {
            "code": 0,
            "msg": "request success",
            "result": {
                "code": 0,
                "msg": None,
                "result": get_device_response(config_module, id, request_method)
            }
        } 