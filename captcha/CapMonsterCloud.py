from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import HcaptchaProxylessRequest, HcaptchaRequest
import logging
import asyncio
import config
from typing import Optional, Dict, Any
from captcha.SolvingService import SolvingService
from captcha.constants import CAP_MONSTER_CLOUD


class CapMonsterCloud(SolvingService):

    @staticmethod
    def solve(apiKey: str, key: str, data: str, userAgent: str, proxy: Optional[Dict[str, Any]] = None) -> Optional[str]:
        clientOptions = ClientOptions(api_key=apiKey)
        capMonsterClient = CapMonsterClient(options=clientOptions)
        requestData = {
            "websiteUrl": config.LOGIN_URL,
            "websiteKey": key,
            "user_agent": userAgent,
            "data": data,
        }

        if proxy is None:
            hCaptchaRequest = HcaptchaProxylessRequest(**requestData)
        else:
            hCaptchaRequest = HcaptchaRequest(
                **requestData,
                proxy_type=proxy["proxyType"],
                proxy_address=proxy["proxyAddress"],
                proxy_port=proxy["proxyPort"],
                proxy_login=proxy["proxyLogin"],
                proxy_password=proxy["proxyPassword"],
            )

        try:
            result = asyncio.run(capMonsterClient.solve_captcha(hCaptchaRequest))
            solution = result["gRecaptchaResponse"]
        except Exception as e:
            logging.error(f"{CAP_MONSTER_CLOUD} Failed: {e}")
            return None

        return solution
