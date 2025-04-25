# app/archive/run.py
from .factory import create_app

app = create_app('development')

if __name__ == "__main__":
    app.run(debug=True, port=5001)
