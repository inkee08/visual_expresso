import json
import requests
import getpass
import os
from dotenv import load_dotenv
load_dotenv() 
from requests.auth import HTTPBasicAuth 


def getauth():
    username = os.getenv('visuser')
    if not username:
        username = input('Visualizer Email: ')
        while not username:
            username = input('Visualizer Email: ')
    password = os.getenv('vispass')
    if not password:
        password = getpass.getpass()
        while not password:
            password = getpass.getpass()

    return username, password

def getshots(username, password):
    url = "https://visualizer.coffee/api/shots"

    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    
    if response.status_code == 200:
        print('Successfully received list of hosts')
    else:
        print(f'Unsuccessful, Reason: {response.reason}')

def getshot(username, password, id):
    url = f"https://visualizer.coffee/api/shots/{id}"
    
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    
    if response.status_code == 200:
        print('Successfully received shot data')
        print(f'{response.json()}')
    else:
        print(f'Unsuccessful, Reason: {response.reason}')

def parsedata():
    with open('shots_list_example.json') as f:
        data = json.load(f)

    # for i in data['data']:
    #     print(i['id'])
    username, password = getauth()

    shotid = data['data'][0]['id']

    print(getshot(username, password, shotid))

if __name__ == "__main__":
    ...
    parsedata()
    # getshots()