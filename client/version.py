import win32api
import os
from typing import Optional, List, Tuple

def getFileVersion(filePath: str) -> Tuple[Optional[List[int]], bool]:
    try:
        info = win32api.GetFileVersionInfo(filePath, os.sep)
        version = (info['FileVersionMS'] >> 16, info['FileVersionMS'] & 0xFFFF, info['FileVersionLS'] >> 16)
        return ".".join(map(str, version)), True
    except Exception as e:
        return e, False
