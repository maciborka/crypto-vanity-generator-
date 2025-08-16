#!/usr/bin/env python3
"""
Общий модуль для поиска паттернов в криптовалютных адресах
Используется в max_core_generator.py и batch_vanity_generator.py
"""

from typing import Tuple

def check_address_pattern(address: str, currency: str, pattern: str, pattern_type: str, ignore_case: bool = False) -> bool:
    """
    Универсальная функция проверки паттерна в адресе
    
    Args:
        address: Адрес для проверки
        currency: Тип криптовалюты (BTC, ETH, TRX, BSC, MATIC, ARB, OP, etc.)
        pattern: Искомый паттерн
        pattern_type: Тип поиска ('prefix' или 'suffix')
        ignore_case: Игнорировать регистр
        
    Returns:
        bool: True если паттерн найден
    """
    # Для EVM адресов (ETH, BSC, MATIC, ARB, OP) убираем 0x префикс для поиска
    if currency in ['ETH', 'BSC', 'MATIC', 'ARB', 'OP'] and address.startswith('0x'):
        search_address = address[2:]  # убираем 0x
    else:
        search_address = address
    
    # Применяем настройки регистра
    if ignore_case:
        search_address = search_address.lower()
        check_pattern = pattern.lower()
    else:
        check_pattern = pattern
    
    # Выполняем поиск
    if pattern_type == "prefix":
        return search_address.startswith(check_pattern)
    elif pattern_type == "suffix":
        return search_address.endswith(check_pattern)
    else:
        raise ValueError(f"Неподдерживаемый тип паттерна: {pattern_type}")

def estimate_pattern_difficulty(pattern: str, pattern_type: str, currency: str) -> Tuple[str, int, float]:
    """
    Универсальная оценка сложности поиска паттерна
    
    Args:
        pattern: Искомый паттерн
        pattern_type: Тип поиска ('prefix' или 'suffix')
        currency: Тип криптовалюты
        
    Returns:
        Tuple[str, int, float]: (уровень_сложности, вероятность, время_в_секундах)
    """
    # Базовые характеристики алфавитов для каждой валюты
    alphabets = {
        'BTC': 58,   # Base58
        'LTC': 58,   # Base58
        'DOGE': 58,  # Base58
        'ETH': 16,   # Hex (EVM)
        'TRX': 58,   # Base58
        'BSC': 16,   # Hex (EVM совместимый)
        'MATIC': 16, # Hex (EVM совместимый)
        'ARB': 16,   # Hex (EVM совместимый)
        'OP': 16     # Hex (EVM совместимый)
    }
    
    alphabet_size = alphabets.get(currency, 58)
    pattern_length = len(pattern)
    
    # Примерная вероятность
    probability = alphabet_size ** pattern_length
    
    # Классификация сложности
    if probability <= 100:
        level = "Очень легко"
        time_estimate = probability / 200000  # секунд при 200k addr/s
    elif probability <= 10000:
        level = "Легко"  
        time_estimate = probability / 150000
    elif probability <= 1000000:
        level = "Средне"
        time_estimate = probability / 100000
    elif probability <= 100000000:
        level = "Сложно"
        time_estimate = probability / 80000
    elif probability <= 10000000000:
        level = "Очень сложно"
        time_estimate = probability / 50000
    else:
        level = "Экстремально сложно"
        time_estimate = probability / 30000
    
    return level, probability, time_estimate

def get_currency_alphabet_info(currency: str) -> Tuple[int, str]:
    """
    Получить информацию об алфавите для валюты
    
    Args:
        currency: Тип криптовалюты
        
    Returns:
        Tuple[int, str]: (размер_алфавита, тип_кодирования)
    """
    if currency in ['BTC', 'LTC', 'DOGE', 'TRX']:
        return 58, "Base58"
    elif currency in ['ETH', 'BSC', 'MATIC', 'ARB', 'OP']:
        return 16, "Hex"
    else:
        return 58, "Base58"  # По умолчанию

def is_evm_currency(currency: str) -> bool:
    """
    Проверить, является ли валюта EVM-совместимой
    
    Args:
        currency: Тип криптовалюты
        
    Returns:
        bool: True если EVM-совместимая
    """
    return currency in ['ETH', 'BSC', 'MATIC', 'ARB', 'OP']
