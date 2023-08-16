import json
import requests


def get(url, header, retry=2):
    payload = {}
    for num in range(retry):
        try:
            response = requests.request("GET", url, headers=header, data=payload, timeout=10)
            if response.status_code == 200:
                break
        except Exception as e:
            print(e.__context__)
            return None
    result = None
    if response.status_code != 200:
        print("url: " + url)
        print("payload: " + str(payload))
        print("status_code: " + str(response.status_code))
    else:
        if response:
            try:
                result = response.json()
            except AttributeError:
                return None
    return result


def post(url, header, payload, retry=2):
    payload = json.dumps(payload)
    for num in range(retry):
        try:
            response = requests.request("POST", url, headers=header, data=payload, timeout=10)
            if response.status_code == 200:
                break
        except Exception as e:
            print(e.__context__)
            return None

    result = None
    if response.status_code != 200:
        print("url: " + url)
        print("payload: " + payload)
        print("status_code: " + str(response.status_code))
        print("text: " + response.text)
    else:
        if response:
            try:
                result = response.json()
            except AttributeError:
                return None
    return result
