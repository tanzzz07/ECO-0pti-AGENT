def calculate_vehicle_emissions(data):
    # Example:
    km_per_day = data.get("average_km_per_vehicle_per_day", 0)
    num_vehicles = data.get("number_of_diesel_vehicles", 0)
    # Emission factor (approximate): 2.68 kg CO₂ per liter of diesel
    # Let's assume avg 15 km/l fuel efficiency
    emission = (num_vehicles * km_per_day / 15) * 2.68
    return round(emission, 2)

import json
import re

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