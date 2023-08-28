import shutil
import os
import copy
import json
import logging
import config
import re
from typing import Dict, List, Tuple, Optional, Any
from client.tasks.exceptions import NoAccountDataException
from functools import partial
import math


def eraseFiles(path: str):
    """
    Erases all files in a given folder.

    :param path: The path to the folder.
    """
    try:
        files = os.listdir(path)
    except FileNotFoundError:
        return
    
    for file in files:
        filePath = os.path.join(path, file)
        try:
            shutil.rmtree(filePath)
        except OSError:
            os.remove(filePath)

def makeDirectory(path: str) -> None:
    """
    Creates a directory at the given path.

    :param path: The path of the directory to create.
    """
    try:
        os.mkdir(path)
    except FileExistsError:
        return

def exportRaw(account: Dict[str, Any]) -> None:
    """
    Exports raw JSON data of an account.

    :param account: The account data to export as JSON.
    """
    makeDirectory(config.RAW_DATA_PATH)
    # usernames are globally unique
    with open(os.path.join(config.RAW_DATA_PATH, account["username"]), "w", encoding="utf-8") as fp:
        fp.write(json.dumps(account, indent=4))


def readRawExport(username: str) -> Dict[str, Any]:
    """
    Reads and returns the raw exported account data.

    :return: A tuple with a dictionary containing the raw exported account data and timestamp of last edit.
    """
    makeDirectory(config.RAW_DATA_PATH)
    
    rawData = {}
    filePath = os.path.join(config.RAW_DATA_PATH, username)
    try:
        with open(filePath, "r", encoding="utf-8") as fp:
            rawData = json.load(fp)

        timestamp = os.path.getmtime(filePath)
        return rawData, timestamp
    except FileNotFoundError:
        raise NoAccountDataException(f"No data found for account: {username}")

def readRawExports() -> List[Dict[str, Any]]:
    """
    Reads and returns the raw exported account data.

    :return: A list of dictionaries containing the raw exported account data.
    """
    makeDirectory(config.RAW_DATA_PATH)

    fileList = os.listdir(config.RAW_DATA_PATH)
    accounts = []

    for filename in fileList:
        with open(os.path.join(config.RAW_DATA_PATH, filename), "r", encoding="utf-8") as fp:
            accounts.append(json.load(fp))

    return accounts

