"""Pytest configuration file."""

import os
import pytest
import requests
import logging
from typing import Generator, Dict, Any
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Server configuration
SERVER_HOST = "localhost"
SERVER_PORT = 8000  # Use the mock server's default port
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"
HEALTH_CHECK_RETRIES = 10

class RequestTracker:
    """Track API requests and responses."""
    
    def __init__(self):
        """Initialize the tracker."""
        self.reset()
    
    def reset(self):
        """Reset tracking state."""
        self.last_request = None
        self.last_response = None
    
    def track_request(self, *args, **kwargs):
        """Track a request."""
        # Extract request details from PyVeSync's call_api arguments
        if len(args) >= 3:  # PyVeSync call_api(cls, api: str, json_object: dict, headers: dict = None)
            api = args[1]
            json_object = args[2]
            headers = args[3] if len(args) > 3 else {}
        else:
            api = kwargs.get("api", "")
            json_object = kwargs.get("json_object", {})
            headers = kwargs.get("headers", {})
        
        self.last_request = {
            "url": api,
            "method": "post",  # PyVeSync uses POST for everything
            "headers": headers,
            "json": json_object
        }
        logger.debug(f"Tracking API call: {self.last_request}")
    
    def track_response(self, response):
        """Track a response."""
        try:
            self.last_response = response.json() if response else None
            logger.debug(f"Tracking API response: {self.last_response}")
        except (AttributeError, ValueError):
            self.last_response = None
            logger.debug("No JSON response to track")
    
    def get_last_request(self):
        """Get the last tracked request."""
        return self.last_request
    
    def get_last_response(self):
        """Get the last tracked response."""
        return self.last_response

# Global tracker instance
tracker = RequestTracker()

def track_api_call(func):
    """Decorator to track API calls for validation."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Store request details
        tracker.track_request(*args, **kwargs)
        
        # Make the API call
        response = func(*args, **kwargs)
        
        # Store response details
        tracker.track_response(response)
        
        return response
    return wrapper

def patch_pyvesync(server_url: str):
    """Patch PyVeSync to use our mock server and track API calls."""
    import pyvesync.helpers as helpers
    
    logger.info(f"Patching PyVeSync to use server URL: {server_url}")
    # Override API base URL
    helpers.API_BASE_URL = server_url
    helpers.API_RATE_LIMIT = 0  # Disable rate limiting for tests
    
    # Store original method
    original_call_api = helpers.Helpers.call_api
    
    # Create new method with tracking
    @track_api_call
    def tracked_call_api(*args, **kwargs):
        return original_call_api(*args, **kwargs)
    
    # Replace the method
    helpers.Helpers.call_api = tracked_call_api
    logger.info("PyVeSync patched successfully")

def is_server_healthy() -> bool:
    """Check if the server is running and healthy."""
    try:
        logger.info(f"Checking server health at {SERVER_URL}/health")
        response = requests.get(f"{SERVER_URL}/health", timeout=1)
        healthy = response.status_code == 200
        logger.info(f"Server health check result: {'healthy' if healthy else 'unhealthy'}")
        return healthy
    except requests.RequestException as e:
        logger.warning(f"Health check failed: {str(e)}")
        return False

@pytest.fixture(scope="session")
def server_url() -> str:
    """Return the server URL for tests to use."""
    return SERVER_URL

@pytest.fixture
def request_tracker():
    """Fixture to access request/response tracking."""
    tracker.reset()  # Reset tracker state before each test
    return {"get_last_request": tracker.get_last_request, 
            "get_last_response": tracker.get_last_response}

@pytest.fixture(scope="session", autouse=True)
def server(server_url) -> Generator[None, None, None]:
    """Setup test environment and patch PyVeSync."""
    logger.info("Starting test setup")
    
    # Check if mock server is running
    for attempt in range(HEALTH_CHECK_RETRIES):
        logger.info(f"Health check attempt {attempt + 1}/{HEALTH_CHECK_RETRIES}")
        if is_server_healthy():
            logger.info("Mock server is healthy!")
            break
    else:
        raise RuntimeError("Mock server is not running or not healthy")
    
    # Patch PyVeSync to use our mock server
    patch_pyvesync(server_url)
    
    logger.info("Test setup complete")
    yield
    logger.info("Test cleanup complete") 