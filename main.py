from flask import Flask, render_template
from flask import request, jsonify

app = Flask(__name__)


@app.route("/")
def main():
    return render_template('index.html')


@app.route("/question")
def invoke_question():
    query = request.args.get('query', 'Basic Question', type=str)
    payload = {"query": query, "answer": 'null'}
    return jsonify(payload)