class Export():
    def __init__(self, bannedTemplate: str, errorTemplate: str, failedSeparately: bool):
        """
        Initializes the Export instance.

        :param bannedTemplate: The template for banned accounts.
        :param errorTemplate: The template for error accounts.
        :param failedSeparately: Indicates whether failed accounts should be exported separately.
        """
        self.__evalPattern = r'\{eval\((.+?)\)\}\}'
        makeDirectory(config.EXPORT_PATH)

        self.singleTemplatesPath = os.path.join(config.TEMPLATE_PATH, "single")
        self.singleExportPath = os.path.join(config.EXPORT_PATH, "single")
        makeDirectory(self.singleExportPath)
        eraseFiles(self.singleExportPath)
        self.singleTemplates = []
        self.__initTemplatesSingle()

        self.allTemplatesPath = os.path.join(config.TEMPLATE_PATH, "all")
        self.allExportPath = os.path.join(config.EXPORT_PATH, "all")
        makeDirectory(self.allExportPath)
        eraseFiles(self.allExportPath)
        self.allTemplates = []
        self.__initTemplatesAll()
        
        self.bannedTemplate = bannedTemplate
        self.errorTemplate = errorTemplate
        self.__failedSeparately = failedSeparately
        self.__failedPath = os.path.join(config.EXPORT_PATH, config.FAILED_ACCOUNT_PATH)
        try:
            os.remove(self.__failedPath)
        except FileNotFoundError:
            pass

    def __initTemplatesSingle(self) -> None:
        """
        Initializes the list of single templates by reading the template files from the single templates path.
        """
        for file in os.listdir(self.singleTemplatesPath):
            if file.endswith(".txt"):
                self.singleTemplates.append(file)

    def __initTemplatesAll(self) -> None:
        """
        Initializes the list of all templates by reading the template files from the all templates path.
        """
        for file in os.listdir(self.allTemplatesPath):
            if file.endswith(".txt"):
                path = os.path.join(self.allExportPath, str(file).split(".")[0])
                makeDirectory(path)
                self.allTemplates.append(file)
    
    def __splitFailed(self, accounts: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Splits the accounts into two lists: OK accounts and failed accounts.

        :param accounts: The list of accounts to split.
        :return: A tuple containing the lists of OK accounts and failed accounts.
        """
        okAccounts = []
        failedAccounts = []

        for account in accounts:
            if account["state"] == "OK":
                okAccounts.append(account)
            else:
                failedAccounts.append(account)

        return okAccounts, failedAccounts
    
    def __replaceEval(self, account: Dict[str, Any], match: re.Match) -> str:
        """
        Replace the evaluated content within {eval()} with the result of evaluation.

        :param account: The account data used for evaluation.
        :param match: The match object from regular expression.

        :return: The replacement string.

        If the evaluation of evalContent succeeds, returns the string representation of the result.
        If the evaluation fails or data doesn't exist for the account, returns the original evalContent.
        """
        evalContent = match.group(1)
        try:
            replacement = str(eval(evalContent, {'account': account, 'math': math}))
            return replacement
        except: # Bad eval string or data doesn't exist for the account
            return evalContent
    
    def __replaceTemplatePlaceholders(self, account: Dict[str, Any], template: str) -> Optional[str]:
        """
        Replaces the placeholders in the template with the corresponding values from the account.

        :param account: The account data.
        :param template: The template string.
        :return: The modified template string with replaced placeholders, or None if the template is empty.
        """
        data = ""

        if account["state"] == "OK":
            data = copy.copy(template)
        elif account["state"] == "BANNED":
            data = copy.copy(self.bannedTemplate)
        else:
            data = copy.copy(self.errorTemplate)
        
        if data:
            for key, value in account.items():
                data = data.replace(f"{{{key}}}", str(value))

            replaceFunction = partial(self.__replaceEval, account)
            data = re.sub(self.__evalPattern, replaceFunction, data)

            return data
        else:
            return None
        
    def __exportSingle(self, accounts: List[Dict[str, Any]]) -> None:
        """
        Performs the "single" type export for all templates, where all accounts are written to a single file for each template.

        :param accounts: The list of accounts to export.
        """
        for template in self.singleTemplates:
            with open(os.path.join(self.singleTemplatesPath, template), "r", encoding="utf-8", newline="") as filePointer:
                templateData = filePointer.read()
                with open(os.path.join(self.singleExportPath, template), "a+", encoding="utf-8", newline="") as exportPointer:
                    for account in accounts:
                        data = self.__replaceTemplatePlaceholders(account, templateData)
                        if data:
                            exportPointer.write(data + "\n")

    def __exportAll(self, accounts: List[Dict[str, Any]]) -> None:
        """
        Performs the "all" type export for all templates, where all accounts are written to separate files for each template.

        :param accounts: The list of accounts to export.
        """
        for template in self.allTemplates:
            with open(os.path.join(self.allTemplatesPath, template), "r", encoding="utf-8", newline="") as filePointer:
                templateData = filePointer.read()
                for account in accounts:
                        data = self.__replaceTemplatePlaceholders(account, templateData)
                        if data:
                            with open(os.path.join(self.allExportPath, str(template).split('.')[0], f"{account['username']}.txt"), "w", encoding="utf-8", newline="") as exportPointer:
                                exportPointer.write(data + "\n")

    def __exportFailed(self, accounts: List[Dict[str, Any]]) -> None:
        """
        Performs the "failed" type export for accounts that are not in the "OK" state.

        :param accounts: The list of failed accounts to export.
        """
        with open(self.__failedPath, "a+", encoding="utf-8", newline="") as exportPointer:
            for account in accounts:
                data = self.__replaceTemplatePlaceholders(account, "")
                if data:
                    exportPointer.write(data + "\n")
    
    def exportNow(self, accounts: List[Dict[str, Any]]) -> None:
        """
        Performs the export of accounts based on the configured settings.

        :param accounts: The list of accounts to export.
        """
        if self.__failedSeparately:
            okAccounts, failedAccounts = self.__splitFailed(accounts)
            self.__exportSingle(okAccounts)
            self.__exportAll(okAccounts)
            self.__exportFailed(failedAccounts)
        else:
            self.__exportSingle(accounts)
            self.__exportAll(accounts)

def exportUnfinished(accounts: List[Dict[str, Any]], delimiter: str) -> None:
    """
    Exports unfinished accounts to a file (ones that don't have a state)

    :param accounts: The list of all accounts.
    :param delimiter: The delimiter to use between the username and password in the export file.
    """
    with open(config.UNFINISHED_ACCOUNT_PATH, "w", encoding="utf-8", newline="") as exportPointer:
        for account in accounts:
            if account.get("state") is None:
                exportPointer.write(f"{account['username']}{delimiter}{account['password']}\n")


def exportAccounts(bannedTemplate: str, errorTemplate: str, failedSeparately: bool) -> None:
    """
    Handles the exporting of accounts.

    :param bannedTemplate: The template to use for banned accounts.
    :param errorTemplate: The template to use for accounts with errors.
    :param failedSeparately: A flag indicating whether failed accounts should be exported separately.
    """
    logging.info("Exporting...")
    export = Export(bannedTemplate, errorTemplate, failedSeparately)
    accounts = readRawExports()
    export.exportNow(accounts)
    logging.info("Exported!")


def exportCustomAccountList(bannedTemplate: str, errorTemplate: str, failedSeparately: bool, accounts: List[Dict[str, Any]]) -> None:
    """
    Handles the exporting of accounts.

    :param accounts: The list of accounts to export.
    :param bannedTemplate: The template to use for banned accounts.
    :param errorTemplate: The template to use for accounts with errors.
    :param failedSeparately: A flag indicating whether failed accounts should be exported separately.
    """
    logging.info("Exporting...")
    export = Export(bannedTemplate, errorTemplate, failedSeparately)
    try:
        accounts = [readRawExport(account["username"])[0] for account in accounts]
    except NoAccountDataException as exception:
        logging.error(f"Exporting failed! {exception.message}")
        return
    
    export.exportNow(accounts)
    logging.info("Exported!")
