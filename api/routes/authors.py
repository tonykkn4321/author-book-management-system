from flask import Blueprint
from flask import request
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.authors import Author, AuthorSchema
from api.utils.database import db

author_routes = Blueprint("author_routes", __name__)

@author_routes.route('/', methods=['POST'])

def create_author():
    try:
        data = request.get_json()
        author_schema = AuthorSchema()

        # Load and validate data
        author_data = author_schema.load(data)

        # Create Author instance
        author = Author(**author_data)
        db.session.add(author)
        db.session.commit()

        # Serialize result
        result = author_schema.dump(author)

        return response_with(resp.SUCCESS_201, value={"author": result})

    except Exception as e:
        print(f"Error creating author: {e}")
        return response_with(resp.INVALID_INPUT_422)

