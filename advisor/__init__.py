from flask import Blueprint

advisor = Blueprint('advisor', __name__)

from . import routes
