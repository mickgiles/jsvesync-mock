"""Constants for VeSync mock server."""

# Mock account details
MOCK_ACCOUNT_ID = "mock_account_id"
MOCK_TOKEN = "mock_token"

# Valid credentials
VALID_EMAIL = "test@example.com"
VALID_PASSWORD = "cc03e747a6afbbcbf8be7668acfebee5"  # MD5 hash of "test123"

# Device UUIDs
DEVICE_UUIDS = {
    "fcb74eff-25ff-2bf7-5f4e-aaefd011b9f7": "LV-PUR131S",
    "dd6d6283-67d9-003b-f7ae-bea09683469c": "Core200S",
    "6cfef6ae-95bb-1fdc-eb6c-7523a4afa793": "Core200S",
    "7b97d1d1-6d78-1d5f-a9c1-12322a7c2f8d": "Core200S",
    "df6776ff-de7c-e083-08f6-fd286f5c6b86": "Core200S",
    "fb05cca6-4a91-1f62-f4ce-c9b21c2c68c3": "Classic300S"
}

# Error codes - matching actual VeSync API responses
ERROR_CODES = {
    "invalid_credentials": {
        "code": -11202022,
        "msg": "the account does not exist"
    },
    "missing_email": {
        "code": -11000022,
        "msg": "illegal argument"
    },
    "missing_password": {
        "code": -11000022,
        "msg": "illegal argument"
    },
    "invalid_token": {
        "code": -11300011,
        "msg": "invalid token"
    },
    "invalid_account_id": {
        "code": -11300012,
        "msg": "invalid account id"
    }
} 