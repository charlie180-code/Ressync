from flask import Blueprint

insights = Blueprint('insights', __name__)

from . import controllers
