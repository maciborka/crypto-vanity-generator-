# 🚀 Примеры использования Multi-Crypto Vanity Generator

Этот файл содержит готовые команды для быстрого старта с генератором.

## 📋 Быстрые примеры

### Bitcoin (BTC)

```bash
# Простой префикс
python max_core_generator.py --currency BTC --prefix 1abc --count 1

# Игнорирование регистра
python max_core_generator.py --currency BTC --prefix 1CAFE --count 5 --ignore-case

# Множественная генерация
python max_core_generator.py --currency BTC --prefix 1test --count 10
```

### Ethereum (ETH)

```bash
# Суффикс адреса
python max_core_generator.py --currency ETH --suffix dead --count 1 --ignore-case

# Префикс после 0x
python max_core_generator.py --currency ETH --prefix 1234 --count 3

# Красивый адрес
python max_core_generator.py --currency ETH --suffix cafe --count 1
```

### Tron (TRX)

```bash
# Стандартный Tron префикс
python max_core_generator.py --currency TRX --prefix TC --count 5

# Длинный префикс (займет больше времени)
python max_core_generator.py --currency TRX --prefix TRON --count 1 --ignore-case
```

### Litecoin (LTC)

```bash
# Префикс для Litecoin
python max_core_generator.py --currency LTC --prefix Lite --count 1 --ignore-case

# Суффикс
python max_core_generator.py --currency LTC --suffix coin --count 3 --ignore-case
```

### Dogecoin (DOGE)

```bash
# Классический Dogecoin
python max_core_generator.py --currency DOGE --prefix Doge --count 1 --ignore-case

# Мем адрес
python max_core_generator.py --currency DOGE --suffix wow --count 1 --ignore-case
```

## 📦 Пакетная обработка

### Простой config.csv

```csv
# currency,pattern_type,pattern,count,ignore_case,priority
BTC,prefix,1test,5,true,1
ETH,suffix,dead,2,true,1
TRX,prefix,TC,3,false,1
```

```bash
python batch_vanity_generator.py --config config.csv
```

### Продвинутый config.csv

```csv
# Быстрые задачи
BTC,prefix,1,10,false,1
ETH,prefix,123,5,true,1

# Средние задачи  
TRX,prefix,TRON,1,true,2
LTC,prefix,Lite,2,true,2

# Сложные задачи (низкий приоритет)
DOGE,suffix,much,1,true,3
ETH,suffix,cafe,1,true,3
```

## ⚡ Оптимизация производительности

### Настройка количества воркеров

```bash
# Использовать все CPU ядра (по умолчанию)
python max_core_generator.py --currency BTC --prefix 1abc --count 1

# Ограничить количество воркеров
python max_core_generator.py --currency BTC --prefix 1abc --count 1 --workers 4

# Максимальная производительность
python batch_vanity_generator.py --config config.csv --workers 16
```

### Сложность паттернов

```bash
# БЫСТРО (секунды)
python max_core_generator.py --currency BTC --prefix 1 --count 10

# СРЕДНЕ (минуты)  
python max_core_generator.py --currency BTC --prefix 1abc --count 1

# МЕДЛЕННО (часы)
python max_core_generator.py --currency BTC --prefix 1abcd --count 1

# ОЧЕНЬ МЕДЛЕННО (дни)
python max_core_generator.py --currency BTC --prefix 1abcde --count 1
```

## 🎯 Специальные случаи

### Бесконечный поиск

```bash
# Искать пока не остановите (Ctrl+C)
python max_core_generator.py --currency BTC --prefix 1abc --count 0
```

### Только суффиксы

```bash
# Ethereum адреса с красивыми окончаниями
python max_core_generator.py --currency ETH --suffix dead --count 5 --ignore-case
python max_core_generator.py --currency ETH --suffix beef --count 3 --ignore-case
python max_core_generator.py --currency ETH --suffix cafe --count 2 --ignore-case
```

### Комбинированный поиск через config

```csv
# Поиск и префиксов, и суффиксов
ETH,prefix,1234,3,true,1
ETH,suffix,dead,3,true,1
ETH,prefix,abcd,2,true,2
ETH,suffix,beef,2,true,2
```

## 📊 Примеры production config

### Для майнинг пула

```csv
# currency,pattern_type,pattern,count,ignore_case,priority
BTC,prefix,1Pool,10,true,1
ETH,prefix,Pool,20,true,1
TRX,prefix,TPool,15,false,1
```

### Для биржи

```csv
# currency,pattern_type,pattern,count,ignore_case,priority  
BTC,prefix,1Exch,50,true,1
ETH,prefix,Exch,100,true,1
TRX,prefix,TExch,30,false,1
LTC,prefix,LExch,25,true,2
DOGE,prefix,DExch,20,true,2
```

### Для персональных кошельков

```csv
# currency,pattern_type,pattern,count,ignore_case,priority
BTC,prefix,1My,5,true,1
ETH,suffix,my,5,true,1
TRX,prefix,TMy,3,false,1
```

## 🎨 Креативные паттерны

```bash
# Год рождения
python max_core_generator.py --currency BTC --prefix 1990 --count 1

# Имя
python max_core_generator.py --currency ETH --prefix Alex --count 1 --ignore-case

# Любимое число
python max_core_generator.py --currency TRX --suffix 777 --count 1

# Компания
python max_core_generator.py --currency LTC --prefix Corp --count 1 --ignore-case

# Мем
python max_core_generator.py --currency DOGE --suffix moon --count 1 --ignore-case
```

## ⚠️ Важные заметки

1. **Сложность растет экспоненциально** с длиной паттерна
2. **Регистр имеет значение** без флага `--ignore-case`
3. **CSV файлы содержат приватные ключи** - храните их безопасно
4. **Ctrl+C** для безопасного завершения поиска
5. **Результаты сохраняются** в папку `CSV/`

## 📈 Оценка времени

| Длина паттерна | Время поиска | Пример |
|----------------|--------------|--------|
| 1 символ       | Секунды      | `1a` |
| 2 символа      | Секунды      | `1ab` |  
| 3 символа      | Минуты       | `1abc` |
| 4 символа      | Часы         | `1abcd` |
| 5+ символов    | Дни/недели   | `1abcde` |

---
🎯 **Совет**: Начните с коротких паттернов для тестирования, затем увеличивайте сложность!

---

**👤 Автор**: [@maciborka](https://github.com/maciborka)  
**💬 Контакт**: [Telegram @it_world_com_ua](https://t.me/it_world_com_ua) | [maciborka@gmail.com](mailto:maciborka@gmail.com)
