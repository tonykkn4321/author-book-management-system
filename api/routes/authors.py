import os
import uuid
from flask import Blueprint, request, url_for, current_app, send_from_directory
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from api.utils.responses import response_with
from api.utils import responses as resp
from api.utils.database import db
from api.models.authors import Author, AuthorSchema

# Allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

# Blueprint setup
author_routes = Blueprint("author_routes", __name__)

# Helper to get request data
def get_request_data():
    return request.get_json() if request.is_json else request.form

# Serve uploaded avatar files
@author_routes.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# Handle OPTIONS requests globally
@author_routes.route('/', methods=['OPTIONS'])
@author_routes.route('/<int:id>', methods=['OPTIONS'])
def handle_options(id=None):
    return '', 204

# Create a new author
@author_routes.route('/', methods=['POST'])
@jwt_required()
def create_author(): 
    """
    Create a new author

    ---
    tags:
      - Authors
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: AuthorCreate
          required:
            - first_name
            - last_name
          properties:
            first_name:
              type: string
              example: "Jane"
            last_name:
              type: string
              example: "Austen"
    responses:
      201:
        description: Author created successfully
      422:
        description: Invalid input
    """
    try:
        data = get_request_data()
        author_schema = AuthorSchema()
        author = author_schema.load(data)
        db.session.add(author)
        db.session.commit()
        result = author_schema.dump(author)
        return response_with(resp.SUCCESS_201, value={"author": result})
    except Exception as e:
        print(f"Error creating author: {e}")
        return response_with(resp.INVALID_INPUT_422, message="Invalid input")


# Get all authors (basic info only)
@author_routes.route('/', methods=['GET'])
def get_author_list():
    """
    Get all authors

    ---
    tags:
      - Authors
    summary: Retrieve a list of all authors with basic information
    responses:
      200:
        description: A list of authors with ID, first name, last name, and avatar URL
        schema:
          type: object
          properties:
            authors:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  first_name:
                    type: string
                    example: "Jane"
                  last_name:
                    type: string
                    example: "Austen"
                  avatar:
                    type: string
                    example: "https://yourdomain.com/api/authors/uploads/avatar123.jpg"
    """
    fetched = Author.query.all()
    author_schema = AuthorSchema(many=True, only=['id', 'first_name', 'last_name', 'avatar', 'books'])
    authors = author_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={"authors": authors})


# Get author details by ID
@author_routes.route('/<int:author_id>/', methods=['GET'])
def get_author_detail(author_id):
    """
    Retrieve author details by ID

    ---
    tags:
      - Authors
    parameters:
      - in: path
        name: author_id
        required: true
        type: integer
        description: ID of the author to retrieve
    responses:
      200:
        description: Author details retrieved successfully
        schema:
          type: object
          properties:
            author:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                first_name:
                  type: string
                  example: "Jane"
                last_name:
                  type: string
                  example: "Austen"
                avatar:
                  type: string
                  example: "https://yourdomain.com/api/authors/uploads/avatar123.jpg"
      404:
        description: Author not found
    """
    fetched = Author.query.get_or_404(author_id)
    author_schema = AuthorSchema()
    author = author_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={"author": author})

# Update full author record (PUT) by ID
@author_routes.route('/<int:id>/', methods=['PUT'])
@jwt_required()
def update_author_detail(id):
    """
    Update full author record

    ---
    tags:
      - Authors
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        required: true
        type: integer
        description: ID of the author to update
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - first_name
            - last_name
          properties:
            first_name:
              type: string
              example: "Emily"
            last_name:
              type: string
              example: "Bronte"
    responses:
      200:
        description: Author updated successfully
        schema:
          type: object
          properties:
            author:
              type: object
      404:
        description: Author not found
    """
    data = get_request_data()
    get_author = Author.query.get_or_404(id)
    get_author.first_name = data.get('first_name')
    get_author.last_name = data.get('last_name')
    db.session.add(get_author)
    db.session.commit()
    author_schema = AuthorSchema()
    author = author_schema.dump(get_author)
    return response_with(resp.SUCCESS_200, value={"author": author})


# Modify partial author record (PATCH) by ID
@author_routes.route('/<int:id>/', methods=['PATCH'])
@jwt_required()
def modify_author_detail(id):
    """
    Modify partial author record

    ---
    tags:
      - Authors
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        required: true
        type: integer
        description: ID of the author to modify
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            first_name:
              type: string
              example: "Leo"
            last_name:
              type: string
              example: "Tolstoy"
    responses:
      200:
        description: Author modified successfully
        schema:
          type: object
          properties:
            author:
              type: object
      404:
        description: Author not found
    """
    data = get_request_data()
    get_author = Author.query.get(id)
    if not get_author:
        return response_with(resp.NOT_FOUND_404)
    if 'first_name' in data:
        get_author.first_name = data.get('first_name')
    if 'last_name' in data:
        get_author.last_name = data.get('last_name')
    db.session.add(get_author)
    db.session.commit()
    author_schema = AuthorSchema()
    author = author_schema.dump(get_author)
    return response_with(resp.SUCCESS_200, value={"author": author})

