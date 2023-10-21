import capsolver
import logging
import config
from typing import Optional, Dict, Any
from captcha.SolvingService import SolvingService
from captcha.constants import CAP_SOLVER
import logging

class CapSolver(SolvingService):

    @staticmethod
    def solve(apiKey: str, key: str, data: str, userAgent: str, proxy: Optional[Dict[str, Any]] = None) -> Optional[str]:
        capsolver.api_key = apiKey
        requestData = {
            "type": "HCaptchaTaskProxyLess",
            "websiteURL": config.LOGIN_URL,
            "websiteKey": key,
            "isInvisible": True,
            "isEnterprise": True,
            "enterprisePayload": {
                "rqdata": data,
            },
            "userAgent": userAgent,
        }

        try:
            if proxy is not None:
                requestData["type"] = "HCaptchaTask"
                requestData.update(proxy)
            result = capsolver.solve(requestData)
            solution = result["gRecaptchaResponse"]
        except Exception as e:
            logging.error(f"{CAP_SOLVER} Failed: {e}")
            return None

        return solution
