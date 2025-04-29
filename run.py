import os
import sys
from apps import create_app
from dotenv import load_dotenv

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    template_folder = os.path.join(base_path, 'templates')
    static_folder = os.path.join(base_path, 'static')
    env_file_path = os.path.join(base_path, '.env')
else:
    template_folder = os.path.abspath('apps/templates')
    static_folder = os.path.abspath('apps/static')
    env_file_path = os.path.abspath('.env')

load_dotenv(env_file_path)

app = create_app(
    development=True,
    template_folder=template_folder,
    static_folder=static_folder
)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000
    )