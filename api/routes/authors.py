from flask import Blueprint, request
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.authors import Author, AuthorSchema
from api.utils.database import db

author_routes = Blueprint("author_routes", __name__)

# POST authors endpoint 
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

# GET authors endpoint 
@author_routes.route('/', methods=['GET'])
def get_author_list():
    fetched = Author.query.all()
    author_schema = AuthorSchema(many=True, only=['first_name', 'last_name','id'])
    authors = author_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={"authors": authors})

# GET route to fetch a specific author using their ID 
@author_routes.route('/<int:author_id>', methods=['GET'])
def get_author_detail(author_id):
    fetched = Author.query.get_or_404(author_id)
    author_schema = AuthorSchema()
    author = author_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={"author": author})