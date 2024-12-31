"""Shared response utilities for VeSync mock server."""

from typing import Dict, Any, Optional
import inspect

def get_error_response(msg: str, code: int = 1) -> Dict[str, Any]:
    """Create error response with line number information."""
    frame = inspect.currentframe()
    caller = frame.f_back if frame else None
    line_num = caller.f_lineno if caller else 0
    func_name = caller.f_code.co_name if caller else "unknown"
    return {
        "code": code,
        "msg": f"{msg} [in {func_name} at line: {line_num}]",
        "result": None
    }

def get_success_response(result: Dict[str, Any], device_type: Optional[str] = None) -> Dict[str, Any]:
    """Create success response with line number information.
    
    Args:
        result: The result dictionary to include in response
        device_type: Optional device type for response formatting
        
    Returns:
        Formatted success response with line number info
    """
    frame = inspect.currentframe()
    caller = frame.f_back if frame else None
    line_num = caller.f_lineno if caller else 0
    func_name = caller.f_code.co_name if caller else "unknown"
    
    response = {
        "code": 0,
        "msg": f"request success [in {func_name} at line: {line_num}]",
        "result": result
    }
    
    # Use format_device_response if device_type provided
    if device_type:
        return format_device_response(response, device_type)
    return response

def format_device_response(response: Dict[str, Any], device_type: str) -> Dict[str, Any]:
    """Format response based on device type.
    
    Args:
        response: The response dictionary to format
        device_type: The device type to determine formatting
        
    Returns:
        Formatted response dictionary
    """
    # Add line number info to success message
    frame = inspect.currentframe()
    caller = frame.f_back if frame else None
    line_num = caller.f_lineno if caller else 0
    func_name = caller.f_code.co_name if caller else "unknown"
    
    if response.get("msg") == "request success":
        response["msg"] = f"request success [in {func_name} at line: {line_num}]"
    
    # Air131 devices use flattened response format
    if device_type and "131" in device_type:
        # Move result fields to root level if they exist
        if "result" in response and isinstance(response["result"], dict):
            result = response.pop("result")
            # If result has nested result, flatten that too
            if "result" in result and isinstance(result["result"], dict):
                nested = result.pop("result")
                result.update(nested)
            response.update(result)
    return response 