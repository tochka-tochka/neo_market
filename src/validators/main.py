from typing import Dict, Any, List
from django.core.exceptions import ValidationError

def validate_characteristics(characteristics: List[Dict[str, Any]]):
    try:
        for c in characteristics:
            if not isinstance(c.get("name"), str):
                raise ValidationError(f"Invalid value {c.get("name")}")
            if not isinstance(c.get("value"), str):
                raise ValidationError(f"Invalid value {c.get("value")}")
    except Exception as e:
        raise ValidationError(f"Invalid JSON data: {e}")