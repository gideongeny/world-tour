"""Affiliate blueprint initialization"""
from flask import Blueprint

affiliate_bp = Blueprint('affiliate', __name__, url_prefix='/api/affiliate')

from . import routes
