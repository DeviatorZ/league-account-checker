from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import HcaptchaProxylessRequest
import logging
import asyncio
import config
from typing import Optional
from captcha.SolvingService import SolvingService
from captcha.constants import CAP_MONSTER_CLOUD

class CapMonsterCloud(SolvingService):

    @staticmethod
    def solve(apiKey: str, key: str, data: str, userAgent: str) -> Optional[str]:
        clientOptions = ClientOptions(api_key=apiKey)
        capMonsterClient = CapMonsterClient(options=clientOptions)
        hCaptchaRequest = HcaptchaProxylessRequest(
            websiteUrl=config.LOGIN_URL,
            websiteKey=key,
            user_agent=userAgent,
            data=data,
        )

        try:
            result = asyncio.run(capMonsterClient.solve_captcha(hCaptchaRequest))
            return result.get("gRecaptchaResponse")
        except Exception as e:
            logging.error(f"{CAP_MONSTER_CLOUD} Failed: {e}")
            return None