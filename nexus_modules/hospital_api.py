from flask import Blueprint, request, jsonify
import requests

hospital_api = Blueprint("hospital_api", __name__)

@hospital_api.route("/hospitals/nearby")
def nearby_hospitals():

    lat = request.args.get("lat")
    lng = request.args.get("lng")

    if not lat or not lng:
        return jsonify({"hospitals": []})

    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:5000,{lat},{lng});
      way["amenity"="hospital"](around:5000,{lat},{lng});
      relation["amenity"="hospital"](around:5000,{lat},{lng});
    );
    out center;
    """

    url = "https://overpass-api.de/api/interpreter"

    try:
        response = requests.get(url, params={"data": query})
        data = response.json()

        hospitals = []

        for item in data.get("elements", []):
            tags = item.get("tags", {})

            hospitals.append({
                "name": tags.get("name", "Unknown Hospital"),
                "lat": item.get("lat", item.get("center", {}).get("lat")),
                "lng": item.get("lon", item.get("center", {}).get("lon")),
                "address": tags.get("addr:full", ""),
                "phone": tags.get("phone", "")
            })

        return jsonify({"hospitals": hospitals})

    except Exception as e:
        return jsonify({"error": str(e)})