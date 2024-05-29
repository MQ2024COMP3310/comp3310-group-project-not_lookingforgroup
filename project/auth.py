# This python script is mostly based on week 8 workshop.
# Week 8 was extended using multiple online guides and public repositories for inspiration.
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import text
from .models import User # TODO USER MODEL NEEDED
from . import db

# Hashing stuff
from werkzeug.security import generate_password_hash, check_password_hash

# Handle for authentication logic so it can be decorated.
auth = Blueprint('auth', __name__)


# Route to the login page
# TODO steal week 10 login html
@auth.route('/login')
def login():
    return render_template('login.html')

# Read from the login form
# Check database
# TODO Check implementation
@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password and compare it with the stored password
    if not user or not (user.password == password):
        flash('Please check your login details and try again.')
        current_app.logger.warning("User login failed")
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

# Route to form for user signup
# TODO Check need signup html
@auth.route('/signup')
def signup():
    return render_template('signup.html')

# TODO Check implementation
@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    # TODO Fix SQL injection vulnerability
    sqlQuery = text('select * from user where email = "' + email +'"')
    user = db.session.execute(sqlQuery).all()
    if len(user) > 0: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')  # 'flash' function stores a message accessible in the template code.
        # TODO modify this logger
        current_app.logger.debug("User email already exists")
        # TODO redirect to login instead, the email is already registered
        return redirect(url_for('auth.signup'))

    
    # create a new user with the form data. TODO: Hash the password so the plaintext version isn't saved.
    # TODO password hashing. After that TODO Hashing clientside
    new_user = User(email=email, name=name, password=password)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # TODO Why are we redirecting? We should just log in the u
    return redirect(url_for('auth.login'))

# Route to logout a user, relies on the Flask blackbox.
@auth.route('/logout')
@login_required
def logout():
    logout_user();
    return redirect(url_for('main.homepage'))