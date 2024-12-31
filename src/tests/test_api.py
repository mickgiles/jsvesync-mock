"""Test script for VeSync mock server API."""

import pytest
import yaml
import requests
from pathlib import Path
import logging
import hashlib
from typing import Dict, Any, Optional
from fastapi.testclient import TestClient
from src.main import app
from src.validators import get_supported_devices
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

class TestVeSyncAPI:
    """Test all VeSync API endpoints."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment before each test."""
        self.base_url = "http://localhost:8000"
        self.account_id = None
        self.token = None
        self.devices = []
        self.api_specs = {}
        self.test_results = {}
        transport = httpx.ASGITransport(app=app)
        self.client = httpx.AsyncClient(transport=transport, base_url=self.base_url)
        self.load_api_specs()
        yield
        self.print_test_summary()

    def load_api_specs(self):
        """Load all API specs from the api folder."""
        api_dir = Path("api")
        
        # Load main VeSync spec
        with open(api_dir / "vesync" / "VeSync.yaml") as f:
            self.api_specs["vesync"] = yaml.safe_load(f)
            logger.info("Loaded VeSync main spec")
        
        # Load device-specific specs
        for device_type in ["vesyncoutlet", "vesyncfan", "vesyncbulb", "vesyncswitch"]:
            device_dir = api_dir / device_type
            if device_dir.exists():
                for spec_file in device_dir.glob("*.yaml"):
                    with open(spec_file) as f:
                        spec = yaml.safe_load(f)
                        model = spec_file.stem
                        self.api_specs[model] = spec
                        logger.info(f"Loaded spec: {model}")

    def get_request_data(self, model: str, uuid: str, op_spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get request data for a device endpoint."""
        if "json_object" not in op_spec:
            return None
        
        request_data = {}
        for field, value in op_spec["json_object"].items():
            request_data[field] = value
            
            if field.lower() == "accountid":
                request_data[field] = self.account_id
            if field in ["token", "tk"]:
                request_data[field] = self.token
            if field in ["uuid", "cid", "deviceid"]:
                request_data[field] = uuid
        
        if "method" in op_spec["json_object"]:
            method = op_spec["json_object"]["method"]
            if method == "bypassV2":
                request_data = {
                    "method": "bypassV2",
                    "payload": {
                        "data": request_data,
                        "method": op_spec.get("method", ""),
                        "source": "APP"
                    }
                }
            elif method == "bypass":
                request_data = {
                    "method": "bypass",
                    "jsonCmd": request_data
                }
        
        return request_data

    def print_test_summary(self):
        """Print a summary of all test results."""
        total_success = 0
        total_failed = 0
        
        logger.info("\n" + "=" * 80)
        logger.info("TEST SUMMARY".center(80))
        logger.info("=" * 80)
        
        for device_type, endpoints in self.test_results.items():
            logger.info(f"\nDevice: {device_type}")
            logger.info("-" * 80)
            
            device_success = 0
            device_failed = 0
            
            for endpoint, result in endpoints.items():
                status = "✅ Success" if result["success"] else "❌ Failed"
                if result["success"]:
                    device_success += 1
                    total_success += 1
                else:
                    device_failed += 1
                    total_failed += 1
                logger.info(f"{status} - {endpoint}")
                if not result["success"] and result.get("error"):
                    logger.info(f"         Error: {result['error']}")
            
            logger.info(f"\nDevice Summary: {device_success} passed, {device_failed} failed")
        
        logger.info("\n" + "=" * 80)
        logger.info(f"TOTAL: {total_success + total_failed} tests".center(80))
        logger.info(f"✅ Passed: {total_success}".center(80))
        logger.info(f"❌ Failed: {total_failed}".center(80))
        logger.info("=" * 80 + "\n")

    def test_login(self):
        """Test login endpoint."""
        logger.info("Testing login endpoint...")
        
        login_spec = self.api_specs["vesync"]["login"]
        login_data = {}
        
        for field, value in login_spec["json_object"].items():
            login_data[field] = value
            
            if field.lower() == "accountid":
                login_data[field] = self.account_id
            if field in ["token", "tk"]:
                login_data[field] = self.token
        
        login_data.update({
            "email": "test@example.com",
            "password": hashlib.md5("test123".encode('utf-8')).hexdigest(),
            "traceId": "TRACE_ID"
        })
        
        headers = {}
        if "headers" in login_spec:
            for header_name, header_value in login_spec["headers"].items():
                headers[header_name] = header_value
                if header_name.lower() == "accountid":
                    headers[header_name] = "mock_account_id"
                if header_name in ["token", "tk"]:
                    headers[header_name] = "mock_token"
        
        response = requests.post(
            f"{self.base_url}/cloud/v1/user/login",
            headers=headers,
            json=login_data
        )
        
        assert response.status_code == 200, f"Login failed with status {response.status_code}: {response.text}"
        
        result = response.json()
        assert result["code"] == 0, f"Login failed: {result['msg']}"
        
        for key, value in result["result"].items():
            if key.lower() == "accountid":
                self.account_id = value
            if key in ["token", "tk"]:
                self.token = value
        
        logger.info(f"Login successful. AccountID: {self.account_id}")

    def test_login_invalid_credentials(self):
        """Test login endpoint with invalid credentials."""
        logger.info("Testing login with invalid credentials...")
        
        login_spec = self.api_specs["vesync"]["login"]
        
        # Test cases for invalid credentials
        test_cases = [
            {
                "email": "wrong@example.com",
                "password": hashlib.md5("test123".encode('utf-8')).hexdigest(),
                "expected_code": -11202022,
                "description": "Invalid email"
            },
            {
                "email": "test@example.com",
                "password": hashlib.md5("wrongpass".encode('utf-8')).hexdigest(),
                "expected_code": -11202022,
                "description": "Invalid password"
            },
            {
                "email": "",
                "password": hashlib.md5("test123".encode('utf-8')).hexdigest(),
                "expected_code": -11000022,
                "description": "Missing email"
            },
            {
                "email": "test@example.com",
                "password": "",
                "expected_code": -11000022,
                "description": "Missing password"
            }
        ]
        
        headers = {}
        if "headers" in login_spec:
            for header_name, header_value in login_spec["headers"].items():
                headers[header_name] = header_value
        
        for test_case in test_cases:
            logger.info(f"Testing {test_case['description']}...")
            
            login_data = {}
            for field, value in login_spec["json_object"].items():
                login_data[field] = value
            
            login_data.update({
                "email": test_case["email"],
                "password": test_case["password"],
                "traceId": "TRACE_ID"
            })
            
            response = requests.post(
                f"{self.base_url}/cloud/v1/user/login",
                headers=headers,
                json=login_data
            )
            
            assert response.status_code == 200, f"Request failed with status {response.status_code}: {response.text}"
            
            result = response.json()
            assert result["code"] == test_case["expected_code"], (
                f"Expected error code {test_case['expected_code']} for {test_case['description']}, "
                f"got {result['code']}: {result['msg']}"
            )
            
            logger.info(f"Successfully verified {test_case['description']}")

    def test_get_devices(self):
        """Test get devices endpoint."""
        logger.info("Testing get devices endpoint...")
        
        # Login first
        self.test_login()
        
        devices_spec = self.api_specs["vesync"]["get_devices"]
        headers = {}
        
        if "headers" in devices_spec:
            for header_name, header_value in devices_spec["headers"].items():
                headers[header_name] = header_value
                if header_name.lower() == "accountid":
                    headers[header_name] = self.account_id
                if header_name in ["token", "tk"]:
                    headers[header_name] = self.token
        
        data = {}
        if "json_object" in devices_spec:
            for field, value in devices_spec["json_object"].items():
                data[field] = value
                if field.lower() == "accountid":
                    data[field] = self.account_id
                if field in ["token", "tk"]:
                    data[field] = self.token
        
        response = requests.post(
            f"{self.base_url}/cloud/v1/deviceManaged/devices",
            headers=headers,
            json=data
        )
        
        assert response.status_code == 200, f"Failed to get devices: {response.text}"
        
        result = response.json()
        assert result["code"] == 0, f"Failed to get devices: {result['msg']}"
        
        self.devices = []
        for device in result["result"]["list"]:
            logger.info(f"Found device: {device['deviceName']} ({device['uuid']})")
            self.devices.append({
                "deviceType": device["deviceType"],
                "uuid": device["uuid"],
                "deviceName": device["deviceName"]
            })
        
        assert len(self.devices) > 0, "No devices found"

    def get_device_url(self, model: str, uuid: str, url_template: str) -> str:
        """Get device-specific URL."""
        url = url_template.replace("{uuid}", uuid)
        url = url.replace("{cid}", uuid)
        
        if model == "wifi-switch-1.3":
            url = url.replace("wifi-switch-1.3-CID", uuid)
        
        if not url.startswith("http"):
            url = f"{self.base_url}{url}"
        
        return url

    def test_device_endpoints(self):
        """Test all device endpoints."""
        logger.info("Testing device endpoints...")
        
        # Get devices first
        self.test_get_devices()
        
        for device in self.devices:
            model = device.get("deviceType")
            uuid = device.get("uuid")
            
            assert model and uuid, f"Invalid device data: {device}"
            
            logger.info(f"\nTesting endpoints for {model} ({uuid})")
            self.test_results[model] = {}
            
            if model not in self.api_specs:
                logger.warning(f"No spec found for {model}, skipping...")
                continue
            
            spec = self.api_specs[model]
            
            for op_name, op_spec in spec.items():
                if op_name in ["login", "get_devices"]:
                    continue
                    
                logger.info(f"Testing {op_name}...")
                
                method = op_spec.get("method", "").upper()
                assert method, "No method specified"
                
                assert "url" in op_spec, "No URL specified"
                url = self.get_device_url(model, uuid, op_spec["url"])
                logger.info(f"  URL: {url}")
                
                request_data = self.get_request_data(model, uuid, op_spec)
                logger.info(f"  Request data: {request_data}")
                
                headers = {}
                if "headers" in op_spec:
                    for header_name, header_value in op_spec["headers"].items():
                        headers[header_name] = header_value
                        if header_name.lower() == "accountid":
                            headers[header_name] = self.account_id
                        if header_name in ["token", "tk"]:
                            headers[header_name] = self.token
                
                logger.info(f"  Making {method} request to {url}")
                
                try:
                    if method == "GET":
                        response = requests.get(url, headers=headers)
                    elif method == "POST":
                        response = requests.post(url, headers=headers, json=request_data)
                    elif method == "PUT":
                        response = requests.put(url, headers=headers, json=request_data)
                    else:
                        raise ValueError(f"Unsupported method: {method}")
                    
                    assert response.status_code == 200, f"HTTP {response.status_code}: {response.text}"
                    
                    logger.info("  Success!")
                    self.test_results[model][op_name] = {
                        "success": True
                    }
                    
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"  Failed: {error_msg}")
                    self.test_results[model][op_name] = {
                        "success": False,
                        "error": error_msg
                    }
                    raise 

    @pytest.mark.asyncio
    async def test_wifi_switch_status(self):
        """Test wifi-switch-1.3 on/off status endpoints."""
        # Get a wifi switch device ID
        device_list = get_supported_devices()
        wifi_switch = next(d for d in device_list if d["deviceType"] == "wifi-switch-1.3")
        device_id = wifi_switch["cid"]
        
        # Test turning on
        response = await self.client.put(f"/v1/wifi-switch-1.3/{device_id}/status/on")
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["status"] == "ok"
        assert data["result"]["deviceStatus"] == "on"
        
        # Test turning off
        response = await self.client.put(f"/v1/wifi-switch-1.3/{device_id}/status/off")
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["status"] == "ok"
        assert data["result"]["deviceStatus"] == "off"
        
        # Test invalid status
        response = await self.client.put(f"/v1/wifi-switch-1.3/{device_id}/status/invalid")
        assert response.status_code >= 400 