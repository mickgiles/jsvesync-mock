"""API routes for VeSync mock server."""

from fastapi import APIRouter, Request
from typing import Dict, Any
from validators import validate_login, validate_devices, validate_device_request, DEVICE_UUIDS

router = APIRouter()

# 10A Outlet Routes
@router.post("/10a/v1/device/devicedetail")
@router.post("/10a/v1/device/devicestatus")
@router.put("/10a/v1/device/devicestatus")
@router.post("/10a/v1/device/energymonth")
@router.post("/10a/v1/device/energyweek")
@router.post("/10a/v1/device/energyyear")
async def outlet_10a(request: Request, data: Dict[str, Any]):
    """Handle 10A outlet requests."""
    is_valid, response = await validate_device_request(request, data)
    return response

# Air Purifier Routes
@router.post("/131airPurifier/v1/device/deviceDetail")
@router.put("/131airPurifier/v1/device/deviceDetail")
@router.post("/131airPurifier/v1/device/deviceStatus")
@router.put("/131airPurifier/v1/device/deviceStatus")
@router.post("/131airPurifier/v1/device/updateMode")
@router.put("/131airPurifier/v1/device/updateMode")
@router.post("/131airPurifier/v1/device/updateSpeed")
@router.put("/131airPurifier/v1/device/updateSpeed")
async def air_purifier(request: Request, data: Dict[str, Any]):
    """Handle air purifier requests."""
    is_valid, response = await validate_device_request(request, data)
    return response

# 15A Outlet Routes
@router.post("/15a/v1/device/devicedetail")
@router.post("/15a/v1/device/devicestatus")
@router.put("/15a/v1/device/devicestatus")
@router.post("/15a/v1/device/energymonth")
@router.post("/15a/v1/device/energyweek")
@router.post("/15a/v1/device/energyyear")
@router.post("/15a/v1/device/nightlightstatus")
@router.put("/15a/v1/device/nightlightstatus")
async def outlet_15a(request: Request, data: Dict[str, Any]):
    """Handle 15A outlet requests."""
    is_valid, response = await validate_device_request(request, data)
    return response

# Smart Bulb Routes
@router.post("/SmartBulb/v1/device/devicedetail")
@router.post("/SmartBulb/v1/device/devicestatus")
@router.put("/SmartBulb/v1/device/devicestatus")
@router.post("/SmartBulb/v1/device/updateBrightness")
@router.put("/SmartBulb/v1/device/updateBrightness")
async def smart_bulb(request: Request, data: Dict[str, Any]):
    """Handle smart bulb requests."""
    is_valid, response = await validate_device_request(request, data)
    return response

# Cloud Routes
@router.post("/cloud/v1/deviceManaged/bypass")
@router.post("/cloud/v2/deviceManaged/bypassV2")
async def cloud_bypass(request: Request, data: Dict[str, Any]):
    """Handle cloud bypass requests."""
    is_valid, response = await validate_device_request(request, data)
    return response

@router.post("/cloud/v2/deviceManaged/configurationsV2")
async def configurations_v2(request: Request, data: Dict[str, Any]):
    """Handle device configuration requests."""
    is_valid, response = await validate_device_request(request, data)
    return response

@router.post("/cloud/v1/deviceManaged/devices")
@router.post("/cloud/v2/deviceManaged/devices")
async def devices(request: Request, data: Dict[str, Any]):
    """Handle device listing requests."""
    is_valid, response = await validate_devices(request, data)
    return response

@router.post("/cloud/v1/user/login")
async def login(request: Request, data: Dict[str, Any]):
    """Handle login requests."""
    is_valid, response = await validate_login(request, data)
    return response

# Dimmer Routes
@router.post("/dimmer/v1/device/devicedetail")
@router.post("/dimmer/v1/device/devicergbstatus")
@router.put("/dimmer/v1/device/devicergbstatus")
@router.post("/dimmer/v1/device/devicestatus")
@router.put("/dimmer/v1/device/devicestatus")
@router.post("/dimmer/v1/device/indicatorlightstatus")
@router.put("/dimmer/v1/device/indicatorlightstatus")
@router.post("/dimmer/v1/device/updatebrightness")
@router.put("/dimmer/v1/device/updatebrightness")
async def dimmer(request: Request, data: Dict[str, Any]):
    """Handle dimmer requests."""
    is_valid, response = await validate_device_request(request, data)
    return response

# In-Wall Switch Routes
@router.post("/inwallswitch/v1/device/devicedetail")
@router.post("/inwallswitch/v1/device/devicestatus")
@router.put("/inwallswitch/v1/device/devicestatus")
async def inwall_switch(request: Request, data: Dict[str, Any]):
    """Handle in-wall switch requests."""
    is_valid, response = await validate_device_request(request, data)
    return response

# Outdoor Socket Routes
@router.post("/outdoorsocket15a/v1/device/devicedetail")
@router.post("/outdoorsocket15a/v1/device/devicestatus")
@router.put("/outdoorsocket15a/v1/device/devicestatus")
@router.post("/outdoorsocket15a/v1/device/energymonth")
@router.post("/outdoorsocket15a/v1/device/energyweek")
@router.post("/outdoorsocket15a/v1/device/energyyear")
async def outdoor_socket(request: Request, data: Dict[str, Any]):
    """Handle outdoor socket requests."""
    is_valid, response = await validate_device_request(request, data)
    return response

# WiFi Switch 1.3 Routes
@router.get("/v1/device/{device_id}/detail")
@router.get("/v1/device/{device_id}/energy/month")
@router.get("/v1/device/{device_id}/energy/week")
@router.get("/v1/device/{device_id}/energy/year")
@router.put("/v1/wifi-switch-1.3/{device_id}/status/off")
@router.put("/v1/wifi-switch-1.3/{device_id}/status/on")
async def wifi_switch(request: Request, device_id: str = None):
    """Handle WiFi switch requests."""
    data = {"device_id": device_id} if device_id else {}
    is_valid, response = await validate_device_request(request, data)
    return response 
