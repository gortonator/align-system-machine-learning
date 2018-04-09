from flask import Flask, render_template
from flask import request, jsonify, make_response

import requests
import json
import statistics


print "Loading configurations..."
with open('config.json') as json_data_file:
    cfg = json.load(json_data_file)

print "Loading answer constants..."
statistics.answer_slot_config(True)
print "Load successful!"
application = Flask(__name__)


@application.route("/")
def main():
    return render_template('index.html')


@application.route("/api")
def invoke_question():
    query = request.args.get('query', 'Basic Question', type=str)
    payload = get_answer(query)
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


@application.route("/api/intents")
def get_intents():
    key = cfg['dialogflow']['dev_key']
    header = {'Authorization': 'Bearer ' + key,
              'content-type': 'application/json'}
    url = "https://api.dialogflow.com/v1/intents?"
    url += "v=" + cfg['dialogflow']['id']
    url += "&lang=" + cfg['dialogflow']['lang']
    req = requests.get(url, headers=header)
    res = req.json()
    res_list = []
    for entry in res:
        res_list.append({'id': entry['id'], "name": entry['name']})
    statistics.answer_slot_config()
    return jsonify(str(res_list))


@application.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print "REQUEST \n" + json.dumps(req, indent=4, sort_keys=True)

    text = req['result']['fulfillment'].get('speech')

    resolved_text = resolve(text)

    res = {'speech': resolved_text, 'displayText': resolved_text}

    return make_response(jsonify(res))


def resolve(answer):
    with open('answers.json') as json_file:
        stats = json.load(json_file)
    words = answer.split(" ")
    fulfilled_ans = answer
    for word in words:
        size = len(word)
        if word[0] == '#' and word[size - 1] == '#':
            constant = stats[word[1:size - 1]]['value']
            fulfilled_ans = fulfilled_ans.replace(word, constant)
    return fulfilled_ans


if __name__ == "__main__":
    application.run(host='0.0.0.0')
