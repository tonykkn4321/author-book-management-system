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