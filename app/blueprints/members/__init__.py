# app/blueprints/members/__init__.py
from flask import Blueprint

members_bp = Blueprint('members_bp', __name__)

from . import routes