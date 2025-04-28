# kavezok/utils.py

import os
import requests

def get_nearby_cafes(lat, lng, radius=2000):
    API_KEY = "AIzaSyAcygYCWGVfayOaUE9ruTUoi6F7XeyFxn0" # vagy a settings.py-ből importáld!
    endpoint = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": "cafe",
        "key": API_KEY,
        "language": "hu"
    }
    response = requests.get(endpoint, params=params)
    cafes = []
    if response.status_code == 200:
        data = response.json()
        for place in data.get("results", []):
            cafes.append({
                "nev": place.get("name"),
                "cim": place.get("vicinity", ""),
                "rating": place.get("rating", 0),
                "place_id": place.get("place_id"),
                "lat": place["geometry"]["location"]["lat"],
                "lng": place["geometry"]["location"]["lng"],
            })
    return cafes