import os
from .base import BaseNetwork, GeneratedKey

class BSCNetwork(BaseNetwork):
    """Генерация Binance Smart Chain (BSC/BNB) адресов"""
    
    def __init__(self):
        self.currency = "BSC"

    def generate(self) -> GeneratedKey:
        """Генерирует новый BSC адрес и приватный ключ"""
        try:
            from web3 import Web3
            from eth_account import Account
        except ImportError:
            raise ImportError("web3 and eth-account required: pip install web3 eth-account")
        
        # BSC использует тот же формат что и Ethereum (EVM совместимая)
        account = Account.create()
        
        return GeneratedKey(
            address=account.address,  # 0x... формат
            private_key=account.key.hex(),
            currency=self.currency
        )

class PolygonNetwork(BaseNetwork):
    """Генерация Polygon (MATIC) адресов"""
    
    def __init__(self):
        self.currency = "MATIC"

    def generate(self) -> GeneratedKey:
        """Генерирует новый Polygon адрес и приватный ключ"""
        try:
            from web3 import Web3
            from eth_account import Account
        except ImportError:
            raise ImportError("web3 and eth-account required: pip install web3 eth-account")
        
        # Polygon использует тот же формат что и Ethereum
        account = Account.create()
        
        return GeneratedKey(
            address=account.address,  # 0x... формат  
            private_key=account.key.hex(),
            currency=self.currency
        )

class ArbitrumNetwork(BaseNetwork):
    """Генерация Arbitrum адресов"""
    
    def __init__(self):
        self.currency = "ARB"

    def generate(self) -> GeneratedKey:
        """Генерирует новый Arbitrum адрес и приватный ключ"""
        try:
            from web3 import Web3
            from eth_account import Account
        except ImportError:
            raise ImportError("web3 and eth-account required: pip install web3 eth-account")
        
        # Arbitrum использует тот же формат что и Ethereum (Layer 2)
        account = Account.create()
        
        return GeneratedKey(
            address=account.address,  # 0x... формат
            private_key=account.key.hex(),
            currency=self.currency
        )

class OptimismNetwork(BaseNetwork):
    """Генерация Optimism адресов"""
    
    def __init__(self):
        self.currency = "OP"

    def generate(self) -> GeneratedKey:
        """Генерирует новый Optimism адрес и приватный ключ"""
        try:
            from web3 import Web3
            from eth_account import Account
        except ImportError:
            raise ImportError("web3 and eth-account required: pip install web3 eth-account")
        
        # Optimism использует тот же формат что и Ethereum (Layer 2)
        account = Account.create()
        
        return GeneratedKey(
            address=account.address,  # 0x... формат
            private_key=account.key.hex(),
            currency=self.currency
        )
