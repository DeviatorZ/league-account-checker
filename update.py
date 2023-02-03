import json
import requests
import time

def update():

    while True:
        response = requests.get("https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json")
        if response.status_code == 200:
            break
        time.sleep(1)

    with open("champions.json", "w") as fp:
        fp.write(json.dumps(response.json(), indent=4))

    while True:
        response = requests.get("https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/skins.json")
        if response.status_code == 200:
            break
        time.sleep(1)

    with open("skins.json", "w") as fp:
        fp.write(json.dumps(response.json(), indent=4))

if __name__ == "__main__":
    update()