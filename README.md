# 🚀 Multi-Crypto Vanity Address Generat## 🚀 Быстрый старт

### Предварительные требования

- **Python 3.12+** (проверьте: `python --version`)
- Git (для клонирования репозитория)

### Установка зависимостей

```bash
# Клонируем репозиторий
git clone https://github.com/maciborka/crypto-vanity-generator-.git
cd crypto-vanity-generator-

# Устанавливаем зависимости
pip install -r requirements.txt
```Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/maciborka/crypto-vanity-generator-/blob/main/LICENSE)
[![Crypto](https://img.shields.io/badge/Crypto-9%20currencies-orange.svg)](https://github.com/maciborka/crypto-vanity-generator-)
[![Performance](https://img.shields.io/badge/Performance-High-red.svg)](https://github.com/maciborka/crypto-vanity-generator-)
[![GitHub stars](https://img.shields.io/github/stars/maciborka/crypto-vanity-generator-.svg?style=social&label=Star)](https://github.com/maciborka/crypto-vanity-generator-)

Высокопроизводительный генератор vanity-адресов для криптовалют с поддержкой многопоточности и пакетной обработки.

## ✨ Особенности

- 🔥 **Максимальная производительность**: 100% загрузка всех CPU ядер
- 🎯 **9 криптовалют**: Bitcoin, Ethereum, Tron, Litecoin, Dogecoin + EVM сети (BSC, Polygon, Arbitrum, Optimism)
- 📦 **Пакетный режим**: автоматическая обработка множественных задач
- 🧠 **Оптимизация памяти**: адаптивный подход для больших объемов
- 💾 **CSV экспорт**: автоматическое сохранение результатов
- ⚙️ **Гибкая настройка**: конфигурация через файл или командную строку
- 🔗 **EVM совместимость**: поддержка всех популярных EVM сетей
- 🏗️ **Унифицированный код**: единая логика без дублирования

## 🎯 Поддерживаемые криптовалюты

### 💰 Основные сети
| Валюта | Тикер | Формат адреса | Пример |
|--------|-------|---------------|--------|
| Bitcoin | BTC | Base58 | `1VanityAddress...` |
| Litecoin | LTC | Base58 | `LVanity...` |
| Dogecoin | DOGE | Base58 | `DVanity...` |
| Ethereum | ETH | Hex | `0x1234...dead` |
| Tron | TRX | Base58 | `TCVanity...` |

### 🔗 EVM-совместимые сети (v1.1.0+)
| Сеть | Тикер | Формат адреса | Пример |
|------|-------|---------------|--------|
| Binance Smart Chain | BSC | Hex | `0xcafe...beef` |
| Polygon | MATIC | Hex | `0xabcd...1234` |
| Arbitrum | ARB | Hex | `0xdead...cafe` |
| Optimism | OP | Hex | `0x1337...beef` |

## � Быстрый старт

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Одиночная генерация

```bash
# Bitcoin с префиксом
python max_core_generator.py --currency BTC --prefix 1abc --count 1

# Ethereum с суффиксом  
python max_core_generator.py --currency ETH --suffix dead --count 5

# Новые EVM сети (v1.1.0+)
python max_core_generator.py --currency BSC --prefix cafe --count 3
python max_core_generator.py --currency MATIC --suffix 1337 --count 2  
python max_core_generator.py --currency ARB --prefix abc --count 1
python max_core_generator.py --currency OP --suffix beef --count 1
```

### Пакетная генерация

```bash
python batch_vanity_generator.py --config config.csv
```

## ⚙️ Конфигурация

### Конфигурационный файл `config.csv`:

```csv
# currency,pattern_type,pattern,count,ignore_case,priority
# Классические валюты
BTC,prefix,1cafe,5,true,1
ETH,suffix,dead,3,true,1
TRX,prefix,TC,10,false,1

# EVM-совместимые сети (v1.1.0+)
BSC,prefix,abc,2,true,1
MATIC,suffix,1337,1,false,2
ARB,prefix,cafe,1,true,2
OP,suffix,beef,1,true,2
```

**Параметры:**
- `currency`: BTC, ETH, TRX, LTC, DOGE, BSC, MATIC, ARB, OP
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
  --currency {BTC,ETH,TRX,LTC,DOGE,BSC,MATIC,ARB,OP}  Криптовалюта
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

## 🏗️ Архитектура проекта

### 📁 Структура файлов

```
📁 crypto-vanity-generator/
├── 🚀 max_core_generator.py         # Одиночный генератор
├── 🚀 batch_vanity_generator.py     # Пакетный генератор
├── 📁 core/
│   ├── __init__.py
│   └── pattern_matcher.py           # Общие функции поиска
├── 📁 networks/
│   ├── __init__.py
│   ├── base.py                      # Базовые классы
│   ├── bitcoin_like.py              # Bitcoin, Litecoin, Dogecoin
│   ├── ethereum.py                  # Ethereum
│   ├── tron.py                      # Tron
│   ├── evm_chains.py               # EVM-совместимые сети
│   └── optimized.py                # Оптимизированные версии
├── ⚙️ config.csv                    # Конфигурация
├── 📄 README.md
└── 📄 requirements.txt
```

### 🔧 Ключевые компоненты

- **🎯 `core/pattern_matcher.py`**: Унифицированная логика поиска паттернов
- **🔗 `networks/evm_chains.py`**: EVM-совместимые сети (BSC, Polygon, Arbitrum, Optimism)
- **⚡ `networks/optimized.py`**: Высокопроизводительные реализации
- **🚀 Генераторы**: Одиночный и пакетный режимы работы

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
- **Python 3.12+** (использует современные возможности типизации и производительности)
- Минимум 4 CPU ядра (рекомендуется 8+)
- 2+ GB RAM  
- 100+ MB свободного места

> 💡 **Почему Python 3.12+?** 
> - Улучшенная производительность многопоточности
> - Современная система типов для лучшей надежности кода
> - Оптимизированные структуры данных

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

```

---

## 📋 Changelog

### 🆕 v1.1.0 (Август 2025)
- **✨ Новое**: Добавлены 4 EVM-совместимые сети (BSC, Polygon, Arbitrum, Optimism)
- **🏗️ Архитектура**: Унифицированная логика в `core/pattern_matcher.py`
- **⚡ Производительность**: Правильная обработка EVM адресов (0x...)
- **🔧 API**: Расширены варианты `--currency` до 9 валют

### 🎯 v1.0.0 (Январь 2025)
- **🚀 Первый релиз**: Поддержка 5 криптовалют
- **💪 Производительность**: Максимальное использование всех CPU ядер
- **📦 Пакетный режим**: Обработка множественных задач
- **💾 Экспорт**: Автоматическое сохранение в CSV

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