# Delete author by ID
@author_routes.route('/<int:id>/', methods=['DELETE'])
@jwt_required()
def delete_author(id):
    """
    Delete author by ID

    ---
    tags:
      - Authors
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        required: true
        type: integer
        description: ID of the author to delete
    responses:
      204:
        description: Author deleted successfully
      404:
        description: Author not found
    """
    get_author = Author.query.get_or_404(id)
    db.session.delete(get_author)
    db.session.commit()
    return response_with(resp.SUCCESS_204)


# Upload or update author avatar image
@author_routes.route('/avatar/<int:author_id>', methods=['POST'])
@jwt_required()
def upsert_author_avatar(author_id):

    """
    Upload or update author avatar

    ---
    tags:
      - Authors
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
    parameters:
      - in: path
        name: author_id
        required: true
        type: integer
        description: ID of the author whose avatar is being uploaded
      - in: formData
        name: avatar
        type: file
        required: true
        description: Avatar image file (png, jpg, jpeg)
    responses:
      200:
        description: Avatar uploaded and author updated successfully
        schema:
          type: object
          properties:
            author:
              type: object
      422:
        description: Invalid input or file type
      500:
        description: Upload folder not configured
    """

    try:
        # Check if the request contains a file
        if 'avatar' not in request.files:
            print("No 'avatar' field found in request.files")
            return response_with(resp.INVALID_INPUT_422, message="No file part in request")

        file = request.files['avatar']

        # Check if the file has a name
        if not file or file.filename.strip() == '':
            print("Empty filename received")
            return response_with(resp.INVALID_INPUT_422, message="No selected file")

        # Validate file extension
        if not allowed_file(file.filename):
            print(f"File type not allowed: {file.filename}")
            return response_with(resp.INVALID_INPUT_422, message="Invalid file type")

        # Generate a unique filename
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        upload_folder = current_app.config.get('UPLOAD_FOLDER')

        # Ensure the upload folder exists
        if not upload_folder:
            print("UPLOAD_FOLDER not configured")
            return response_with(resp.SERVER_ERROR_500, message="Upload folder not configured")

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # Save the file
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # Update the author's avatar URL
        get_author = Author.query.get_or_404(author_id)
        get_author.avatar = url_for('author_routes.uploaded_file', filename=filename, _external=True)
        db.session.add(get_author)
        db.session.commit()

        # Return updated author data
        author_schema = AuthorSchema()
        author = author_schema.dump(get_author)
        return response_with(resp.SUCCESS_200, value={"author": author})

    except Exception as e:
        import traceback
        print("Avatar upload error:", traceback.format_exc())
        return response_with(resp.INVALID_INPUT_422, message="Failed to upload avatar")

# Delete author avatar image
@author_routes.route('/avatar/<int:author_id>', methods=['DELETE'])
@jwt_required()
def delete_author_avatar(author_id):
    
    """
    Delete author avatar

    ---
    tags:
      - Authors
    security:
      - Bearer: []
    parameters:
      - in: path
        name: author_id
        required: true
        type: integer
        description: ID of the author whose avatar is being deleted
    responses:
      200:
        description: Avatar deleted and author updated successfully
        schema:
          type: object
          properties:
            author:
              type: object
      404:
        description: Avatar not found or author does not exist
    """
    # [function body unchanged]

    try:
        author = Author.query.get_or_404(author_id)

        # Check if avatar exists
        if not author.avatar:
            return response_with(resp.NOT_FOUND_404, message="No avatar to delete")

        # Extract filename from URL
        avatar_url = author.avatar
        filename = avatar_url.split('/')[-1]
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        file_path = os.path.join(upload_folder, filename)

        # Delete the file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted avatar file: {file_path}")
        else:
            print(f"Avatar file not found: {file_path}")

        # Remove avatar reference from DB
        author.avatar = None
        db.session.add(author)
        db.session.commit()

        author_schema = AuthorSchema()
        updated_author = author_schema.dump(author)
        return response_with(resp.SUCCESS_200, value={"author": updated_author})

    except Exception as e:
        import traceback
        print("Avatar deletion error:", traceback.format_exc())
        return response