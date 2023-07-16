from typing import Dict
import PySimpleGUI as sg
from client.champions import Champions

def addChampion(values: Dict, championShopList: sg.Multiline, championShopResponse: sg.Text):
    """
    Adds a champion to the purchase list in the GUI.

    :values: The dictionary of values from the GUI.
    :championShopList: The Multiline element displaying the champion purchase list.
    :championShopResponse: The Text element displaying the response message.
    """
    championChoice = values["championChoice"]
    if championChoice:
        championId = Champions.getChampionIdByName(championChoice)
        if championId is None:
            championShopResponse.update(value="Champion not found!")
            return
        
        try:
            championPurchaseList = eval(values["championShopList"])
        except Exception:
            championShopResponse.update(value="Invalid list format!")
            return
        
        if championChoice in championPurchaseList:
            championShopResponse.update(value=f"{championChoice} already in the list!")
            return
        championPurchaseList.append(championChoice)
        championShopList.update(value=str(championPurchaseList))
        championShopResponse.update(value=f"{championChoice} added.")


def removeChampion(values: Dict, championShopList: sg.Multiline, championShopResponse: sg.Text):
    """
    Removes a champion from the purchase list in the GUI.

    :values: The dictionary of values from the GUI.
    :championShopList: The Multiline element displaying the champion purchase list.
    :championShopResponse: The Text element displaying the response message.
    """
    championChoice = values["championChoice"]
    if championChoice:
        championId = Champions.getChampionIdByName(championChoice)
        if championId is None:
            championShopResponse.update(value="Champion not found!")
            return
        
        try:
            championPurchaseList = eval(values["championShopList"])
        except Exception:
            championShopResponse.update(value="Invalid list format!")
            return
        
        if championChoice in championPurchaseList:
            championPurchaseList.remove(championChoice)
            championShopResponse.update(value=f"{championChoice} removed.")
            championShopList.update(value=str(championPurchaseList))
        else:
            championShopResponse.update(value=f"{championChoice} not in the list!")