from flask import current_app as app
from beevs.response import APIResponse


@app.route('/api/v1/auth/login', methods=['POST'], strict_slashes=False)
def login():
    return APIResponse.success(message="WIP")