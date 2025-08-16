import abc
from dataclasses import dataclass
from typing import Tuple

@dataclass
class GeneratedKey:
    address: str
    private_key: str  # WIF или hex
    currency: str

class BaseNetwork(abc.ABC):
    currency: str

    @abc.abstractmethod
    def generate(self) -> GeneratedKey:
        """Генерирует новый адрес и приватный ключ."""
        raise NotImplementedError
