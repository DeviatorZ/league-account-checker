from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import HcaptchaProxylessRequest
import logging
import asyncio
import config
from typing import Optional
from captcha.SolvingService import SolvingService


class CapMonsterCloud(SolvingService):

    @staticmethod
    def solve(apiKey, key, data) -> Optional[str]:
        clientOptions = ClientOptions(api_key=apiKey)
        capMonsterClient = CapMonsterClient(options=clientOptions)
        hCaptchaRequest = HcaptchaProxylessRequest(
            websiteUrl=config.LOGIN_URL,
            websiteKey=key,
            user_agent=config.LOGIN_USER_AGENT,
            data=data
        )

        try:
            result = asyncio.run(capMonsterClient.solve_captcha(hCaptchaRequest))
            return result.get("gRecaptchaResponse")
        except Exception as e:
            logging.debug(f"CapMonsterCloud Failed: {e}")
            return None