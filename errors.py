


from pydantic import ValidationError


def register_error_handlers(app):

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return {
            "error": "Invalid data",
            "details": [
                {
                    "field": ".".join(str(part) for part in item["loc"]),
                    "message": item["msg"],
                }
                for item in error.errors()
            ]
        }, 422
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return {
            "error": "Resource not found"
        }, 404