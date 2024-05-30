from typing import Tuple
import os
import plistlib

def getRiotClientVersion(filePath: str) -> Tuple[str, bool]:
    try:
        with open(os.path.join(os.path.abspath(os.path.join(filePath, "../../")), "Info.plist"), "rb") as plistFile:
            return plistlib.load(plistFile)["FileVersion"], True
    except Exception as e:
        return str(e), False
