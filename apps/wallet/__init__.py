from flask import Blueprint

wallet = Blueprint('wallet', __name__)
from . import controllers
