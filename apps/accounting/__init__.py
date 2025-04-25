from flask import Blueprint

accounting = Blueprint('accounting', __name__)
from . import controllers
