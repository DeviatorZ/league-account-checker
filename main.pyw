from threading import Lock
from GUI.main import setupGUI
from GUI.main import runGUI
import os

def main():
    cwd = os.getcwd()
    lock = Lock()
    mainWindow = setupGUI(cwd)
    runGUI(mainWindow, cwd, lock)

if __name__ == "__main__":
    main()