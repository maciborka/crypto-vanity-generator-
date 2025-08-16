import os
from .base import BaseNetwork, GeneratedKey

class EthereumNetwork(BaseNetwork):
    """Генерация Ethereum адресов"""
    
    def __init__(self):
        self.currency = "ETH"

    def generate(self) -> GeneratedKey:
        """Генерирует новый Ethereum адрес и приватный ключ в hex формате"""
        try:
            from web3 import Web3
            from eth_account import Account
        except ImportError:
            raise ImportError("web3 and eth-account required: pip install web3 eth-account")
        
        # Создаём новый аккаунт
        account = Account.create()
        
        # Возвращаем адрес и приватный ключ
        return GeneratedKey(
            address=account.address,
            private_key=account.key.hex(),
            currency=self.currency
        )
