from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from db import db
from new_models import Destination, User, Booking, Contact, EmailCampaign
import os

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/destinations', methods=['GET', 'POST'])
@login_required
@admin_required
def destinations():
    if request.method == 'POST':
        # Logic for adding destination
        pass
    all_destinations = Destination.query.all()
    return render_template('admin/destinations.html', destinations=all_destinations)

# Add more admin routes for bookings, contacts, etc.
