from flask import Blueprint, request, url_for, render_template_string
from flask_jwt_extended import create_access_token
import logging

from api.utils.responses import response_with
from api.utils import responses as resp
from api.utils.database import db
from api.utils.token import generate_verification_token, confirm_verification_token
from api.utils.email import send_email
from api.models.users import User, UserSchema

user_routes = Blueprint("user_routes", __name__)

# POST user route to create a new user
@user_routes.route('/', methods=['POST'])
def create_user():
    try:
        data = request.get_json()

        # Validate required fields
        if not data or 'username' not in data or 'password' not in data or 'email' not in data:
            return response_with(resp.INVALID_INPUT_422, value={"error": "Username, email, and password are required."})

        # Check for existing user
        if User.find_by_email(data['email']) or User.find_by_username(data['username']):
            return response_with(resp.INVALID_INPUT_422, value={"error": "Email or username already exists."})

        # Hash the password
        data['password'] = User.generate_hash(data['password'])

        # Load and create user
        user_schema = UserSchema()
        user = user_schema.load(data)
        user.create()

        # Generate verification token and email
        token = generate_verification_token(data['email'])
        verification_email = url_for('user_routes.verify_email', token=token, _external=True)
        html = render_template_string(
            "<p>Welcome! Thanks for signing up. Please follow this link to activate your account:</p>"
            "<p><a href='{{ verification_email }}'>{{ verification_email }}</a></p><br><p>Thanks!</p>",
            verification_email=verification_email
        )
        subject = "Please Verify Your Email"
        send_email(user.email, subject, html)

        # Serialize and respond
        result = user_schema.dump(user)
        return response_with(resp.SUCCESS_201, value={"user": result})

    except Exception as e:
        logging.exception("Error creating user")
        return response_with(resp.INVALID_INPUT_422, value={"error": str(e)})

# Create a login route for the signed up users to login
@user_routes.route('/login', methods=['POST'])
def authenticate_user():
    try:
        data = request.get_json()

        if data.get('email'):
            current_user = User.find_by_email(data['email'])
        elif data.get('username'):
            current_user = User.find_by_username(data['username'])
        else:
            return response_with(resp.INVALID_INPUT_422, value={"error": "Email or username is required."})

        if not current_user:
            return response_with(resp.SERVER_ERROR_404, value={"error": "User not found."})

        if not current_user.isVerified:
            return response_with(resp.BAD_REQUEST_400, value={"error": "Email not verified."})

        if User.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=current_user.username)
            return response_with(
                resp.SUCCESS_201,
                value={
                    'message': f'Logged in as {current_user.username}',
                    'access_token': access_token
                }
            )
        else:
            return response_with(resp.UNAUTHORIZED_401, value={"error": "Invalid password."})

    except Exception as e:
        logging.exception("Login error")
        return response_with(resp.INVALID_INPUT_422, value={"error": str(e)})

# GET endpoint to handle email validation
@user_routes.route('/confirm/<token>', methods=['GET'])
def verify_email(token):
    try:
        email = confirm_verification_token(token)
    except Exception as e:
        logging.warning(f"Token verification failed: {e}")
        return response_with(resp.SERVER_ERROR_401, value={"error": "Invalid or expired token."})

    user = User.query.filter_by(email=email).first_or_404()

    if user.isVerified:
        return response_with(resp.INVALID_INPUT_422, value={"error": "Email already verified."})
    else:
        user.isVerified = True
        db.session.add(user)
        db.session.commit()
        return response