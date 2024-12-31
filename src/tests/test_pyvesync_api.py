"""Integration tests using the PyVeSync client library."""

import pytest
from pyvesync import VeSync
import logging
import yaml
from pyvesync.helpers import Helpers as helper
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

# Create a handler that captures PyVeSync module logs
class PyVeSyncLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []
        self.ignore_errors = False
        
    def emit(self, record):
        # Only capture logs from pyvesync modules
        if record.name.startswith('pyvesync.'):
            self.logs.append({
                'module': record.name,
                'level': record.levelname,
                'message': record.getMessage()
            })
            # Fail immediately on PyVeSync errors unless ignored
            if record.levelname in ('ERROR', 'WARNING') and not self.ignore_errors:
                print(f"\nPyVeSync error detected: [{record.name} - {record.levelname}] {record.getMessage()}")
                pytest.fail("PyVeSync error detected")

# Test configuration
TEST_EMAIL = "test@example.com"  # Match documented test credentials
TEST_PASSWORD = "test123"
TEST_TIME_ZONE = "America/New_York"

class TestPyVeSyncClient:
    """Test class for PyVeSync client integration."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment before each test."""
        self.api_specs = {}
        self.test_results = {}
        
        # Set up PyVeSync log capture
        self.log_handler = PyVeSyncLogHandler()
        for logger_name in ['pyvesync.helpers', 'pyvesync.vesync', 'pyvesync.vesyncbasedevice', 
                            'pyvesync.vesyncfan','pyvesync.vesyncbulb', 
                            'pyvesync.vesyncoutlet','pyvesync.vesyncswitch']:
            logger = logging.getLogger(logger_name)
            logger.addHandler(self.log_handler)
            logger.setLevel(logging.DEBUG)
        
        self.load_api_specs()
        yield
        self.print_test_summary()

    def load_api_specs(self):
        """Load all API specifications from YAML files."""
        # Load core VeSync specs
        with open('api/vesync/VeSync.yaml', 'r') as f:
            vesync_spec = yaml.safe_load(f)
            self.api_specs.update(vesync_spec)

        # Load device-specific specs
        device_types = {
            'outlets': 'vesyncoutlet',
            'switches': 'vesyncswitch',
            'fans': 'vesyncfan',
            'bulbs': 'vesyncbulb'
        }
        for device_type, dir_name in device_types.items():
            device_dir = f'api/{dir_name}'
            if os.path.exists(device_dir):
                for spec_file in os.listdir(device_dir):
                    if spec_file.endswith('.yaml'):
                        device_type_key = spec_file[:-5]  # Remove .yaml extension
                        with open(os.path.join(device_dir, spec_file), 'r') as f:
                            device_spec = yaml.safe_load(f)
                            self.api_specs[device_type_key] = device_spec
                            logger.info(f"Loaded spec for device type: {device_type_key}")

    def check_for_errors(self, operation: str, ignore_errors: bool = False):
        """Check for PyVeSync errors and fail immediately if found.
        
        Args:
            operation: The operation being tested
            ignore_errors: If True, don't fail on errors (for expected error cases)
        """
        error_logs = [log for log in self.log_handler.logs 
                     if log['level'] in ('ERROR', 'WARNING')]
        if error_logs and not ignore_errors:
            print(f"\nPyVeSync errors detected for {operation}:")
            for error in error_logs:
                print(f"[{error['module']} - {error['level']}] {error['message']}")
            pytest.fail("PyVeSync errors detected")
        return error_logs

    def test_invalid_credentials(self):
        """Test login with invalid credentials."""
        logger.info("Testing invalid credentials...")

        # Test cases for invalid credentials
        test_cases = [
            {
                "email": "wrong@example.com",
                "password": "test123",
                "description": "Invalid email"
            },
            {
                "email": "test@example.com",
                "password": "wrongpass",
                "description": "Invalid password"
            },
            {
                "email": "",
                "password": "test123",
                "description": "Missing email"
            },
            {
                "email": "test@example.com",
                "password": "",
                "description": "Missing password"
            }
        ]

        # Enable error ignoring for this test
        self.log_handler.ignore_errors = True

        for test_case in test_cases:
            logger.info(f"Testing {test_case['description']}...")
            
            # Clear previous logs
            self.log_handler.logs.clear()
            
            # Create client with test credentials
            client = VeSync(
                test_case["email"],
                test_case["password"],
                time_zone=TEST_TIME_ZONE,
                debug=True
            )
            
            # Attempt login
            login_result = client.login()
            
            # Login should fail
            assert not login_result, (
                f"Login should have failed for {test_case['description']}, "
                f"but succeeded with email={test_case['email']}, password={test_case['password']}"
            )
            
            # Verify we got error logs as expected
            error_logs = [log for log in self.log_handler.logs if log['level'] in ('ERROR', 'WARNING')]
            assert error_logs, f"Expected error logs for {test_case['description']}, but got none"
            
            logger.info(f"Successfully verified {test_case['description']}")
            self.record_result(f"login.{test_case['description']}", True, error_logs)

        # Disable error ignoring after test
        self.log_handler.ignore_errors = False

    def test_api_operations(self):
        """Test each API operation from the specs against stored devices."""
        logger.info("Testing API operations from specs...")
        
        # Initialize VeSync client
        client = VeSync(TEST_EMAIL, TEST_PASSWORD)
        
        # Clear previous logs
        self.log_handler.logs.clear()
        
        # Login to get token and account ID
        if not client.login():
            error_logs = self.check_for_errors('login')
            self.record_result('login', False, error_logs)
            return
        
        # Get devices
        if not client.get_devices():
            error_logs = self.check_for_errors('get_devices')
            self.record_result('get_devices', False, error_logs)
            return
        
        # Test each operation in the API specs
        for device_type in ['outlets', 'switches', 'fans', 'bulbs']:
            device_list = getattr(client, device_type)
            logger.info(f"\nTesting {device_type} devices ({len(device_list)} found)")
            for device in device_list:
                if device.device_type in self.api_specs:
                    logger.info(f"\nTesting operations for {device_type} device: {device.device_type}")
                    spec = self.api_specs[device.device_type]
                    operations = spec
                    logger.info(f"Found {len(operations)} operations in spec")
                    
                    for op_name, op_spec in operations.items():
                        logger.info(f"Testing operation: {op_name}")
                        endpoint = op_spec.get('url', '')  # Use url field from YAML
                        method = op_spec.get('method', 'post').lower()
                        logger.info(f"Making request to {endpoint}")
                        
                        # Clear previous logs
                        self.log_handler.logs.clear()
                        
                        try:
                            # Prepare request body and headers
                            headers = op_spec.get('headers', {})
                            json_object = op_spec.get('json_object', {})
                            
                            # Add auth headers
                            headers.update({
                                'accountId': client.account_id,
                                'tk': client.token
                            })
                            
                            # Add device identifiers to json
                            json_object.update({
                                'uuid': device.uuid,
                                'cid': device.cid,
                                'configModule': device.config_module,
                                'deviceRegion': device.device_region or 'US'
                            })
                            
                            # Make API call
                            response, status_code = helper.call_api(
                                endpoint,
                                method,
                                json_object=json_object,
                                headers=headers
                            )
                            
                            operation_key = f"{device_type}.{device.device_type}.{op_name}"
                            
                            # Check for API error logs
                            error_logs = self.check_for_errors(operation_key)
                            
                            # Record test result
                            if status_code == 200 and response is not None:
                                self.record_result(operation_key, True, error_logs)
                            else:
                                self.record_result(operation_key, False, error_logs)
                                pytest.fail(f"Operation failed: {operation_key}")
                                
                        except Exception as e:
                            logger.error(f"Error testing {device_type} operation {op_name}: {str(e)}")
                            operation_key = f"{device_type}.{device.device_type}.{op_name}"
                            error_logs = self.check_for_errors(operation_key)
                            self.record_result(operation_key, False, error_logs)
                            raise
                else:
                    logger.warning(f"No spec found for device type: {device.device_type}")

    def record_result(self, operation: str, success: bool, error_logs: list = None):
        """Record the result of a test operation."""
        if operation not in self.test_results:
            self.test_results[operation] = {
                'success': success,
                'pyvesync_errors': error_logs or []
            }

    def print_test_summary(self):
        """Print a summary of all test results."""
        total_tests = len(self.test_results)
        if total_tests == 0:
            return
            
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        failed_tests = total_tests - passed_tests

        print("\n" + "=" * 100)
        print(" " * 40 + "PyVeSync Mock Test Results\n")
        print("=" * 100 + "\n")

        # Print operation results
        print("Operations:")
        print(f"  Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"  Failed: {failed_tests}/{total_tests} ({failed_tests/total_tests*100:.1f}%)")
        
        # Print failures and PyVeSync errors
        for op, result in self.test_results.items():
            if not result['success'] or result['pyvesync_errors']:
                if not result['success']:
                    print(f"\n  Failed Operation: {op}")
                if result['pyvesync_errors']:
                    print("  PyVeSync Errors:")
                    for error in result['pyvesync_errors']:
                        print(f"    [{error['module']} - {error['level']}] {error['message']}")

        # Print overall summary
        print("\n" + "-" * 100)
        print(" " * 45 + "Overall Results:\n")
        print(" " * 45 + f"Total Tests: {total_tests}")
        print(" " * 45 + f"Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(" " * 45 + f"Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        print("-" * 100 + "\n")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 