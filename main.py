from flask import Flask
from flask import request, jsonify

app = Flask(__name__)


@app.route("/")
def main():
    return "<h1>Welcome to the Machine Learning Module</h1>"


@app.route("/question")
def invoke_question():
    query = request.args.get('query', 'Basic Question', type=str)
    payload = {"query": query, "answer": 'null'}
    return jsonify(payload)