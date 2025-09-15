from flask import Blueprint, request
from flask_jwt_extended import create_access_token
import logging

from api.utils.responses import response_with
from api.utils import responses as resp
from api.utils.database import db
from api.models.users import User, UserSchema

user_routes = Blueprint("user_routes", __name__)

# POST user route to create a new user
@user_routes.route('/', methods=['POST'])
def create_user():
    try:
        data = request.get_json()

        # Validate required fields
        if not data or 'username' not in data or 'password' not in data:
            return response_with(resp.INVALID_INPUT_422, value={"error": "Username and password are required."})

        # Hash the password
        data['password'] = User.generate_hash(data['password'])

        # Load and create user
        user_schema = UserSchema()
        user = user_schema.load(data)
        user.create()

        # Serialize response
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
        current_user = User.find_by_username(data['username'])
        if current_user and User.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=data['username'])
            return response_with(
                resp.SUCCESS_201,
                value={
                    'message': f'Logged in as {current_user.username}',
                    'access_token': access_token
                }
            )
        else:
            return response_with(resp.UNAUTHORIZED_401)
    except Exception as e:
        logging.exception("Error authenticating user")
        return response_with(resp.INVALID_INPUT_422)
