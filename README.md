# DeviatorZ Account Checker
League of Legends account checker <br />
Tested and working on Windows 7 (Python 3.8), Windows Server 2019 (Python 3.10).
## Features
- Process multiple accounts at once
- Checks for bans, invalid credentials
- Claims event rewards and spends event tokens
- Opens and disenchants loot
- Exports account information
- Template system to export in custom format

## How to install
- Only windows 7 or higher supported
- Download and install League of Legends - make sure that the client is up to date for each server that your accounts are on
- Download and install [Python 3.7 or higher](https://www.python.org/downloads/)
    - For next step to work select "Add python to path" and "pip" package manager(included in default installation) <br /> ![PythonExample](https://i.imgur.com/y1k3rmd.png)
- Download and extract the checker <br /> ![Download](https://i.imgur.com/jafvk8i.png)
- Install required packages using "pip":
    - Enter command line (on windows - press Windows key, type in "cmd" and press Enter)
    - Use command "cd pathToChecker" e.g. "cd C:\Users\Administrator\Desktop\league-account-checker"
    - Use command "pip install -r requirements.txt"
    - Once install is finished you'll be ready to go!
- Launch the GUI by opening "main.pyw"
## Main
![MainTab](https://i.imgur.com/BkJELsk.png)

Here you can see the console and track the progress. 
- "Start" - starts checking accounts if settings are properly configured ("Save" button in each tab is only to save for next launch, "Start" will use current settings regardless whether they are saved or not). If there's an issue - an error will be shown in the console.
- "Stop" - gracefully stops all running checker threads (exporting will be skipped)
- "Exports folder" - opens export directory if it exists
- "Erase exports" - erases all export files in the export directory

## Settings
![SettingsTab](https://i.imgur.com/OXvyGit.png)
- "RiotClientServices.exe" location" - path to RiotClientServices.exe on your device. No need to change if using default install location
- "LeagueClient.exe location" - path to LeagueClient.exe on your device. No need to change if using default install location
- "Account file location" - path to your account file. Account file should contain one account per line with username, delimiter and a password. e.g. with "," as delimiter: <br /> ![ExampleAccountFile](https://i.imgur.com/k9A8R4H.png)
- "Account file delimiter" - select the delimiter that you're using in your account file
- "Thread count" - amount of accounts to check at once. 

## Tasks
![TasksTab](https://i.imgur.com/FrOF7XK.png)

## Export
### Templates
Templates are a way for the user to export account information in a desired format. There are 2 types of templates:
- all - use a separate file for each account.
- single - export all accounts in a single file.

Example templates can be found in the "templates" folder. General guidelines:
- As many templates can be used at once as needed
- Filename extension of all templates should be ".txt". 
- Templates that should be used as "all" type should be placed inside "templates\all", for "single" type place them in "templates\single". 
- Same template can be placed in both folders. 
- Exports can be found in "export" folder. 
    - "single" type exports will be in "export\single" folder with file name being "NameOfTheTemplate.txt". 
    - "all" type exports can be found in "export\all" folder with each "all" type template having it's own folder. Inside each folder all accounts will be exported in separate files with filenames using usernames of the accounts
- If an account is banned or has invalid credentials it will still be included in every export file using "banned" and "error" templates respectively. These templates can be specified in [export tab](#export)
### Export tab
![ExportTab](https://i.imgur.com/umM0JRK.png)
- "Banned account template" - export template replacement for banned accounts
- "Error account template" - export template replacement for accounts that couldn't be checked. <br /> 
    - state "AUTH_FAILURE" if credentials are invalid 
    - state "VngAccountRequired" if account needs updating (email and phone number need to be added)
    - state "RETRY_LIMIT_EXCEEDED" if there have been too many failed attempts at performing tasks on the account. Most likely the server is down or the client is outdated for that server - make sure to update manually
- Leave Banned/Error template empty in order to skip exporting such accounts
- "Standard export type":
    - Minimal - export only username, password and region, useful for quick ban and credential checking.
    - Full - export using all available variables
- "Delete raw data" - deletes raw export data. Raw data - all data of an account that's exported whenever an account is finished. This will delete raw data of all accounts.
- "Export now" - exports raw data using templates.
- "Update skin and champion information" - tries to update champion and skin information. Skins come out nearly every patch and it might take multiple days until data files are updatable. Ids unrecognized by the checker won't get exported so make sure to stay updated!
