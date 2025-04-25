from flask import Blueprint

reseller = Blueprint('reseller', __name__)

from . import controllers
