import os
from flask import Flask
from flask import jsonify
from api.utils.database import db

app = Flask(__name__)

if os.environ.get('WORK_ENV') == 'PROD':
    app_config = ProductionConfig
elif os.environ.get('WORK_ENV') == 'TEST':
    app_config = TestingConfig
else:
    app_config = DevelopmentConfig

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app

if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0", use_reloader=False)
