import shutil
import os
import copy


# erases all files in a given folder
def eraseFiles(path):
    try:
        for file in os.listdir(path):
            filePath = os.path.join(path, file)
            try:
                shutil.rmtree(filePath)
            except OSError:
                os.remove(filePath)
    except:
        pass

class Export():
    # sets up export by creating missing folders and reading the templates
    def __init__(self, singleTemplatesPath, singleExportPath, allTemplatesPath, allExportPath, bannedTemplate, errorTemplate):
        try:
            os.mkdir("export")
        except:
            pass

        try:
            os.mkdir("export\\single")
        except:
            pass

        try:
            os.mkdir("export\\all")
        except:
            pass

        self.singleTemplatesPath = singleTemplatesPath
        self.singleExportPath = singleExportPath
        self.singleTemplates = []

        for file in os.listdir(self.singleTemplatesPath):
            if file.endswith(".txt"):
                self.singleTemplates.append(file)

        self.allTemplatesPath = allTemplatesPath
        self.allExportPath = allExportPath
        self.allTemplates = []

        for file in os.listdir(self.allTemplatesPath):
            if file.endswith(".txt"):
                try:
                    path = os.path.join(self.allExportPath, str(file).split(".")[0])
                    os.mkdir(path)
                except Exception:
                    pass
                self.allTemplates.append(file)
        
        self.bannedTemplate = bannedTemplate
        self.errorTemplate = errorTemplate

    # "single" type export for all templates (all accounts in one file)
    def exportSingle(self, accounts):
        for template in self.singleTemplates:
            with open(f"{self.singleTemplatesPath}\{template}", "r", encoding="utf-8", newline="") as filePointer:
                fileData = filePointer.read()
                with open(f"{self.singleExportPath}\{template}", "a+", encoding="utf-8", newline="") as exportPointer:
                    for account in accounts:
                        if account["state"] == "OK":
                            data = copy.copy(fileData)
                        elif account["state"] == "BANNED":
                            data = copy.copy(self.bannedTemplate)
                        else:
                            data = copy.copy(self.errorTemplate)

                        for key, value in account.items():
                            data = data.replace(f"{{{key}}}", str(value))

                        if data:
                            exportPointer.write(data + "\n")

    # "all" type export for all templates (separate file for each account)
    def exportAll(self, accounts):
        for template in self.allTemplates:
            with open(f"{self.allTemplatesPath}\{template}", "r", encoding="utf-8", newline="") as filePointer:
                fileData = filePointer.read()
                for account in accounts:
                        if account["state"] == "OK":
                            data = copy.copy(fileData)
                        elif account["state"] == "BANNED":
                            data = copy.copy(self.bannedTemplate)
                        else:
                            data = copy.copy(self.errorTemplate)

                        for key, value in account.items():
                            data = data.replace(f"{{{key}}}", str(value))

                        if data:
                            with open(f"{self.allExportPath}\{str(template).split('.')[0]}\{account['username']}.txt", "w", encoding="utf-8", newline="") as exportPointer:
                                exportPointer.write(data + "\n")

# handles account exporting
def exportAccounts(accounts, bannedTemplate, errorTemplate):
    export = Export("templates\\single", "export\\single", "templates\\all", "export\\all", bannedTemplate, errorTemplate)
    export.exportSingle(accounts)
    export.exportAll(accounts)

