from flask import Blueprint

promote = Blueprint('promote', __name__)
from . import controllers
