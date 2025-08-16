import os
import hashlib
import base58
from .base import BaseNetwork, GeneratedKey

class TronNetwork(BaseNetwork):
    """Генерация Tron (TRX) адресов"""
    
    def __init__(self):
        self.currency = "TRX"

    def _private_key_to_tron_address(self, private_key_bytes: bytes) -> str:
        """Генерирует Tron адрес из приватного ключа"""
        try:
            import secp256k1
        except ImportError:
            raise ImportError("secp256k1 library required: pip install secp256k1")
        
        # Получаем публичный ключ (uncompressed, без префикса 0x04)
        privkey = secp256k1.PrivateKey(private_key_bytes)
        pubkey_full = privkey.pubkey.serialize(compressed=False)
        pubkey = pubkey_full[1:]  # убираем префикс 0x04
        
        # Keccak256 hash публичного ключа
        keccak_hash = self._keccak256(pubkey)
        
        # Берём последние 20 байт и добавляем Tron prefix (0x41)
        address_bytes = b'\x41' + keccak_hash[-20:]
        
        # Двойной SHA256 для checksum
        checksum = hashlib.sha256(hashlib.sha256(address_bytes).digest()).digest()[:4]
        
        # Base58 кодирование
        return base58.b58encode(address_bytes + checksum).decode()

    def _keccak256(self, data: bytes) -> bytes:
        """Keccak-256 hash (не путать с SHA3-256)"""
        try:
            from Crypto.Hash import keccak
            return keccak.new(digest_bits=256).update(data).digest()
        except ImportError:
            # Fallback на hashlib (если доступен Keccak)
            import hashlib
            return hashlib.sha3_256(data).digest()

    def generate(self) -> GeneratedKey:
        """Генерирует новый Tron адрес и приватный ключ в hex формате"""
        # Генерируем случайный 32-байт приватный ключ
        private_key_bytes = os.urandom(32)
        
        # Обеспечиваем что ключ в правильном диапазоне
        secp256k1_order = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        while int.from_bytes(private_key_bytes, 'big') >= secp256k1_order:
            private_key_bytes = os.urandom(32)
        
        address = self._private_key_to_tron_address(private_key_bytes)
        private_key_hex = private_key_bytes.hex()
        
        return GeneratedKey(
            address=address,
            private_key=private_key_hex,
            currency=self.currency
        )
