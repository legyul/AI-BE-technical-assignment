from flask import Flask, request, jsonify, Response
from src.processor import process_talent
import json
from dotenv import load_dotenv
load_dotenv(dotenv_path="./.env")
import os
from logger_utils import logger



app = Flask(__name__)

@app.route("/api/talent", methods=["POST"])
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
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8000)