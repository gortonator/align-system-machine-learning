import requests
import os
import json


def answer_slot_config(update):
    if not(os.path.exists("answers.json")):
        empty_config = {}
        with open('answers.json', 'w') as f:
            json.dump(empty_config, f)
    else:
        stats = {}
        with open('answers.json') as json_file:
            stats = json.load(json_file)
            for key, value in stats.iteritems():
                try:
                    if value['value'] == "" or update:
                        fn = globals()[value['fn']]
                        value['value'] = fn()
                except TypeError:
                    print "Not a valid method"
                    continue
        with open('answers.json', 'w') as f:
            json.dump(stats, f, indent=4, sort_keys=True)


def get_student_count():
    req = requests.get("http://asd2.ccs.neu.edu:8080/webapi/admin-facing/students")
    return "4259"


def get_graduated_count():
    return "5000"