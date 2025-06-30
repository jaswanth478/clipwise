from flask import Flask, request, jsonify
from flask_cors import CORS
from lambda_function import lambda_handler
import json

app = Flask(__name__)
CORS(app, origins="*", allow_headers="*", methods=["POST", "OPTIONS"])


@app.route("/clip", methods=["POST", "OPTIONS"])
def clip():
    if request.method == "OPTIONS":
        return '', 204

    body = request.get_json()
    result = lambda_handler(body)  # pass body directly
    return jsonify(result)



if __name__ == "__main__":
    app.run(debug=True, port=5000)
