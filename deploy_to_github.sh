#!/bin/bash
# Скрипт для первоначальной загрузки проекта на GitHub

echo "🚀 Подготовка проекта crypto-vanity-generator для GitHub..."

# Настройка Git конфигурации
echo "⚙️ Настройка Git конфигурации..."
git config --global user.name "maciborka"
git config --global user.email "maciborka@gmail.com"

# Проверяем, что мы в правильной директории
if [ ! -f "max_core_generator.py" ]; then
    echo "❌ Ошибка: Запустите скрипт из корневой директории проекта"
    exit 1
fi

# Инициализация Git (если еще не сделано)
if [ ! -d ".git" ]; then
    echo "📝 Инициализация Git репозитория..."
    git init
fi

# Добавление всех файлов
echo "📦 Добавление файлов..."
git add .

# Проверяем статус
echo "📊 Статус репозитория:"
git status

# Коммит
echo "💾 Создание первого коммита..."
git commit -m "🚀 Initial release: Multi-Crypto Vanity Address Generator v1.0.0

✨ Features:
- 🎯 Support for 5 cryptocurrencies (BTC, ETH, TRX, LTC, DOGE)
- 🔥 Maximum CPU utilization with multiprocessing
- 📦 Batch processing with CSV configuration
- 🧠 Adaptive memory optimization
- 💾 Automatic CSV export
- ⚙️ Flexible command-line interface
- 🎨 Prefix and suffix pattern support
- 🔤 Case-insensitive search option
- 📊 Priority system for tasks
- ⏱️ Smart time estimation
- 🛡️ Graceful shutdown with Ctrl+C
- 📈 Detailed performance statistics

🛠️ Technical:
- Python 3.8+ support
- Modular architecture
- Optimized algorithms
- Memory management
- Cross-platform compatibility

📚 Documentation:
- Comprehensive README with examples
- Security guidelines
- Changelog and versioning
- GitHub templates and workflows"

# Установка origin (если еще не установлен)
if ! git remote | grep -q origin; then
    echo "🔗 Добавление remote origin..."
    git remote add origin https://github.com/maciborka/crypto-vanity-generator-.git
fi

# Создание основной ветки
echo "🌿 Создание main ветки..."
git branch -M main

# Загрузка на GitHub
echo "📤 Загрузка на GitHub..."
echo "⚠️  Убедитесь, что репозиторий создан на GitHub: https://github.com/maciborka/crypto-vanity-generator-"
echo "🔑 Вам может потребоваться аутентификация..."

read -p "Продолжить загрузку? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push -u origin main
    echo "✅ Проект успешно загружен на GitHub!"
    echo "🌟 Не забудьте:"
    echo "   1. Добавить topics в настройках репозитория"
    echo "   2. Включить Discussions и Issues"
    echo "   3. Проверить, что все файлы загружены"
    echo "   4. Добавить описание репозитория"
    echo ""
    echo "🔗 Ваш репозиторий: https://github.com/maciborka/crypto-vanity-generator-"
else
    echo "⏸️  Загрузка отменена. Выполните 'git push -u origin main' когда будете готовы."
fi

echo "🎉 Готово!"
