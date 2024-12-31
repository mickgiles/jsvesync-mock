#!/usr/bin/env python3
"""Test VeSync device APIs using YAML specifications."""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List
from pyvesync import VeSync

def load_yaml_spec(device_type: str) -> Dict[str, Any]:
    """Load YAML spec for a device type."""
    # Search for the YAML file in api/vesyncoutlet and api/vesyncfan directories
    search_dirs = ['api/vesyncoutlet', 'api/vesyncfan']
    for directory in search_dirs:
        yaml_path = Path(directory) / f"{device_type}.yaml"
        if yaml_path.exists():
            with open(yaml_path) as f:
                return yaml.safe_load(f)
    return None

def is_read_only_endpoint(endpoint_name: str, endpoint_spec: Dict[str, Any]) -> bool:
    """Determine if an endpoint is read-only."""
    # Only allow devicedetail endpoints
    return 'devicedetail' in endpoint_name.lower()

def test_device_api(device: Any, yaml_spec: Dict[str, Any]) -> None:
    """Test all read-only API endpoints for a device."""
    device_name = getattr(device, 'device_name', 'Unknown Device')
    device_type = getattr(device, 'device_type', 'Unknown Type')
    
    print(f"\n=== {device_name} ({device_type}) ===")
    
    # Get device details directly
    details = device.details
    if details:
        print(json.dumps(details, indent=2))

def main():
    """Main entry point."""
    # Get credentials from environment or command line
    username = os.environ.get('VESYNC_USERNAME') or (len(sys.argv) > 1 and sys.argv[1])
    password = os.environ.get('VESYNC_PASSWORD') or (len(sys.argv) > 2 and sys.argv[2])
    
    if not username or not password:
        print("Please provide VeSync credentials via environment variables "
              "(VESYNC_USERNAME, VESYNC_PASSWORD) or command line arguments")
        sys.exit(1)
    
    # Initialize VeSync client
    client = VeSync(
        username,
        password,
        time_zone="America/New_York",
        debug=False
    )
    
    # Login and update device list
    if not client.login():
        print("Failed to login to VeSync")
        sys.exit(1)
        
    client.update()
    
    # Combine all device collections
    all_devices = []
    for collection in ['outlets', 'switches', 'fans', 'bulbs', 'air_purifiers']:
        if hasattr(client, collection):
            all_devices.extend(getattr(client, collection))
    
    # Test each device
    for device in all_devices:
        device_type = getattr(device, 'device_type', None)
        if not device_type:
            continue
            
        yaml_spec = load_yaml_spec(device_type)
        if yaml_spec:
            test_device_api(device, yaml_spec)

if __name__ == '__main__':
    main() 