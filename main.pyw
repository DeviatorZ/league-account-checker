from GUI.main import setupGUI
from GUI.main import runGUI
import os

def main():
    """
    Main function to launch the account checker application.
    """
    cwd = os.getcwd()
    mainWindow = setupGUI(cwd)
    runGUI(mainWindow)

if __name__ == "__main__":
    main()