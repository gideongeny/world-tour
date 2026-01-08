from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from new_models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        new_user = User(username=data.get('username'), email=data.get('email'), password_hash=generate_password_hash(data.get('password')))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return jsonify({'success': True})
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        user = User.query.filter_by(username=data.get('username')).first()
        if user and check_password_hash(user.password_hash, data.get('password')):
            login_user(user)
            return jsonify({'success': True})
        return jsonify({'error': 'Invalid credentials'}), 401
    return render_template('login.html')
