# 🚀 Multi-Crypto Vanity Address Generator

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/maciborka/crypto-vanity-generator-/blob/main/LICENSE)
[![Crypto](https://img.shields.io/badge/Crypto-5%20currencies-orange.svg)](https://github.com/maciborka/crypto-vanity-generator-)
[![Performance](https://img.shields.io/badge/Performance-High-red.svg)](https://github.com/maciborka/crypto-vanity-generator-)
[![GitHub stars](https://img.shields.io/github/stars/maciborka/crypto-vanity-generator-.svg?style=social&label=Star)](https://github.com/maciborka/crypto-vanity-generator-)

Высокопроизводительный генератор vanity-адресов для криптовалют с поддержкой многопоточности и пакетной обработки.

## ✨ Особенности

- 🔥 **Максимальная производительность**: 100% загрузка всех CPU ядер
- 🎯 **5 криптовалют**: Bitcoin, Ethereum, Tron, Litecoin, Dogecoin
- 📦 **Пакетный режим**: автоматическая обработка множественных задач
- 🧠 **Оптимизация памяти**: адаптивный подход для больших объемов
- 💾 **CSV экспорт**: автоматическое сохранение результатов
- ⚙️ **Гибкая настройка**: конфигурация через файл или командную строку

## 🎯 Поддерживаемые криптовалюты

| Валюта | Тикер | Примеры адресов |
|--------|-------|----------------|
| Bitcoin | BTC | `1VanityAddress...` |
| Ethereum | ETH | `0x1234...dead` |
| Tron | TRX | `TCVanity...` |
| Litecoin | LTC | `LVanity...` |
| Dogecoin | DOGE | `DVanity...` |

## � Быстрый старт

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Одиночная генерация

```bash
python max_core_generator.py --currency BTC --prefix 1abc --count 1
```

### Пакетная генерация

```bash
python batch_vanity_generator.py --config config.csv
```

## ⚙️ Конфигурация

### Конфигурационный файл `config.csv`:

```csv
# currency,pattern_type,pattern,count,ignore_case,priority
TRX,prefix,TC,12,false,1
BTC,prefix,1c,100,true,1  
ETH,suffix,dead,1,true,1
```

**Параметры:**
- `currency`: BTC, ETH, TRX, LTC, DOGE
- `pattern_type`: prefix, suffix
- `pattern`: искомый паттерн
- `count`: количество адресов (0 = бесконечно)
- `ignore_case`: true/false
- `priority`: 1-5 (1=высший приоритет)

### Командная строка

#### Одиночный генератор (`max_core_generator.py`)

```bash
python max_core_generator.py [OPTIONS]

Опции:
  --currency {BTC,ETH,TRX,LTC,DOGE}  Криптовалюта
  --prefix TEXT                      Префикс адреса
  --suffix TEXT                      Суффикс адреса  
  --count INTEGER                    Количество адресов
  --ignore-case                      Игнорировать регистр
  --workers INTEGER                  Количество воркеров
```

#### Пакетный генератор (`batch_vanity_generator.py`)

```bash
python batch_vanity_generator.py [OPTIONS]

Опции:
  --config PATH                      Путь к конфигурационному файлу
  --workers INTEGER                  Количество воркеров
  --single                          Режим одиночной задачи
```

## � Примеры использования

### 1. Простой Bitcoin адрес

```bash
python max_core_generator.py --currency BTC --prefix 1abc --count 5
```

### 2. Ethereum адрес с суффиксом

```bash
python max_core_generator.py --currency ETH --suffix dead --count 1 --ignore-case
```

### 3. Пакетная обработка

Создайте `config.csv`:
```csv
BTC,prefix,1test,10,true,1
ETH,suffix,cafe,5,true,2  
TRX,prefix,TC,20,false,1
```

Запустите:
```bash
python batch_vanity_generator.py --config config.csv
```

## 🧠 Оптимизация производительности

### Адаптивные алгоритмы

- **Малые задачи (count ≤ 10)**: Простой режим без оптимизации памяти
- **Большие задачи (count > 10)**: Batch-режим с потоковым сохранением
- **Бесконечный поиск (count = 0)**: Полная оптимизация памяти

### Производительность

| Криптовалюта | Скорость (адр/с) | Сложность |
|--------------|------------------|-----------|
| Bitcoin | ~10,000 | Средняя |
| Ethereum | ~25,000 | Низкая |
| Tron | ~1,500 | Высокая |
| Litecoin | ~12,000 | Средняя |
| Dogecoin | ~8,000 | Средняя |

*Производительность зависит от сложности паттерна и железа*

## 📁 Структура проекта

```
├── README.md                    # Документация
├── requirements.txt            # Зависимости
├── config.csv                 # Конфигурация пакетной обработки
├── max_core_generator.py      # Одиночный генератор
├── batch_vanity_generator.py  # Пакетный генератор
├── networks/                  # Модули криптовалют
│   ├── __init__.py
│   ├── base.py               # Базовый класс
│   ├── bitcoin_like.py       # BTC, LTC, DOGE
│   ├── ethereum.py           # ETH
│   ├── tron.py              # TRX
│   └── optimized.py         # Оптимизированные алгоритмы
└── CSV/                     # Результаты (создается автоматически)
```

## 🔒 Безопасность

⚠️ **ВНИМАНИЕ**: Этот инструмент предназначен только для образовательных и исследовательских целей.

- Сгенерированные приватные ключи полностью случайны
- Не используйте на production без дополнительной проверки
- Храните приватные ключи в безопасности
- Автор не несет ответственности за потерю средств

## 🛠️ Технические детали

### Архитектура
- **Многопроцессинг**: ProcessPoolExecutor для максимального использования CPU
- **Модульность**: Отдельные модули для каждой криптовалюты
- **Оптимизация**: Batch-сохранение и управление памятью

### Зависимости
- `web3`: Для работы с Ethereum
- `eth-account`: Генерация Ethereum ключей  
- `secp256k1`: Криптографические операции
- `base58`: Кодирование адресов

### Системные требования
- Python 3.8+
- Минимум 4 CPU ядра (рекомендуется 8+)
- 2+ GB RAM
- 100+ MB свободного места

## ❓ FAQ

**Q: Какова вероятность найти паттерн?**
A: Зависит от длины и сложности. 4 символа = ~1/1М попыток, 5 символов = ~1/60М

**Q: Можно ли остановить поиск?**
A: Да, нажмите Ctrl+C для корректного завершения

**Q: Где сохраняются результаты?**
A: В папке `CSV/` в формате `{Currency}_{Pattern}_{Timestamp}.csv`

## 📞 Поддержка

- 🐛 [Сообщить о багах](https://github.com/maciborka/crypto-vanity-generator-/issues)
- 💡 [Предложить улучшения](https://github.com/maciborka/crypto-vanity-generator-/discussions)
- 📧 [Email](mailto:maciborka@gmail.com)
- 💬 [Telegram: @it_world_com_ua](https://t.me/it_world_com_ua)
- 👤 [GitHub: @maciborka](https://github.com/maciborka)

---
⭐ **Понравился проект? Поставьте звезду!** ⭐

---

<div align="center">

**🚀 Создано [@maciborka](https://github.com/maciborka)**

💬 [Telegram: @it_world_com_ua](https://t.me/it_world_com_ua) | 📧 [maciborka@gmail.com](mailto:maciborka@gmail.com)

*High-performance crypto vanity address generation for the blockchain era*

</div>

# Быстрый поиск
python3 max_core_generator.py --currency TRX --prefix TC --count 1

# Пакетный поиск  
python3 batch_vanity_generator.py --config config.csv
```

---

**Генератор готов к работе! 🚀**
