from abc import ABC, abstractmethod
from typing import Optional


class SolvingService(ABC):

    @staticmethod
    @abstractmethod
    def solve(apiKey: str, key: str, data: str) -> Optional[str]:
        raise NotImplementedError
