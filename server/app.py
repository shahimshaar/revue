"""
GUIDE: This defines the entry point to the flask app.
"""
import config
import os

from datetime import date
from flask import Flask, jsonify, send_from_directory
from flask.json import JSONEncoder
from flask_cors import CORS

class CustomJSONEncoder(JSONEncoder):
    """Use ISO 8601 for dates"""

    def default(self, obj):  # noqa: E0202
        try:
            if isinstance(obj, date):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
app.config["SECRET_KEY"] = config.flask_secret_key
# GUIDE: Cross-Origin Resource Sharing is a mechanism used by servers to tell the browser which other servers the browser should trust for this site.
# https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
CORS(app)


# GUIDE: This is how we tell flask to respond to a request on a specific url
# This particular instance responds to /api/file/filename. The last segment, filename, is turned into a string and passed as an argument to the function
# The @ syntax is called a function decorator. @app.route() is a function that takes another function as an argument and returns a modified function
# This is an advanced python feature that can be a lot of fun to waste time with.
# Flask makes great use of function decorators to attach functions to server responses/behaviors
# https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.route

@app.route("/api/file/<string:filename>")
def images_get(filename):
    return send_from_directory(config.image_upload_folder, filename)


from views.authentication import *  # noqa
from views.posts import *  # noqa
from views.subvues import *  # noqa
from views.users import *  # noqa

import errors  # noqa


# GUIDE: here are functions to respond to various server errors. Note the use of decorators.
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({
        "error": "API endpoint not found"
    }), 404


@app.errorhandler(500)
@app.errorhandler(405)
def internal_server_error(e):
    return jsonify({
        "error": "Internal server error"
    }), 500


@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify({
        "error": "To large (max. 1 MB)"
    }), 413


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    app.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)