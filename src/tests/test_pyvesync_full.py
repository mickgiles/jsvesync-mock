"""Test all device features using PyVeSync device classes."""

import pytest
from pyvesync import VeSync
import logging
import yaml
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any

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
        
    def emit(self, record):
        # Print any error messages immediately
        if record.name.startswith('pyvesync.') and 'error' in record.getMessage().lower():
            print(f"[{record.name}] {record.getMessage()}")
        
        # Capture all logs from pyvesync modules
        if record.name.startswith('pyvesync.'):
            log_entry = {
                'module': record.name,
                'level': record.levelname,
                'message': record.getMessage()
            }
            self.logs.append(log_entry)

    def get_errors(self):
        """Return all logs containing the word 'error'."""
        return [log for log in self.logs if 'error' in log['message'].lower()]

    def clear(self):
        """Clear all logs."""
        self.logs = []

class TestDeviceFeatures:
    """Test all device features using actual PyVeSync device classes."""
    
    @pytest.fixture(autouse=True)
    def setup(self, capsys):
        """Set up test environment before each test."""
        self.capsys = capsys
        
        # Set up PyVeSync log capture
        self.log_handler = PyVeSyncLogHandler()
        for logger_name in ['pyvesync.helpers', 'pyvesync.vesync', 'pyvesync.vesyncbasedevice', 
                            'pyvesync.vesyncfan','pyvesync.vesyncbulb', 
                            'pyvesync.vesyncoutlet','pyvesync.vesyncswitch']:
            logger = logging.getLogger(logger_name)
            logger.addHandler(self.log_handler)
            logger.setLevel(logging.DEBUG)
        
        self.client = VeSync(
            "test@example.com",
            "test123",
            time_zone="America/New_York",
            debug=True
        )
        
        # Attempt login and update
        login_success = self.client.login()
        if not login_success:
            print("\nLogin failed - check credentials")
        else:
            print("\nLogin successful")
            self.client.update()
        
        # Print any errors found during setup but continue
        error_logs = self.log_handler.get_errors()
        if error_logs:
            print("\n=== PyVeSync Setup Errors ===")
            for error in error_logs:
                print(f"[{error['module']}] {error['message']}")
            print("\nContinuing with test despite errors...")
        
        # Combine all device collections into devices list
        self.client.devices = []
        if hasattr(self.client, 'outlets'):
            self.client.devices.extend(self.client.outlets)
        if hasattr(self.client, 'switches'):
            self.client.devices.extend(self.client.switches)
        if hasattr(self.client, 'fans'):
            self.client.devices.extend(self.client.fans)
        if hasattr(self.client, 'bulbs'):
            self.client.devices.extend(self.client.bulbs)
        if hasattr(self.client, 'air_purifiers'):
            self.client.devices.extend(self.client.air_purifiers)
        if hasattr(self.client, 'humidifiers'):
            self.client.devices.extend(self.client.humidifiers)
        
        # Load all YAML specs
        self.device_specs = {}
        api_dir = Path("api")
        for device_type in ["vesyncfan", "vesyncbulb", "vesyncoutlet", "vesyncswitch"]:
            device_dir = api_dir / device_type
            if device_dir.exists():
                for spec_file in device_dir.glob("*.yaml"):
                    with open(spec_file) as f:
                        model = spec_file.stem
                        self.device_specs[model] = yaml.safe_load(f)
        
        # Initialize test summary
        self.test_summary = defaultdict(lambda: {
            "tested_features": set(), 
            "failed_features": set(),
            "pyvesync_errors": defaultdict(list)  # Track PyVeSync errors by feature
        })
        
        yield
        
        # Print test summary
        with self.capsys.disabled():
            print("\n=== Test Summary ===")
            
            # First print all errors found
            print("\n=== All Errors Found ===")
            has_errors = False
            for device_name, results in self.test_summary.items():
                if results["pyvesync_errors"]:
                    has_errors = True
                    print(f"\nDevice: {device_name}")
                    for method, errors in results["pyvesync_errors"].items():
                        print(f"\nMethod: {method}")
                        for error in errors:
                            print(f"[{error['module']}] {error['message']}")
            
            if not has_errors:
                print("No errors found!")
            
            # Then print the regular test summary
            print("\n=== Feature Summary ===")
            for device_name, results in self.test_summary.items():
                print(f"\nDevice: {device_name}")
                print("Tested features:")
                for feature in sorted(results["tested_features"]):
                    status = "✓" if feature not in results["failed_features"] else "✗"
                    print(f"  {status} {feature}")
                if results["failed_features"]:
                    print("Failed features:")
                    for feature in sorted(results["failed_features"]):
                        print(f"  ✗ {feature}")
        
        self.client = None

    def check_for_errors(self, device_name: str, method_name: str):
        """Check for PyVeSync errors and fail immediately if found."""
        error_logs = self.log_handler.get_errors()
        if error_logs:
            print(f"\n=== PyVeSync Errors Detected ===")
            print(f"Device: {device_name}")
            print(f"Method: {method_name}")
            print("\nError Details:")
            for error in error_logs:
                print(f"[{error['module']}] {error['message']}")
            
            # Clear logs
            self.log_handler.clear()
            
            # Fail immediately
            pytest.fail("PyVeSync errors detected - see above for details")

    def test_device_features(self):
        """Test all device features based on YAML specs."""
        for device in self.client.devices:
            device_type = device.device_type
            spec = self.get_device_spec(device_type)
            if not spec:
                logger.error(f"No YAML spec found for device type: {device_type}")
                continue

            device_name = f"{device.device_name} ({device_type})"
            device_summary = self.test_summary[device_name]
            
            # Clear logs before testing each device
            self.log_handler.clear()
            
            # Get all available methods from the YAML spec
            available_methods = list(spec.keys())
            
            # Test each method from the YAML spec
            for method_name in available_methods:
                if not hasattr(device, method_name):
                    logger.error(f"Method {method_name} not found on device {device_type}")
                    device_summary["failed_features"].add(method_name)
                    continue
                
                method = getattr(device, method_name)
                device_summary["tested_features"].add(method_name)
                
                # Clear logs before testing each method
                self.log_handler.clear()
                
                try:
                    # Handle special cases for method parameters
                    if method_name == "change_fan_speed":
                        for speed in range(1, 4):
                            method(speed)
                            self.check_for_errors(device_name, f"{method_name}({speed})")
                    
                    elif method_name == "set_brightness":
                        for brightness in [25, 50, 75, 100]:
                            method(brightness)
                            self.check_for_errors(device_name, f"{method_name}({brightness})")
                    
                    elif method_name == "set_humidity":
                        for humidity in [40, 50, 60, 70]:
                            method(humidity)
                            self.check_for_errors(device_name, f"{method_name}({humidity})")
                    
                    elif method_name == "set_color_temp":
                        for temp in [2700, 4000, 5500]:
                            method(temp)
                            self.check_for_errors(device_name, f"{method_name}({temp})")
                    
                    elif method_name == "set_hsv":
                        colors = [
                            (0, 100, 100),    # Red
                            (120, 100, 100),  # Green
                            (240, 100, 100),  # Blue
                        ]
                        for h, s, v in colors:
                            method(h, s, v)
                            self.check_for_errors(device_name, f"{method_name}({h},{s},{v})")
                    
                    elif method_name == "set_timer":
                        method(2)  # 2 hours
                        self.check_for_errors(device_name, f"{method_name}(2)")
                    
                    elif method_name == "set_mist_level":
                        max_level = getattr(device, 'mist_level_max', 3)
                        for level in range(1, max_level + 1):
                            method(level)
                            self.check_for_errors(device_name, f"{method_name}({level})")
                    
                    elif method_name == "set_warm_level":
                        max_level = getattr(device, 'warm_level_max', 3)
                        for level in range(1, max_level + 1):
                            method(level)
                            self.check_for_errors(device_name, f"{method_name}({level})")
                    
                    elif method_name == "set_drying_mode_enabled":
                        for state in [True, False]:
                            method(state)
                            self.check_for_errors(device_name, f"{method_name}({state})")
                    
                    elif method_name == "change_mode":
                        for mode in ["manual", "sleep", "auto"]:
                            method(mode)
                            self.check_for_errors(device_name, f"{method_name}({mode})")
                    
                    elif method_name in ["get_monthly_energy", "get_weekly_energy", "get_yearly_energy"]:
                        method()
                        self.check_for_errors(device_name, method_name)
                    
                    elif method_name == "rgb_color_set":
                        colors = [
                            (255, 0, 0),      # Red
                            (0, 255, 0),      # Green
                            (0, 0, 255),      # Blue
                        ]
                        for r, g, b in colors:
                            method(r, g, b)
                            self.check_for_errors(device_name, f"{method_name}({r},{g},{b})")
                    
                    elif method_name == "set_temperature":
                        for temp in [150, 200, 250, 300, 350, 400]:
                            method(temp)
                            self.check_for_errors(device_name, f"{method_name}({temp})")
                    
                    elif method_name == "set_cooking_time":
                        for minutes in [10, 20, 30, 45, 60]:
                            method(minutes)
                            self.check_for_errors(device_name, f"{method_name}({minutes})")
                    
                    elif method_name == "set_cooking_mode":
                        for mode in ["air_fry", "roast", "bake", "broil", "toast", "warm"]:
                            method(mode)
                            self.check_for_errors(device_name, f"{method_name}({mode})")
                    
                    else:
                        # For simple methods with no parameters
                        method()
                        self.check_for_errors(device_name, method_name)
                    
                except Exception as e:
                    logger.error(f"Error testing {method_name} on {device_type}: {e}")
                    device_summary["failed_features"].add(method_name)
                    # Also capture any PyVeSync errors that occurred during the exception
                    error_logs = [log for log in self.log_handler.logs 
                                if log['level'] in ('ERROR', 'WARNING')]
                    if error_logs:
                        device_summary["pyvesync_errors"][method_name].extend(error_logs)
                        print(f"\nPyVeSync errors detected during exception for {device_name} - {method_name}:")
                        for error in error_logs:
                            print(f"[{error['module']} - {error['level']}] {error['message']}")
                    raise
                    
            # Test device-specific properties
            if any(x in device_type for x in ['CS158-AF', 'CS358-AF', 'CS137-AF']):
                if hasattr(device, 'current_temperature'):
                    device.current_temperature
                    self.check_for_errors(device_name, "current_temperature")
                    device_summary["tested_features"].add("current_temperature")
                
                if hasattr(device, 'cooking_status'):
                    device.cooking_status
                    self.check_for_errors(device_name, "cooking_status")
                    device_summary["tested_features"].add("cooking_status")
                
                if hasattr(device, 'remaining_time'):
                    device.remaining_time
                    self.check_for_errors(device_name, "remaining_time")
                    device_summary["tested_features"].add("remaining_time")
            
            # Only test humidity for humidifiers
            if any(x in device_type for x in ['Classic300S', 'Classic200S', 'Dual200S', 'LV600S', 'OASISMIST', 'OASISMIST1000S', 'Superior6000S']):
                if hasattr(device, 'current_humidity'):
                    device.current_humidity
                    self.check_for_errors(device_name, "current_humidity")
                    device_summary["tested_features"].add("current_humidity")
                
                if hasattr(device, 'water_lacks'):
                    device.water_lacks
                    self.check_for_errors(device_name, "water_lacks")
                    device_summary["tested_features"].add("water_lacks")
            
            # Test outlet-specific properties
            if any(x in device_type for x in ['ESW', 'ESO']):
                if hasattr(device, 'voltage'):
                    device.voltage
                    self.check_for_errors(device_name, "voltage")
                    device_summary["tested_features"].add("voltage")
                
                if hasattr(device, 'power'):
                    device.power
                    self.check_for_errors(device_name, "power")
                    device_summary["tested_features"].add("power")
                
                # Test energy monitoring for outlets - only call if methods exist
                if hasattr(device, 'get_weekly_energy'):
                    device.get_weekly_energy()
                    self.check_for_errors(device_name, "get_weekly_energy")
                    device_summary["tested_features"].add("get_weekly_energy")
                if hasattr(device, 'get_monthly_energy'):
                    device.get_monthly_energy()
                    self.check_for_errors(device_name, "get_monthly_energy")
                    device_summary["tested_features"].add("get_monthly_energy")
                if hasattr(device, 'get_yearly_energy'):
                    device.get_yearly_energy()
                    self.check_for_errors(device_name, "get_yearly_energy")
                    device_summary["tested_features"].add("get_yearly_energy") 

    def get_device_spec(self, device_type: str) -> Dict[str, Any]:
        """Get YAML spec for a device type."""
        return self.device_specs.get(device_type, {}) 