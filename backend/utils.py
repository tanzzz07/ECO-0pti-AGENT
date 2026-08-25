import json
import re

def sanitize_string(val, max_length=255):
    """
    Sanitizes string inputs by stripping whitespace, removing null bytes,
    and enforcing type safety and length limits.
    """
    if not isinstance(val, (str, int, float)):
        return ""
    s = str(val).replace("\x00", "").strip()
    return s[:max_length]

def validate_username(username):
    """
    Validates username format. Must be 3-100 characters containing only
    alphanumeric characters, underscores, and hyphens.
    """
    if not isinstance(username, str):
        return False
    return bool(re.match(r"^[a-zA-Z0-9_-]{3,100}$", username))

def validate_email(email):
    """
    Validates email format and max length (120 characters).
    """
    if not isinstance(email, str) or len(email) > 120:
        return False
    return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email))

def sanitize_numeric(val, min_val=0.0, max_val=1000000.0, default=0.0):
    """
    Ensures input is a valid numeric float within realistic bounds.
    """
    try:
        num = float(val)
        if num < min_val:
            return min_val
        if num > max_val:
            return max_val
        return num
    except (ValueError, TypeError):
        return default

def calculate_vehicle_emissions(data):
    # Example:
    km_per_day = sanitize_numeric(data.get("average_km_per_vehicle_per_day", 0))
    num_vehicles = sanitize_numeric(data.get("number_of_diesel_vehicles", 0))
    # Emission factor (approximate): 2.68 kg CO₂ per liter of diesel
    # Let's assume avg 15 km/l fuel efficiency
    emission = (num_vehicles * km_per_day / 15) * 2.68
    return round(emission, 2)

def robust_parse_suggestions(content, parser):
    if isinstance(content, list):
        return content
        
    if isinstance(content, dict):
        if "properties" in content and isinstance(content["properties"], dict) and "suggestions" in content["properties"]:
            return content["properties"]["suggestions"]
        if "suggestions" in content:
            return content["suggestions"]
        content = json.dumps(content)

    try:
        parsed = parser.parse(content)
        return getattr(parsed, "suggestions", [])
    except Exception as e:
        original_error = e

    try:
        match = re.search(r'"suggestions"\s*:\s*(\[[^\]]+\])', content)
        if match:
            return json.loads(match.group(1))
    except Exception:
        pass
        
    try:
        match = re.search(r'\[(.*?)\]', content, re.DOTALL)
        if match:
            array_str = match.group(0)
            try:
                return json.loads(array_str)
            except Exception:
                matches = re.findall(r'"([^"]+)"', array_str)
                if matches:
                    return matches
    except Exception:
        pass
        
    return ["Suggestion 1: Optimize usage.", "Suggestion 2: Upgrade equipment.", f"Error parsing: {str(original_error)}"]