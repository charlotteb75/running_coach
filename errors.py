


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
    
    @app.errorhandler(409)
    def handle_conflict(error):
        return {
            "error": "Request generates conflict with resource",
            "message": error.description
        }, 409
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return {
            "error": "Internal server error"
        }, 500