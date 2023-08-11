from client.tasks.exceptions import NoAccountDataException
import GUI.keys as guiKeys
from client.tasks.export import readRawExport
import time
from typing import Dict, Any

def checkCanSkip(settings: Dict[str, Any], account: Dict[str, Any]) -> bool:
        """
        Checks if an account can be skipped based on execution settings.

        :param settings: A dictionary containing execution settings.
        :param account: A dictionary containing account data.

        :return: True if the account can be skipped, False otherwise.
        """
        if not settings[guiKeys.SKIP_ACCOUNTS_WITH_DATA]:
            return False
        
        try:
            accountData, timestamp = readRawExport(account["username"])
            accountState = accountData["state"]
            age = time.time() - timestamp

            if settings[guiKeys.DONT_SKIP_ACCOUNTS_WITH_DATA_ONE_DAY_OLD] and age > 86400:
                return False
            elif settings[guiKeys.DONT_SKIP_ACCOUNTS_WITH_DATA_ONE_WEEK_OLD] and age > 604800:
                return False
            
            if accountState == "BANNED":
                if settings[guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_BANNED] and accountData.get("banExpiration") != "PERMANENT":
                    return False
                elif settings[guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_PERMABANNED] and accountData.get("banExpiration") == "PERMANENT":
                    return False
                
            if accountState == "RETRY_LIMIT_EXCEEDED" and settings[guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_TOO_MANY_ATTEMPS]:
                return False
            
            if accountState == "AUTH_FAILURE" and settings[guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_AUTH_FAILURE]:
                return False
            
            if settings[guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_GENERAL_ERROR]:
                otherStates = {"OK", "BANNED", "RETRY_LIMIT_EXCEEDED", "AUTH_FAILURE"}
                if accountState not in otherStates:
                    return False
                
            return True
        except NoAccountDataException:
            return False