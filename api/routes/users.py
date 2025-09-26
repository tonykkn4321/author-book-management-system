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

    """
    Create a new user

    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: UserSignup
          required:
            - username
            - password
            - email
          properties:
            username:
              type: string
              description: Unique username of the user
              default: "Johndoe"
            password:
              type: string
              description: Password of the user
              default: "somethingstrong"
            email:
              type: string
              description: Email of the user
              default: "someemail@provider.com"
    responses:
      201:
        description: User successfully created
        schema:
          id: UserSignUpSchema
          properties:
            user:
              type: object
      422:
        description: Invalid input arguments
        schema:
          id: InvalidInput
          properties:
            error:
              type: string
    """

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
    """
    User Login

    ---
    tags:
      - Users
    summary: Authenticate user and return JWT token
    description: Allows a registered and verified user to log in using either email or username and receive a JWT access token.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: UserLogin
          required:
            - password
          properties:
            email:
              type: string
              description: Email of the user
              example: "someemail@provider.com"
            username:
              type: string
              description: Username of the user
              example: "Johndoe"
            password:
              type: string
              description: Password of the user
              example: "somethingstrong"
    responses:
      201:
        description: User successfully authenticated
        schema:
          id: LoginSuccess
          properties:
            message:
              type: string
              example: "Logged in as Johndoe"
            access_token:
              type: string
              description: JWT access token
      400:
        description: Email not verified
        schema:
          id: EmailNotVerified
          properties:
            error:
              type: string
              example: "Email not verified."
      401:
        description: Invalid password or expired token
        schema:
          id: Unauthorized
          properties:
            error:
              type: string
              example: "Invalid password."
      404:
        description: User not found
        schema:
          id: UserNotFound
          properties:
            error:
              type: string
              example: "User not found."
      422:
        description: Invalid input
        schema:
          id: InvalidInput
          properties:
            error:
              type: string
              example: "Email or username is required."
    """
 
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
                resp.SUCCESS_200,
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
    """
    Verify Email

    ---
    tags:
      - Users
    summary: Verify user's email using token
    description: Confirms the user's email address using a token sent via email.
    parameters:
      - in: path
        name: token
        required: true
        type: string
        description: Verification token sent to the user's email
    responses:
      200:
        description: Email successfully verified
        schema:
          id: EmailVerified
          properties:
            message:
              type: string
              example: "Email successfully verified."
      401:
        description: Invalid or expired token
        schema:
          id: InvalidToken
          properties:
            error:
              type: string
              example: "Invalid or expired verification link."
      404:
        description: User not found
        schema:
          id: UserNotFound
          properties:
            error:
              type: string
              example: "User not found."
      422:
        description: Email already verified
        schema:
          id: AlreadyVerified
          properties:
            error:
              type: string
              example: "Email already verified."
    """

    email = confirm_verification_token(token)
    if not email:
        logging.warning(f"Token verification failed or expired for token: {token}")
        return response_with(resp.UNAUTHORIZED_401, value={"error": "Invalid or expired verification link."})


    user = User.query.filter_by(email=email).first()
    if not user:
        logging.warning(f"No user found for verified email: {email}")
        return response_with(resp.SERVER_ERROR_404, value={"error": "User not found."})

    if user.isVerified:
        logging.info(f"Email already verified for user: {user.email}")
        return response_with(resp.INVALID_INPUT_422, value={"error": "Email already verified."})

    user.isVerified = True
    db.session.commit()
    logging.info(f"Email successfully verified for user: {user.email}")
    return response_with(resp.SUCCESS_200, value={"message": "Email successfully verified."})

