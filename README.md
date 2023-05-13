# **DeviatorZ Account Checker**
Designed to obtain account data and perform various tasks through the League client.
## **Features**
- Process multiple accounts simultaneously.
- Check for bans and invalid credentials.
- Claim event rewards and spend event tokens.
- Open and disenchant loot.
- Export account information.
- Template system for custom export formats.
## **Disclaimer**
DeviatorZ Account Checker is not endorsed by Riot Games and does not reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games and all associated properties are trademarks or registered trademarks of Riot Games, Inc

## **Installation**
- Supported platform: 64-bit Windows (7 or higher).
- Download and install League of Legends.
- Download and install [Python 3.8 or higher](https://www.python.org/downloads/)
    - During installation, select "Add Python to PATH" and "pip" package manager (included by default). <br /> ![PythonExample](https://i.imgur.com/y1k3rmd.png)
- Download and extract the account checker. <br /> ![Download](https://i.imgur.com/jafvk8i.png)
- Open the command line (Windows key + "cmd" + Enter).
- Navigate to the checker directory using the command `cd pathToChecker` (e.g. `cd C:\Users\Administrator\Desktop\league-account-checker`).
- Install required packages using the command `pip install -r requirements.txt`.
- Once the installation is complete, you're ready to go!
- Launch the GUI by opening "main.pyw".
## **Main Tab**
![MainTab](https://i.imgur.com/XeZ91hk.png)

The main tab displays the console and tracks the progress. It offers the following options:
- **Start**: Begins checking the accounts with the current settings. The settings can be modified and saved using the "Save" button in each tab.
- **Stop**: Gracefully stops all running checker threads.
- **Exports folder**: Opens the export directory if it exists.

## **Settings Tab**
![SettingsTab](https://i.imgur.com/gAFycWL.png)
- **RiotClientServices.exe location**: Path to RiotClientServices.exe on your device. No need to change if using the default installation location.
- **LeagueClient.exe location**: Path to LeagueClient.exe on your device. No need to change if using the default installation location.
- **Account file location**: Path to your account file. The account file should contain one account per line, with the username and password separated by the specified delimiter: <br /> ![ExampleAccountFile](https://i.imgur.com/k9A8R4H.png)
- **Account file delimiter**: Select the delimiter used in your account file.
- **Thread count**: Number of threads to use for account checking. When using 1 thread, the Riot/League client will be able to update, while in other cases, patching is disabled.

## **Tasks Tab**
![TasksTab](https://i.imgur.com/xAymURs.png)

The tasks tab allows you to enable/disable various account-related tasks.
## **Export**
### **Templates**
Templates enable the export of account information in desired formats. There are two types of templates:
- **all**: Each account is exported to a separate file.
- **single**: All accounts are exported to a single file.

Example templates can be found in the "templates" folder. Consider the following guidelines:
- Multiple templates can be used simultaneously.
- All template filenames should have the ".txt" extension.
- Place **all** type templates in the "templates/all" folder and **single** type templates in the "templates/single" folder.
- Same template can be placed in both folders. 
- Exports can be found in the "export" folder.
    - For **single** type exports, they will be located in the "export\single" folder with the file name "NameOfTheTemplate.txt". 
    - **all** type exports can be found in the "export\all" folder. Each **all** type template will have its own folder. Inside each folder, all accounts will be exported in separate files, using the usernames of the accounts as the filenames.
- If an account is banned or has invalid credentials, it will still be included in every export file using the "banned" and "error" templates, respectively. These templates can be specified in the [Export Tab.](#export-tab)
### **Export Tab**
![ExportTab](https://i.imgur.com/jsfEndE.png)
- **Banned account template**: Export template replacement for banned accounts.
- **Error account template**: Export template replacement for accounts that couldn't be checked. <br /> 
    - State "AUTH_FAILURE" if credentials are invalid.
    - State "VngAccountRequired" if the account needs updating (email and phone number need to be added).
    - State "RETRY_LIMIT_EXCEEDED" if there have been too many failed attempts at performing tasks on the account. Most likely, the server is down or the client is outdated. Try updating manually or running the account in single-threaded mode.
- To skip exporting banned or error accounts, leave the Banned/Error template empty. Alternatively, you can select "Export failed accounts separately" to export them in a separate file.
- **Raw export type**: determines the type of data obtained during account checking:
    - Minimal: Obtains only username, password, and region, useful for quick ban and credential checking.
    - Full: Obtains all available data.
- **Delete raw data**: Deletes raw export data. Raw data includes all data of an account that's exported when the account is finished. This will delete raw data of all accounts.
- **Export now**: Exports raw data using templates.
- **Update skin and champion information**: Tries to update champion and skin information. Skins are released nearly every patch, and it might take multiple days until data files are updatable. IDs unrecognized by the checker will not be exported, so make sure to stay updated!
