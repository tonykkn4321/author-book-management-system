from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.utils.responses import response_with
from api.utils import responses as resp
from api.utils.database import db
from api.models.books import Book, BookSchema

book_routes = Blueprint("book_routes", __name__)

def get_request_data():
    if request.is_json:
        return request.get_json()
    else:
        return request.form

# Handle OPTIONS requests globally for this blueprint
@book_routes.route('/', methods=['OPTIONS'])
@book_routes.route('/<int:id>', methods=['OPTIONS'])
def handle_options(id=None):
    return '', 204

# POST book endpoint
@book_routes.route('/', methods=['POST'])
@jwt_required()
def create_book():
    """
    Create a new book

    ---
    tags:
      - Books
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
            - year
            - author_id
          properties:
            title:
              type: string
              example: "Pride and Prejudice"
            year:
              type: integer
              example: 1813
            author_id:
              type: integer
              example: 1
    responses:
      201:
        description: Book created successfully
        schema:
          type: object
          properties:
            book:
              type: object
      422:
        description: Invalid input
    """
    try:
        data = get_request_data()
        book_schema = BookSchema()
        book_data = book_schema.load(data)
        book = Book(**book_data)
        db.session.add(book)
        db.session.commit()
        result = book_schema.dump(book)
        return response_with(resp.SUCCESS_201, value={"book": result})
    except Exception as e:
        print(f"Error creating book: {e}")
        return response_with(resp.INVALID_INPUT_422)

# GET books endpoint
@book_routes.route('/', methods=['GET'])
def get_book_list():
    """
    Get all books

    ---
    tags:
      - Books
    summary: Retrieve a list of all books
    responses:
      200:
        description: A list of books
        schema:
          type: object
          properties:
            books:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  title:
                    type: string
                    example: "Emma"
                  year:
                    type: integer
                    example: 1815
                  author_id:
                    type: integer
                    example: 2
    """
    fetched = Book.query.all()
    book_schema = BookSchema(many=True, only=['id','title', 'year', 'author_id'])
    books = book_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={"books": books})


# GET route to fetch a specific book using its ID
@book_routes.route('/<int:id>/', methods=['GET'])
def get_book_detail(id):
    """
    Get book details by ID

    ---
    tags:
      - Books
    parameters:
      - in: path
        name: id
        required: true
        type: integer
        description: ID of the book to retrieve
    responses:
      200:
        description: Book details retrieved successfully
        schema:
          type: object
          properties:
            book:
              type: object
      404:
        description: Book not found
    """
    fetched = Book.query.get_or_404(id)
    book_schema = BookSchema()
    book = book_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={"book": book})


# PUT books endpoint
@book_routes.route('/<int:id>/', methods=['PUT'])
@jwt_required()
def update_book_detail(id):
    """
    Update full book record

    ---
    tags:
      - Books
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        required: true
        type: integer
        description: ID of the book to update
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
            - year
          properties:
            title:
              type: string
              example: "Sense and Sensibility"
            year:
              type: integer
              example: 1811
    responses:
      200:
        description: Book updated successfully
        schema:
          type: object
          properties:
            book:
              type: object
      404:
        description: Book not found
    """
    data = get_request_data()
    get_book = Book.query.get_or_404(id)
    get_book.title = data.get('title')
    get_book.year = data.get('year')
    db.session.add(get_book)
    db.session.commit()
    book_schema = BookSchema()
    book = book_schema.dump(get_book)
    return response_with(resp.SUCCESS_200, value={"book": book})

# PATCH books endpoint
@book_routes.route('/<int:id>/', methods=['PATCH'])
@jwt_required()
def modify_book_detail(id):
    """
    Modify partial book record

    ---
    tags:
      - Books
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        required: true
        type: integer
        description: ID of the book to modify
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              example: "Northanger Abbey"
            year:
              type: integer
              example: 1817
    responses:
      200:
        description: Book modified successfully
        schema:
          type: object
          properties:
            book:
              type: object
      404:
        description: Book not found
    """
    data = get_request_data()
    get_book = Book.query.get_or_404(id)
    if 'title' in data:
        get_book.title = data.get('title')
    if 'year' in data:
        get_book.year = data.get('year')
    db.session.add(get_book)
    db.session.commit()
    book_schema = BookSchema()
    book = book_schema.dump(get_book)
    return response_with(resp.SUCCESS_200, value={"book": book})

# DELETE books endpoint
@book_routes.route('/<int:id>/', methods=['DELETE'])
@jwt_required()
def delete_book(id):
    """
    Delete book by ID

    ---
    tags:
      - Books
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        required: true
        type: integer
        description: ID of the book to delete
    responses:
      204:
        description: Book deleted successfully
      404:
        description: Book not found
    """
    get_book = Book.query.get_or_404(id)
    db.session.delete(get_book)
    db.session.commit()
    return response_with(resp.SUCCESS_204)

