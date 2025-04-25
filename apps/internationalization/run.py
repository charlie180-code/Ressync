# app/api/run.py
from .factory import create_app

app = create_app('development')

if __name__ == "__main__":
    app.run(debug=True)
