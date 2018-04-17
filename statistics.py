"""
    A component of the web hook which pre-loads all dynamic data
    into a dictionary in memory for fast recall.
    Additional functions to get other statistics must
    have the values implemented in the REDIS cache first
    Then provide the proper function in the answers.json
    file to resolve for a particular value
    AUTHOR: Nicholas Carugati
"""
import os
import json
import traceback
import requests

HOST = "redis_client"
PORT_HOST = "15000"
with open('config.json') as json_data_file:
    CFG = json.load(json_data_file)


def answer_slot_config(update=False):
    """ Reads and parses the JSON from the answers file
        This routine can change the values periodically if chosen

        update -- if the pre-loader should update the answer values
        regardless if the answer is present (default False)
    """

    if not os.path.exists("answers.json"):
        empty_config = {}
        with open('answers.json', 'w') as answer_file:
            json.dump(empty_config, answer_file)
    else:
        with open('answers.json') as json_file:
            stats = json.load(json_file)
            for key, value in stats.iteritems():
                try:
                    if value['value'] == "" or update:
                        function_resolve = globals()[value['fn']]
                        if 'params' in value:
                            value['value'] = function_resolve(*value['params'])
                        else:
                            value['value'] = function_resolve()

                except TypeError:
                    print key + " Not a valid method"
                    traceback.print_stack()
                    return
        with open('answers.json', 'w') as answer_file:
            json.dump(stats, answer_file, indent=4, sort_keys=True)


def get_student_count():
    """ Retrieves the amount of students in the ALIGN program from the REDIS cache
        This routine can change the values periodically

        RETURN: The overall amount of students in the ALIGN program
    """

    req = requests.get(HOST + ":" + PORT_HOST + "/stats/student-numbers")
    total = 0
    count_tuple = req.json()
    for value in count_tuple.itervalues():
        total += int(value)
    return str(total)


def get_student_count_graduated():
    """ Retrieves the amount of students in the ALIGN program from the REDIS cache that graduated
        This routine can change the values periodically

        RETURN: The overall amount of students in the ALIGN program that graduated
    """

    req = requests.get(HOST + ":" + PORT_HOST + "/stats/num-graduates")
    count = str(req.json()['totalGraduates'])
    return count


def get_student_count_city(city):
    """ Retrieves the amount of students in the ALIGN program
        from the REDIS cache for a specific city
        This routine can change the values periodically if chosen

        city -- The city of choice to count the students
        RETURN: The overall amount of students in the ALIGN program
    """

    req = requests.get(HOST + ":" + PORT_HOST + "/stats/student-numbers")
    return str(req.json()[city])


def get_top_bachelors(max_count):
    """ Retrieves the top 10 bachelors degrees for all students in the program
        This routine can change the values periodically if chosen

        RETURN: The top 5 bachelor degrees in the program in a readable string
    """

    req = requests.get(HOST + ":" + PORT_HOST + "/stats/backgrounds/top?k=" + str(max_count))
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
    """ Retrieves the top 10 employers for all students in the program (full time)
        This routine can change the values periodically if chosen

        RETURN: The top 5 employers in the program in a readable string
    """

    req = requests.get(HOST + ":" + PORT_HOST + "/stats/employers/top?k=" + str(max_count))
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
