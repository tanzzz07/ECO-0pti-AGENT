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
    try:
        parsed = parser.parse(content)
        return getattr(parsed, "suggestions", [])
    except Exception as e:
        try:
            match = re.search(r'"suggestions"\s*:\s*(\[[^\]]+\])', content)
            if match:
                return json.loads(match.group(1))
        except Exception:
            pass
        raise e