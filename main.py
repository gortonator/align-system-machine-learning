from flask import Flask, render_template
from flask import request, jsonify
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from queue import Queue

import getpass
import requests
import smtplib
import json
import threading


class EmailListener(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            if not self.queue.empty():
                question = self.queue.get()
                send_email(question)
                self.queue.task_done()


print "Loading configurations..."
with open('config.json') as json_data_file:
    cfg = json.load(json_data_file)

username = cfg['email']['username']
password = getpass.getpass(prompt='Enter your email password for: ' + username + ' ')
print "Initializing Email Listener..."
email_queue = Queue()
email_worker = EmailListener(email_queue)
email_worker.setDaemon(True)
email_worker.start()
print "Listener established!"
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
        email_queue.put(query)
        email_queue.join()
    answer = {"question": query, "answer": payload['result']['fulfillment']['speech']}
    return jsonify(answer)


def get_answer(question):
    key = cfg['dialogflow']['key']
    header = {'Authorization': 'Bearer ' + key}
    url = "https://api.dialogflow.com/v1/query?"
    url += "v=" + cfg['dialogflow']['id']
    url += "&sessionId=" + cfg['dialogflow']['session']
    url += "&lang=" + cfg['dialogflow']['lang']
    url += "&query=" + question
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

