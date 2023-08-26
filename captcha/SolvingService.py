from abc import ABC, abstractmethod
from typing import Optional


class SolvingService(ABC):

    @staticmethod
    @abstractmethod
    def solve(apiKey, key, data) -> Optional[str]:
        raise NotImplementedError
