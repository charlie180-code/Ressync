from flask import request, jsonify
from . import api
from ..models.general.company import Company
from ..models.general.user import User
from dotenv import load_dotenv
import os, requests

load_dotenv()

# geocoding api
@api.route("/autocomplete-address", methods=["GET"])
def autocomplete_address():
    query = request.args.get("query")
    key = os.environ.get('OPENCAGE_API_KEY')
    url = f"https://api.opencagedata.com/geocode/v1/json?q={query}&key={key}"
    
    response = requests.get(url)
    data = response.json()

    suggestions = []
    if data["results"]:
        for result in data["results"]:
            suggestions.append(result["formatted"])

    return jsonify(suggestions)

# freightos api
@api.route('/get-air-freight-rate/<int:company_id>', methods=['POST'])
def get_air_freight_rate(company_id):
    company = Company.query.get_or_404(company_id)
    data = request.get_json()

    request_url = "https://sandbox.freightos.com/api/v1/freightEstimates"

    request_headers = {
        "x-apikey": os.environ.get('FREIGHTOS_API_KEY'),
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    request_body = {
        "legs": [
            {
                "origin": data['DepartPort'],
                "destination": data['Arrival'],
                "date": data['Date']
            }
        ],
        "load": {
            "weight": {"value": data['Weight'], "unit": "kg"} if data['Weight'] else None,
            "volume": {"value": data['Volume'], "unit": "m3"} if data['Volume'] else None,
            "dimensions": {
                "length": {"value": data['Length'], "unit": "m"},
                "width": {"value": data['Width'], "unit": "m"},
                "height": {"value": data['Height'], "unit": "m"}
            } if data['Length'] and data['Width'] and data['Height'] else None
        }
    }

    request_body['load'] = {k: v for k, v in request_body['load'].items() if v is not None}

    response = requests.post(request_url, headers=request_headers, json=request_body)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to fetch rates', 'details': response.text}), response.status_code


# weather api
@api.route("/get-weather/realtime/<int:company_id>")
def get_weather():
    user_ip = request.remote_addr
    ipinfo_response = requests.get(f"https://ipinfo.io/{user_ip}/json")
    location_data = ipinfo_response.json()
    location = location_data.get('loc')

    if not location:
        return jsonify({'error': 'Could not determine location'}), 400

    tomorrow_api_key = os.environ.get('TOMORROW_API_KEY')
    weather_url = f"https://api.tomorrow.io/v4/weather/realtime?location=new york&apikey={tomorrow_api_key}"
    weather_response = requests.get(weather_url)
    weather_data = weather_response.json()

    return jsonify(weather_data)



@api.route("/company/check_duplicate_name", methods=['GET'])
def check_duplicate_company_name():
    title = request.args.get('title')

    if not title:
        return jsonify({"error": "Title is required"}), 400

    company = Company.query.filter_by(title=title).first()

    if company:
        return jsonify({"exists": True}), 200
    else:
        return jsonify({"exists": False}), 200


@api.route('/company/check_duplicate_email', methods=['GET'])
def check_duplicate_email():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'exists': True}), 200
    else:
        return jsonify({'exists': False}), 200



