# app/archive/archive.py
from .factory import create_app

cloudsquish = create_app(config_name='development')

if __name__ == "__main__":
    cloudsquish.run(
        debug=True, 
        port=5001
    )
