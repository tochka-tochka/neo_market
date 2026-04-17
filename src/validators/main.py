import json
from typing import Dict, Any
from django.core.exceptions import ValidationError

def validate_characteristics(characteristics: str):
    try:
        characteristics = json.loads(characteristics)
        for c in characteristics:
            if not isinstance(c["name"], str):
                raise ValidationError(f"Invalid value {c['name']}")
            if not isinstance(c["value"], str):
                raise ValidationError(f"Invalid value {c['value']}")
    except Exception as e:
        raise ValidationError(f"Invalid JSON data: {e}")