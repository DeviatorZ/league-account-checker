from captcha.CapMonsterCloud import CapMonsterCloud
from captcha.CapSolver import CapSolver
from captcha.exceptions import CaptchaException
from captcha.constants import *
import GUI.keys as guiKeys
from typing import Dict, Any


class CaptchaProxy:
    __solveByName = {
        CAP_MONSTER_CLOUD: CapMonsterCloud.solve,
        CAP_SOLVER: CapSolver.solve,
    }

    @classmethod
    def solve(cls, settings: Dict[str, Any], key: str, data: str, userAgent: str) -> str:
        if settings[guiKeys.USE_PROXY]:
            proxy = {
                "proxyType": settings[guiKeys.PROXY_TYPE],
                "proxyAddress": settings[guiKeys.PROXY_ADDRESS],
                "proxyPort": int(settings[guiKeys.PROXY_PORT]),
                "proxyLogin": settings[guiKeys.PROXY_LOGIN],
                "proxyPassword": settings[guiKeys.PROXY_PASSWORD],
            }
            token = cls.__solveByName[settings[guiKeys.CAPTCHA_SOLVER]](settings[guiKeys.CAPTCHA_API_KEY], key, data, userAgent, proxy)
        else:
            token = cls.__solveByName[settings[guiKeys.CAPTCHA_SOLVER]](settings[guiKeys.CAPTCHA_API_KEY], key, data, userAgent)

        if token is None:
            raise CaptchaException("Failed to get Captcha token!")
        
        return token
