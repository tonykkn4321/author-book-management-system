from flask import Blueprint, request
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.authors import Author, AuthorSchema
from api.utils.database import db

author_routes = Blueprint("author_routes", __name__)

def get_request_data():
    if request.is_json:
        return request.get_json()
    else:
        return request.form

# Handle OPTIONS requests globally for this blueprint
@author_routes.route('/', methods=['OPTIONS'])
@author_routes.route('/<int:id>', methods=['OPTIONS'])
def handle_options(id=None):
    return '', 204

# POST authors endpoint 
@author_routes.route('/', methods=['POST'])
def create_author():
    try:
        data = get_request_data()
        author_schema = AuthorSchema()
        author_data = author_schema.load(data)
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

# PUT endpoint for the author route to update the author object
@author_routes.route('/<int:id>', methods=['PUT'])
def update_author_detail(id):
    data = get_request_data()
    get_author = Author.query.get_or_404(id)
    get_author.first_name = data.get('first_name')
    get_author.last_name = data.get('last_name')
    db.session.add(get_author)
    db.session.commit()
    author_schema = AuthorSchema()
    author = author_schema.dump(get_author)
    return response_with(resp.SUCCESS_200, value={"author": author})

# PATCH endpoint to update only a part of the author object
@author_routes.route('/<int:id>', methods=['PATCH'])
def modify_author_detail(id):
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

# DELETE author endpoint which will take the author ID from the request parameter and delete the author object
@author_routes.route('/<int:id>', methods=['DELETE'])
def delete_author(id):
    get_author = Author.query.get_or_404(id)
    db.session.delete(get_author)
    db.session.commit()
    return response_with(resp.SUCCESS_204)
