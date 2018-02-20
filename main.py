from flask import Flask, render_template
from flask import request, jsonify
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import getpass

username = raw_input('Enter your email username: ')
password = getpass.getpass(prompt='Enter your email password: ')
app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')


@app.route("/api")
def invoke_question():
    query = request.args.get('query', 'Basic Question', type=str)
    payload = get_answer(query)
    query_decision = payload['result']['action']
    if query_decision == "input.unknown":
        send_email(query)
    answer = {"question": query, "answer": payload['result']['fulfillment']['speech']}
    return jsonify(answer)


def get_answer(question):
    key = "e63d08b802e841ecb87a8b3bc6c5976a"
    header = {'Authorization': 'Bearer ' + key}
    url = "https://api.dialogflow.com/v1/query?v=20150910&sessionId=12345&lang=en&query=" + question
    req = requests.get(url, headers=header)
    return req.json()


def send_email(question):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(username, password)

    msg = MIMEMultipart()
    msg['Subject'] = "You have a new unanswered question!"
    msg['From'] = username
    msg['To'] = username
    text = "You have a question to answer: \n\n" + question
    msg.attach(MIMEText(text, 'plain'))
    s.sendmail(username, username, msg.as_string())
    s.quit()
