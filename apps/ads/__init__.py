from flask import Blueprint

advertise = Blueprint('advertise', __name__)

from . import controllers