from flask import Flask, render_template
from flask import request, jsonify
import requests

app = Flask(__name__)


@app.route("/")
def main():
    return render_template('index.html')


@app.route("/api")
def invoke_question():
    query = request.args.get('query', 'Basic Question', type=str)
    return jsonify(get_answer(query))


def get_answer(question):
    key = "e63d08b802e841ecb87a8b3bc6c5976a"
    header = {'Authorization': 'Bearer ' + key}
    url = "https://api.dialogflow.com/v1/query?v=20150910&sessionId=12345&lang=en&query=" + question
    req = requests.get(url, headers=header)
    return req.json()



