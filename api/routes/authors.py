from flask import Blueprint, request
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.authors import Author, AuthorSchema
from api.utils.database import db

author_routes = Blueprint("author_routes", __name__)

@author_routes.route('/', methods=['POST'])

def create_author():
    try:

        author_schema = AuthorSchema()
        
        if request.is_json:
            # Handle raw JSON
            data = request.get_json()
            author_data = author_schema.load(data)

        else:
            # Handle form-data
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            author_data = {
                'first_name': first_name,
                'last_name': last_name,
                'books': []  # You can later populate this if form supports it
            }

        author = Author(**author_data)
        db.session.add(author)
        db.session.commit()

        result = author_schema.dump(author)
        return response_with(resp.SUCCESS_201, value={"author": result})

    except Exception as e:
        print(f"Error creating author: {e}")
        return response_with(resp.INVALID_INPUT_422)

