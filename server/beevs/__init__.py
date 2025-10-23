from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from beevs.response import APIResponse
from beevs.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    SQLAlchemy(app)
    CORS(app)

    @app.route('/api/v1', strict_slashes=False)
    def home():
        return APIResponse.success(message="Welcome to BEEVS API v1")

    with app.app_context():
        import beevs.endpoints
    
    return app