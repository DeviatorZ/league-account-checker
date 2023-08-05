import logging
from typing import Dict, Any
from GUI.exceptions import InvalidPathException
from client.tasks.export import exportCustomAccountList, eraseFiles
from GUI.userInputValidation import getAccounts, checkForFileErrors
import GUI.keys as guiKeys
import logging
import config

def exportInputAccounts(settings: Dict[str, Any]) -> None:
    """
    Exports accounts that are in the input file.

    :param settings: The user settings dictionary.
    """
    try:
        checkForFileErrors(settings)
    except InvalidPathException as exception:
        logging.error(exception.message)
        return
    
    try:
        accounts = getAccounts(settings)
    except IndexError:
        logging.error(f"Account file format error. Expected line format: username{settings['accountsDelimiter']}password")
        return 
    except SyntaxError as error:
        logging.error(error.msg)
        return
     
    exportCustomAccountList(settings[guiKeys.BANNED_ACCOUNT_STATE_TEMPLATE], settings[guiKeys.ERROR_ACCOUNT_STATE_TEMPLATE], settings[guiKeys.EXPORT_FAILED_SEPARATELY], accounts)


def deleteRawData() -> None:
    logging.info("Deleting data...")
    eraseFiles(config.RAW_DATA_PATH)
    logging.info("Data erased!")