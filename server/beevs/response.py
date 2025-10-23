from flask import jsonify

class APIResponse:
    @staticmethod
    def success(message="Success", data=None, status_code=200):
        response = {
            "success": True,
            "message": message,
            "data": data
        }
        return jsonify(response), status_code

    @staticmethod
    def error(message, errors={}, status_code=400):
        response = {
            "success": False,
            "message": message,
            "errors": errors
        }
        return jsonify(response), status_code