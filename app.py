from flask import Flask, request, jsonify, Response
from src.processor import process_talent
import json
from dotenv import load_dotenv
load_dotenv(dotenv_path="./.env")
import os
from logger_utils import logger
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS



app = Flask(__name__)
CORS(app)

SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.yaml"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Talent Tagging API"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/talent", methods=["POST"])
def create_talent():
    data = request.files.get('file')        # Request to get talent's JSON file
    threshold = float(request.form.get('threshold', 0.85))

    if not data:
        logger.error(f"[ERROR] No file uploaded")
        return jsonify({"error": "No file uploaded"}), 400
    
    data_path = f"/tmp/{data.filename}"
    data.save(data_path)

    try:
        tags = process_talent(data_path, threshold)
        return Response(json.dumps({"tags": tags}, ensure_ascii=False), content_type="application/json")
    except FileNotFoundError:
        logger.error("[ERROR] File not found")
        return jsonify({"error": "Uploaded file not found"}), 400
    except ValueError as ve:
        logger.error(f"[ERROR] Threshold error: {ve}")
        return jsonify({"error": str(ve)}), 422
    except Exception as e:
        logger.exception(f"[ERROR] Unhandled exception in /talent: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8000)