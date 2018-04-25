"""
    The main web hook application which serves as an answer resolver for the DialogFlow chatbot
    Also contains a standalone shell and debugging mechanics for intent analysis and development
    AUTHOR: Nicholas Carugati
"""
import json
import statistics
import requests


from flask import Flask, render_template
from flask import request, jsonify, make_response

print "Loading configurations..."
with open('config.json') as json_data_file:
    CFG = json.load(json_data_file)

print "Loading answer constants..."
statistics.answer_slot_config(True)
print "Load successful!"
APPLICATION = Flask(__name__)


@APPLICATION.route("/")
def main():
    """
        The main route which provides a visual shell for the bot.
        RETURNS: The web view for the chat bot standalone shell
    """
    return render_template('index.html')


@APPLICATION.route("/api")
def invoke_question():
    """
        The endpoint which asks a question for the standalone shell
        RETURNS: The answer that was send from DialogFlow
    """

    query = request.args.get('query', 'Basic Question', type=str)
    payload = get_answer(query)
    answer = {"question": query, "answer": payload['result']['fulfillment']['speech']}
    return jsonify(answer)


def get_answer(question):
    """
        The function which resolves an answer via DialogFlow.
        question -- The question being asked
        RETURNS: The JSON answer composition from the bot
    """

    key = CFG['dialogflow']['key']
    header = {'Authorization': 'Bearer ' + key}
    url = "https://api.dialogflow.com/v1/query?"
    url += "v=" + CFG['dialogflow']['id']
    url += "&sessionId=" + CFG['dialogflow']['session']
    url += "&lang=" + CFG['dialogflow']['lang']
    url += "&query=" + question
    req = requests.get(url, headers=header)
    return req.json()


@APPLICATION.route("/api/intents")
def get_intents():
    """
        A utility route which provides the list of all the bot's
        intents for debugging purposes.

        RETURNS: The JSON composition for the list of intents stored in the bot
    """

    key = CFG['dialogflow']['dev_key']
    header = {'Authorization': 'Bearer ' + key,
              'content-type': 'application/json'}
    url = "https://api.dialogflow.com/v1/intents?"
    url += "v=" + CFG['dialogflow']['id']
    url += "&lang=" + CFG['dialogflow']['lang']
    req = requests.get(url, headers=header)
    res = req.json()
    res_list = []
    for entry in res:
        res_list.append({'id': entry['id'], "name": entry['name']})
    statistics.answer_slot_config()
    return jsonify(str(res_list))


@APPLICATION.route('/webhook', methods=['POST'])
def webhook():
    """
        The main function of the webhook which listens for post requests
        from DialogFlow and resolves the answer.

        RETURNS: The modified response from the statistical handler
    """

    req = request.get_json(silent=True, force=True)
    print "REQUEST \n" + json.dumps(req, indent=4, sort_keys=True)

    text = req['result']['fulfillment'].get('speech')

    resolved_text = resolve(text)

    res = {'speech': resolved_text, 'displayText': resolved_text}

    return make_response(jsonify(res))


def resolve(answer):
    """
        The function which parses the bot's answer texts and replaces
        the dynamic syntax values with its designated assignments.
        answer -- The default answer from the bot's intent

        RETURNS: The fulfilled web hook answer
    """

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
    APPLICATION.run(host='0.0.0.0', port=5000)
