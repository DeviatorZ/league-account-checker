from captcha.CapMonsterCloud import CapMonsterCloud
from captcha.exceptions import CaptchaException

CAP_MONSTER_CLOUD = "capMonsterCloud"


class CaptchaProxy:
    __solveByName = {
        CAP_MONSTER_CLOUD: CapMonsterCloud.solve
    }

    @classmethod
    def solve(cls, providerName, apiKey, key, data) -> str:
        token = cls.__solveByName[providerName](apiKey, key, data)

        if token is None:
            raise CaptchaException()
        
        return token
