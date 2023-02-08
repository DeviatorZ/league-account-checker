import requests
from time import sleep
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# handles skin and champion json file updating, uses community links as they usually update sooner than riot
def update(window):
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    window["updateStatus"].update("Updating...")

    try:
        response = session.get("https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json")
        if response.status_code == 200:
            with open("champions.json", "w") as fp:
                fp.write(json.dumps(response.json(), indent=4))
        else:
            raise Exception
    except:
        window["updateStatus"].update("Update failed...")
        sleep(5)
        window["updateStatus"].update("")
        return


    try:
        response = session.get("https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/skins.json")
        if response.status_code == 200:
            with open("skins.json", "w") as fp:
                fp.write(json.dumps(response.json(), indent=4))
        else:
            raise Exception
    except:
        window["updateStatus"].update("Update failed...")
        sleep(5)
        window["updateStatus"].update("")
        return
    
    window["updateStatus"].update("Updated!")
    sleep(5)
    window["updateStatus"].update("")