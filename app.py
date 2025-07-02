from flask import Flask, request, jsonify
from flask_cors import CORS
from lambda_function import lambda_handler
import json

import logging

logging.basicConfig(
    level=logging.INFO,  # Set the minimum level to INFO
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

app = Flask(__name__)

# 👇 This enables all CORS, including preflight handling
CORS(app)

@app.route("/clip", methods=["POST", "OPTIONS"])
def clip():
    if request.method == "OPTIONS":
        return '', 204  # Optional, Flask-CORS will handle it

    body = request.get_json()
    result = lambda_handler(body)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
