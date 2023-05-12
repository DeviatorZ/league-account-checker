from GUI.main import setupGUI
from GUI.main import runGUI
import os

def main():
    cwd = os.getcwd()
    mainWindow = setupGUI(cwd)
    runGUI(mainWindow, cwd)

if __name__ == "__main__":
    main()