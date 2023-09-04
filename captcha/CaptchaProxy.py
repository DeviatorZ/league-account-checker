from captcha.CapMonsterCloud import CapMonsterCloud
from captcha.exceptions import CaptchaException
from captcha.constants import *


class CaptchaProxy:
    __solveByName = {
        CAP_MONSTER_CLOUD: CapMonsterCloud.solve,
    }

    @classmethod
    def solve(cls, providerName: str, apiKey: str, key: str, data: str, userAgent: str) -> str:
        token = cls.__solveByName[providerName](apiKey, key, data, userAgent)

        if token is None:
            raise CaptchaException()
        
        return token
