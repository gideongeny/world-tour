from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from new_models import User
import json

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle JSON (API) or Form (Traditional)
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
        else:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

        user = User.query.filter((User.username == username) | (User.email == email)).first()
        if user:
            if request.is_json:
                return jsonify({'error': 'User already exists'}), 400
            flash('Username or email already exists', 'error')
            return redirect(url_for('auth.register'))

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        
        if request.is_json:
            login_user(new_user)
            return jsonify({'success': True, 'user': {'username': new_user.username, 'email': new_user.email}})
            
        login_user(new_user)
        flash('Registration successful!', 'success')
        return redirect(url_for('home'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if request.is_json:
                return jsonify({'success': True, 'user': {'username': user.username, 'email': user.email}})
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        
        if request.is_json:
            return jsonify({'error': 'Invalid credentials'}), 401
        flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    if request.is_json:
        return jsonify({'success': True})
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@auth_bp.route('/api/user')
@login_required
def get_user():
    return jsonify({
        'username': current_user.username,
        'email': current_user.email,
        'id': current_user.id
    })
