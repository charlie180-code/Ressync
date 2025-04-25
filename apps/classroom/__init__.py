from flask import Blueprint

classroom = Blueprint('classroom', __name__)

from . import controllers
