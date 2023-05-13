from time import sleep
import json
import requests
import PySimpleGUI as sg
import config
from typing import Dict, Any

def updateInformation(updateButton: sg.Button) -> None:
    """
    Launches the skin and champion file update task.

    :param updateButton: The update button element.
    """
    startingText = updateButton.ButtonText
    updateButton.update(disabled=True, text="Updating...")
    success = updateData()
    if success:
        updateButton.update(disabled=True, text="Updated!")
    else:
        updateButton.update(disabled=True, text="Update failed...")
    
    sleep(2)
    updateButton.update(disabled=False, text=startingText)


def downloadJson(URL: str) -> dict:
    """
    Downloads JSON data from the given URL.

    :param URL: The URL of the JSON data.
    :return: The downloaded JSON data as a dictionary, or None if the download fails.
    """
    for _ in range(3):
        try:
            response = requests.get(URL)
            if response.status_code == 200:
                data = response.json()
                return data
        except:
            pass

    return None

def dumpJson(path: str, data: Dict[str, Any]) -> None:
    """
    Dumps JSON data to a file.

    :param path: The file path to save the JSON data.
    :param data: The JSON data to save.
    """
    with open(path, "w") as filePointer:
        filePointer.write(json.dumps(data, indent=4))

def updateData() -> bool:
    """
    Handles the skin and champion JSON file updating.

    :return: True if the update is successful, False otherwise.
    """
    championData = downloadJson(config.CHAMPION_DATA_URL)
    if championData is None:
        return False
    
    skinData = downloadJson(config.SKIN_DATA_URL)
    if skinData is None:
        return False
    
    dumpJson(config.CHAMPION_FILE_PATH, championData)
    dumpJson(config.SKIN_FILE_PATH, skinData)

    return True
