import os
import json
import requests
import traceback

host = "http://35.185.57.14"
port_host = "15000"
with open('config.json') as json_data_file:
    cfg = json.load(json_data_file)


def answer_slot_config(update=False):
    if not(os.path.exists("answers.json")):
        empty_config = {}
        with open('answers.json', 'w') as f:
            json.dump(empty_config, f)
    else:
        with open('answers.json') as json_file:
            stats = json.load(json_file)
            for key, value in stats.iteritems():
                try:
                    if value['value'] == "" or update:
                        fn = globals()[value['fn']]
                        if 'params' in value:
                            value['value'] = fn(*value['params'])
                        else:
                            value['value'] = fn()

                except TypeError:
                    print key + " Not a valid method"
                    traceback.print_stack()
                    return
        with open('answers.json', 'w') as f:
            json.dump(stats, f, indent=4, sort_keys=True)


def get_student_count():
    req = requests.get(host + ":" + port_host + "/stats/student-numbers")
    total = 0
    count_tuple = req.json()
    for key, value in count_tuple.iteritems():
        total += int(value)
    return str(total)


def get_student_count_graduated():
    req = requests.get(host + ":" + port_host + "/stats/num-graduates")
    count = str(req.json()['totalGraduates'])
    return count


def get_student_count_city(city):
    req = requests.get(host + ":" + port_host + "/stats/student-numbers")
    return str(req.json()[city])


def get_top_bachelors(max_count):
    req = requests.get(host + ":" + port_host + "/stats/backgrounds/top?k=" + str(max_count))
    bachelors = req.json()['backgrounds']
    if len(bachelors) == 1:
        return bachelors[0]
    composite = ""
    count = 0
    while count < len(bachelors):
        tex = bachelors[count]
        if count == len(bachelors) - 1 or count == max_count - 1:
            composite += "and " + str(tex)
        else:
            composite += str(tex) + ", "
        count += 1
    return composite


def get_top_employers(max_count):
    req = requests.get(host + ":" + port_host + "/stats/employers/top?k=" + str(max_count))
    employers = req.json()['employers']
    composite = ""
    if len(employers) == 1:
        return employers[0]
    count = 0
    while count < len(employers):
        tex = employers[count]
        if count == len(employers) - 1 or count == max_count - 1:
            composite += "and " + str(tex)
        else:
            composite += str(tex) + ", "
        count += 1
    return composite
