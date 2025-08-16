import hashlib
import os
import base58
from .base import BaseNetwork, GeneratedKey

class BitcoinLikeNetwork(BaseNetwork):
    """Генерация адресов для Bitcoin-подобных сетей (BTC, LTC, DOGE)"""
    
    def __init__(self, currency: str, network: str):
        self.currency = currency
        self.network = network
        
        # Настройки для разных сетей (version bytes)
        if network == 'bitcoin':
            self.version_bytes = {'p2pkh': 0x00, 'wif': 0x80}
        elif network == 'litecoin':
            self.version_bytes = {'p2pkh': 0x30, 'wif': 0xB0}
        elif network == 'dogecoin':
            self.version_bytes = {'p2pkh': 0x1E, 'wif': 0x9E}
        else:
            raise ValueError(f"Unsupported network: {network}")

    def _private_key_to_wif(self, private_key_bytes: bytes) -> str:
        """Конвертирует приватный ключ в WIF формат"""
        # Добавляем версию сети + приватный ключ + 0x01 (compressed)
        extended = bytes([self.version_bytes['wif']]) + private_key_bytes + b'\x01'
        
        # Двойной SHA256 для checksum
        checksum = hashlib.sha256(hashlib.sha256(extended).digest()).digest()[:4]
        
        # Base58 кодирование
        return base58.b58encode(extended + checksum).decode()

    def _private_key_to_address(self, private_key_bytes: bytes) -> str:
        """Генерирует P2PKH адрес из приватного ключа"""
        try:
            import secp256k1
        except ImportError:
            raise ImportError("secp256k1 library required: pip install secp256k1")
            
        # Получаем публичный ключ (compressed)
        privkey = secp256k1.PrivateKey(private_key_bytes)
        pubkey = privkey.pubkey.serialize(compressed=True)
        
        # RIPEMD160(SHA256(pubkey))
        sha256_hash = hashlib.sha256(pubkey).digest()
        ripemd160 = hashlib.new('ripemd160', sha256_hash).digest()
        
        # Добавляем version byte для сети
        versioned = bytes([self.version_bytes['p2pkh']]) + ripemd160
        
        # Двойной SHA256 для checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
        
        # Base58 кодирование
        return base58.b58encode(versioned + checksum).decode()

    def generate(self) -> GeneratedKey:
        """Генерирует новый адрес и приватный ключ в WIF формате"""
        # Генерируем случайный 32-байт приватный ключ
        private_key_bytes = os.urandom(32)
        
        # Обеспечиваем что ключ в правильном диапазоне (меньше порядка кривой secp256k1)
        secp256k1_order = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        while int.from_bytes(private_key_bytes, 'big') >= secp256k1_order:
            private_key_bytes = os.urandom(32)
        
        address = self._private_key_to_address(private_key_bytes)
        wif = self._private_key_to_wif(private_key_bytes)
        
        return GeneratedKey(address=address, private_key=wif, currency=self.currency)
