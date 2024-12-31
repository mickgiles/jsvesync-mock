"""Test to get and display all device statuses using PyVeSync."""

import pytest
from pyvesync import VeSync
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

class TestDeviceStatus:
    """Test class for getting all device statuses."""
    
    @pytest.fixture(autouse=True)
    def setup(self, capsys):
        """Set up test environment before each test."""
        self.capsys = capsys
        
        # Initialize VeSync client
        self.client = VeSync(
            "test@example.com",
            "test123",
            time_zone="America/New_York",
            debug=True
        )
        
        # Attempt login and update
        login_success = self.client.login()
        if not login_success:
            logger.error("Login failed - check credentials")
            pytest.fail("Login failed")
        else:
            logger.info("Login successful")
            self.client.update()
        
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
        
        yield
        self.client = None

    def test_get_all_device_status(self):
        """Get and display status for all devices."""
        print("\nGetting status for all devices...")
        print(f"\nFound {len(self.client.devices)} devices")
        
        for device in self.client.devices:
            try:
                print("\n" + "="*80)
                print(device.displayJSON())
                print("="*80)
            except Exception as e:
                print(f"\nError getting details for {device.device_name}: {str(e)}")
                continue 