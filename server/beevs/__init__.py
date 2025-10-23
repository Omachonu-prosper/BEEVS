from flask import Flask
from beevs.response import APIResponse


def create_app():
    app = Flask(__name__)
    
    @app.route('/api/v1', strict_slashes=False)
    def home():
        return APIResponse.success(message="Welcome to BEEVS API v1")
    
    return app