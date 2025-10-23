from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from datetime import timedelta

from beevs.response import APIResponse
from beevs.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app)
    Migrate(app, db)

    @app.route('/api/v1', strict_slashes=False)
    def home():
        return APIResponse.success(message="Welcome to BEEVS API v1")

    with app.app_context():
        import beevs.error_handlers
        import beevs.endpoints
    
    return app