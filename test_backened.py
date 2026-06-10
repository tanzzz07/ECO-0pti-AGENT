# from dotenv import load_dotenv
# import os
# import requests

# # Load environment variables
# load_dotenv()

# url = "http://127.0.0.1:5000/analyze"

# data = {
#     "business_type": "Retail",
#     "lighting_type": "LED",
#     "light_usage_hours_per_day": 12,
#     "number_of_ac_units": 3,
#     "ac_usage_hours_per_day": 8,
#     "monthly_electricity_bill": 15000,
#     "uses_diesel_generator": True,
#     "uses_lpg_or_propane": False,
#     "number_of_diesel_vehicles": 2,
#     "average_km_per_vehicle_per_day": 40,
#     "uses_solar_panels": True,
#     "uses_energy_efficient_devices": True
# }

# response = requests.post(url, json=data)

# print("Status Code:", response.status_code)
# print("Response Text:", response.text)
import requests
import os
from dotenv import load_dotenv

load_dotenv()

url = "http://127.0.0.1:5000/analyze"
data = {
    "business_type": "Retail",
    "lighting_type": "LED",
    "light_usage_hours_per_day": 12,
    "number_of_ac_units": 3,
    "ac_usage_hours_per_day": 8,
    "monthly_electricity_bill": 15000,
    "uses_diesel_generator": True,
    "uses_lpg_or_propane": False,
    "number_of_diesel_vehicles": 2,
    "average_km_per_vehicle_per_day": 40,
    "uses_solar_panels": False,
    "uses_energy_efficient_devices": True
}

try:
    response = requests.post(url, json=data)
    response.raise_for_status() # This will raise an HTTPError for bad responses
    
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
    if response and response.text:
        print("Response Text:", response.text)