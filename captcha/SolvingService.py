from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class SolvingService(ABC):

    @staticmethod
    @abstractmethod
    def solve(apiKey: str, key: str, data: str, userAgent: str, proxy: Optional[Dict[str, Any]] = None) -> Optional[str]:
        raise NotImplementedError
