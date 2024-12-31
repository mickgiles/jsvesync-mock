# Key Learnings

## Device Types and Classifications

### Device Categories
- Devices are split into distinct categories with different validation needs:
  1. **Outlets**: Power outlets and smart plugs
  2. **Switches**: In-wall switches
  3. **Bulbs**: Smart light bulbs
  4. **Fans**: Air purifiers and humidifiers (not yet refactored)

### Outlets vs Switches
- Despite having "switch" in its name, the `wifi-switch-1.3` is actually an outlet device, not a switch
- Outlet devices include:
  - ESW models
  - ESO models
  - wifi-switch-1.3
- True switch devices are only:
  - ESWL models (in-wall switches)

### Device Type Detection
- Device type can be determined by the model prefix:
  - `ESW*` = outlet
  - `ESO*` = outlet
  - `wifi-switch-1.3` = outlet
  - `ESWL*` = switch (in-wall)
  - `ESL*` = bulb
  - `XYD*` = bulb

### Validation Organization
- Each device category has its own validator module:
  - `outlet_validator.py`: Outlet-specific validation
  - `switch_validator.py`: Switch-specific validation
  - `bulb_validator.py`: Bulb-specific validation
- Main validator (`validators.py`) only contains routing logic to direct requests to the appropriate device-specific validator

### Common Gotchas
- Don't be misled by device names - always verify the actual device type
- The `wifi-switch-1.3` should be handled by outlet validators despite its name
- Keep device-specific validation logic in the appropriate validator module to maintain clean separation of concerns
- Bulbs have unique endpoints for brightness and color control that other devices don't use 