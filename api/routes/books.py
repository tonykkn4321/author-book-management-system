from flask import Blueprint, request
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.books import Book, BookSchema
from api.utils.database import db

book_routes = Blueprint("book_routes", __name__)

#  POST book endpoint
@book_routes.route('/', methods=['POST'])
def create_book():
    try:

        book_schema = BookSchema()
        
        if request.is_json:
            # Handle raw JSON
            data = request.get_json()
            book_data = book_schema.load(data)

        else:
            # Handle form-data
            title = request.form.get('title')
            year = request.form.get('year')
            author_id = request.form.get('author_id')
            book_data = {
                'title': title,
                'year': year,
                'author_id': author_id
            }

        book = Book(**book_data)
        db.session.add(book)
        db.session.commit()

        result = book_schema.dump(book)
        return response_with(resp.SUCCESS_201, value={"book": result})

    except Exception as e:
        print(f"Error creating book: {e}")
        return response_with(resp.INVALID_INPUT_422)

#   GET books endpoint
@book_routes.route('/', methods=['GET'])
def get_book_list():
    fetched = Book.query.all()
    book_schema = BookSchema(many=True, only=['author_id','title', 'year', 'id'])
    books = book_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={"books": books})

#   PUT books endpoint
@book_routes.route('/<int:id>', methods=['PUT'])
def update_book_detail(id):
    data = request.get_json()
    get_book = Book.query.get_or_404(id)
    get_book.title = data['title']
    get_book.year = data['year']
    db.session.add(get_book)
    db.session.commit()
    book_schema = BookSchema()
    book = book_schema.dump(get_book)
    return response_with(resp.SUCCESS_200, value={"book": book})

#   PATCH books endpoint
@book_routes.route('/<int:id>', methods=['PATCH'])
def modify_book_detail(id):
    data = request.get_json()
    get_book = Book.query.get_or_404(id)
    if data.get('title'):
        get_book.title = data['title']
    if data.get('year'):
        get_book.year = data['year']
    db.session.add(get_book)
    db.session.commit()
    book_schema = BookSchema()
    book = book_schema.dump(get_book)
    return response_with(resp.SUCCESS_200, value={"book": book})

#   DELETE books endpoint
@book_routes.route('/<int:id>', methods=['DELETE'])
def delete_book(id):
    get_book = Book.query.get_or_404(id)
    db.session.delete(get_book)
    db.session.commit()
    return response_with(resp.SUCCESS_204)
