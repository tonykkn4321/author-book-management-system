# main.py

import os, logging
from dotenv import load_dotenv
from flask import Flask, jsonify, Blueprint, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint

# Mnnitoring Packages:
import sentry_sdk

from api.utils.responses import response_with
import api.utils.responses as resp
from api.config.config import DevelopmentConfig, ProductionConfig, TestingConfig
from api.utils.database import db
from api.utils.email import mail
from api.models.authors import Author, AuthorSchema
from api.routes.authors import author_routes
from api.routes.books import book_routes
from api.routes.users import user_routes

load_dotenv()

# Determine config
if os.environ.get('RAILWAY_ENVIRONMENT_NAME') == 'production':
    app_config = ProductionConfig
elif os.environ.get('RAILWAY_ENVIRONMENT_NAME') == 'test':
    app_config = TestingConfig
else:
    app_config = DevelopmentConfig

def create_app(app_config):

    # Initialize Sentry
    sentry_sdk.init(
        dsn="https://1a2bad50c8e9301441ea1bb0099f6ee6@o4510117421514752.ingest.us.sentry.io/4510117450940416",
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
    )

    app = Flask(__name__)
    app.config.from_object(app_config)
    jwt = JWTManager(app)
    mail.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()  # This runs on every app start

    '''
    CORS(app, supports_credentials=True, origins=[
        "https://front-end-page-for-api-endpoint-test.netlify.app/",
        "http://localhost:8000"
    ])
    '''
    
    CORS(app, supports_credentials=True, origins="*")

    SWAGGER_URL = '/api/docs'

    app.register_blueprint(author_routes, url_prefix='/api/authors')
    app.register_blueprint(book_routes, url_prefix='/api/books')
    app.register_blueprint(user_routes, url_prefix='/api/users')
    swaggerui_blueprint = get_swaggerui_blueprint('/api/docs', '/api/spec', config={'app_name': "Flask Author Book Management System"})
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    @app.route('/api/<path:path>', methods=['OPTIONS'])
    def options_handler(path):
        response = jsonify({'message': 'CORS preflight'})
        response.status_code = 200
        return response

    @app.route('/avatar/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

    @app.after_request
    def add_header(response):
        origin = request.headers.get("Origin")
        if origin in [
            "http://localhost:8000",
            "https://front-end-page-for-api-endpoint-test.netlify.app"
        ]:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        return response

    @app.errorhandler(400)
    def bad_request(e):
        logging.error(e)
        return response_with(resp.BAD_REQUEST_400)

    @app.errorhandler(500)
    def server_error(e):
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)

    @app.errorhandler(404)
    def not_found(e):
        logging.error(e)
        return response_with(resp.SERVER_ERROR_404)
    
    @app.route("/api/spec")
    def spec():
        swag = swagger(app, prefix='/api')
        swag['info']['base'] = "http://localhost:5000"
        swag['info']['version'] = "1.0"
        swag['info']['title'] = "Flask Author Book Management System"
        return jsonify(swag)

    return app

# Create app using selected config
app = create_app(app_config)

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 8080)), host="0.0.0.0", use_reloader=False)

