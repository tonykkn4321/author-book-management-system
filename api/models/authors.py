from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

from api.utils.database import db
from api.models.books import BookSchema

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    created = db.Column(db.DateTime, server_default=db.func.now())
    books = db.relationship('Book', backref='Author', cascade="all, delete-orphan")
    avatar = db.Column(db.String(512), nullable=True)  # ✅ Increased length

    def __init__(self, first_name, last_name, books=None):
        self.first_name = first_name
        self.last_name = last_name
        self.books = books if books else []

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class AuthorSchema(SQLAlchemyAutoSchema):
    class Meta(SQLAlchemyAutoSchema.Meta):
        model = Author
        sqla_session = db.session
        load_instance = True

    id = fields.Int(dump_only=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    created = fields.String(dump_only=True)
    books = fields.Nested(BookSchema, many=True, only=['title', 'year', 'id'])
    avatar = fields.String(dump_only=True)
