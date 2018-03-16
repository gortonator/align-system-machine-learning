import requests


def get_intents(cfg):
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
    return res_list