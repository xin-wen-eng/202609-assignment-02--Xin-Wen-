"""
CSYE 6225 - Assignment 2: CI/CD Deployment to AWS EC2

Simple Flask API server with a /healthcheck endpoint.

Do NOT modify this file. You will deploy it as-is to your EC2 instance.
"""

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    # Listens on all interfaces so it's reachable from outside the EC2 instance.
    app.run(host="0.0.0.0", port=80)
