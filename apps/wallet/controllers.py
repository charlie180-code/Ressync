import json
from flask import jsonify, request
from . import wallet

@wallet.route('/get-transport-companies', methods=['GET'])
def get_transport_companies():
    category_files = {
        'air': 'air.json',
        'sea': 'sea.json',
        'tram': 'tram.json',
        'road': 'road.json',
        'urban': 'urban.json'
    }

    all_companies = []
    
    for category, filename in category_files.items():
        try:
            with open(f"apps/static/data-objects/transport/{filename}") as f:
                companies = json.load(f)
                for company in companies:
                    company['category'] = category
                all_companies.extend(companies)
        except FileNotFoundError:
            return jsonify({'error': f'Category file {filename} not found'}), 404

    return jsonify(all_companies)
