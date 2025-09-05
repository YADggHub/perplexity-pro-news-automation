# 📦 Подробная инструкция по установке

## 📋 Содержание

1. [Системные требования](#системные-требования)
2. [Подготовка учетных данных](#подготовка-учетных-данных)
3. [Способы установки](#способы-установки)
   - [Docker (рекомендуется)](#docker-установка)
   - [Локальная установка](#локальная-установка)
   - [Установка на VPS](#установка-на-vps)
4. [Настройка конфигурации](#настройка-конфигурации)
5. [Первый запуск](#первый-запуск)
6. [Проверка работоспособности](#проверка-работоспособности)
7. [Устранение проблем](#устранение-проблем)

## 🖥️ Системные требования

### Минимальные требования
- **ОС**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+
- **RAM**: 2GB (рекомендуется 4GB)
- **Диск**: 5GB свободного места
- **Интернет**: стабильное соединение 10+ Mbps
- **Python**: версия 3.11 или выше

### Рекомендуемые для продакшена
- **ОС**: Ubuntu Server 22.04 LTS
- **RAM**: 8GB
- **CPU**: 2+ ядра
- **Диск**: 20GB SSD
- **Интернет**: выделенный канал

### Браузерные требования
- **Google Chrome**: последняя стабильная версия
- **ChromeDriver**: автоматически устанавливается
- **Дисплей**: может работать в headless режиме

## 🔑 Подготовка учетных данных

### 1. Perplexity Pro подписка

1. **Регистрация аккаунта**:
   ```
   1. Перейдите на https://perplexity.ai
   2. Нажмите "Sign Up" в правом верхнем углу
   3. Зарегистрируйтесь через email или Google
   4. Подтвердите email адрес
   ```

2. **Оформление подписки**:
   ```
   1. Войдите в аккаунт Perplexity
   2. Нажмите "Upgrade to Pro" 
   3. Выберите план "Pro" ($20/месяц)
   4. Оплатите подписку банковской картой
   5. Подтвердите активацию Pro функций
   ```

3. **Проверка лимитов**:
   ```
   1. В интерфейсе Perplexity найдите счетчик запросов
   2. Убедитесь, что отображается "300 Pro searches today"
   3. Проверьте доступ к различным ИИ моделям
   ```

### 2. Telegram Bot

1. **Создание бота**:
   ```
   1. Найдите @BotFather в Telegram
   2. Отправьте команду /start
   3. Отправьте команду /newbot
   4. Введите имя бота (например: "News Automation Bot")
   5. Введите username бота (например: "news_automation_bot")
   6. Скопируйте полученный токен (формат: 1234567890:ABC...)
   ```

2. **Создание каналов**:
   ```
   1. Создайте новые каналы в Telegram:
      - @your_it_news (для IT новостей)
      - @your_automation_news (для автоматизации)
      - @your_robotics_news (для робототехники)
   
   2. Для каждого канала:
      - Перейдите в настройки канала
      - Выберите "Administrators" 
      - Добавьте созданного бота как администратора
      - Дайте права "Post Messages"
   ```

3. **Получение Chat ID каналов**:
   ```
   1. Добавьте бота @userinfobot в каналы
   2. Перешлите любое сообщение из канала боту
   3. Скопируйте полученный Chat ID (начинается с -100)
   4. Удалите @userinfobot из каналов
   ```

## 📦 Способы установки

### 🐳 Docker установка (рекомендуется)

#### Ubuntu/Debian:
```bash
# 1. Установка Docker
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 2. Добавление пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker

# 3. Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Проверка установки
docker --version
docker-compose --version
```

#### macOS:
```bash
# 1. Установка через Homebrew
brew install --cask docker

# 2. Запуск Docker Desktop
open -a Docker

# 3. Установка Docker Compose
brew install docker-compose

# 4. Проверка
docker --version
docker-compose --version
```

#### Windows:
```powershell
# 1. Скачайте Docker Desktop с https://www.docker.com/products/docker-desktop
# 2. Запустите установщик и следуйте инструкциям
# 3. Перезагрузите компьютер
# 4. Запустите Docker Desktop
# 5. Проверьте в PowerShell:
docker --version
docker-compose --version
```

#### Установка проекта:
```bash
# 1. Клонирование репозитория
git clone https://github.com/your-repo/perplexity-pro-news-automation
cd perplexity-pro-news-automation

# 2. Настройка конфигурации
cp .env.example .env

# Отредактируйте .env файл:
# Linux/Mac:
nano .env
# Windows:
notepad .env

# 3. Запуск системы
docker-compose up -d

# 4. Проверка запуска
docker-compose ps
docker-compose logs -f perplexity-news-bot
```

### 💻 Локальная установка

#### Ubuntu/Debian:
```bash
# 1. Обновление системы
sudo apt update && sudo apt upgrade -y

# 2. Установка Python 3.11
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# 3. Установка Google Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# 4. Установка дополнительных пакетов
sudo apt install -y git curl wget unzip

# 5. Клонирование проекта
git clone https://github.com/your-repo/perplexity-pro-news-automation
cd perplexity-pro-news-automation

# 6. Создание виртуального окружения
python3.11 -m venv venv
source venv/bin/activate

# 7. Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt

# 8. Настройка конфигурации
cp .env.example .env
nano .env

# 9. Запуск системы
python src/main.py
```

#### macOS:
```bash
# 1. Установка Homebrew (если не установлен)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Установка Python
brew install python@3.11

# 3. Установка Google Chrome
brew install --cask google-chrome

# 4. Клонирование проекта
git clone https://github.com/your-repo/perplexity-pro-news-automation
cd perplexity-pro-news-automation

# 5. Создание виртуального окружения
python3.11 -m venv venv
source venv/bin/activate

# 6. Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt

# 7. Настройка конфигурации
cp .env.example .env
nano .env

# 8. Запуск системы
python src/main.py
```

#### Windows:
```powershell
# 1. Установка Python 3.11
# Скачайте с https://python.org/downloads/
# Выберите "Add Python to PATH" при установке

# 2. Установка Google Chrome
# Скачайте с https://www.google.com/chrome/

# 3. Установка Git
# Скачайте с https://git-scm.com/downloads

# 4. Клонирование проекта (в PowerShell)
git clone https://github.com/your-repo/perplexity-pro-news-automation
cd perplexity-pro-news-automation

# 5. Создание виртуального окружения
python -m venv venv
venv\Scripts\activate

# 6. Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt

# 7. Настройка конфигурации
copy .env.example .env
notepad .env

# 8. Запуск системы
python src/main.py
```

### 🌐 Установка на VPS

#### Выбор провайдера VPS:
**Рекомендуемые провайдеры:**
- **DigitalOcean**: от $5/месяц (1GB RAM, 1 CPU)
- **Vultr**: от $3.50/месяц (512MB RAM, 1 CPU)  
- **Linode**: от $5/месяц (1GB RAM, 1 CPU)
- **Hetzner**: от €3.79/месяц (2GB RAM, 1 CPU)

#### Установка на Ubuntu Server:
```bash
# 1. Подключение к VPS
ssh root@your-vps-ip

# 2. Обновление системы
apt update && apt upgrade -y

# 3. Создание пользователя
adduser newsbot
usermod -aG sudo newsbot
su - newsbot

# 4. Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# 5. Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 6. Клонирование проекта
git clone https://github.com/your-repo/perplexity-pro-news-automation
cd perplexity-pro-news-automation

# 7. Настройка конфигурации
cp .env.example .env
nano .env

# 8. Запуск системы
docker-compose up -d

# 9. Настройка автозапуска
sudo crontab -e
# Добавьте строку:
@reboot /usr/local/bin/docker-compose -f /home/newsbot/perplexity-pro-news-automation/docker-compose.yml up -d

# 10. Настройка файрвола
sudo ufw allow 22
sudo ufw allow 8080
sudo ufw --force enable
```

## ⚙️ Настройка конфигурации

### Основной .env файл:
```env
# =============================================================================
# PERPLEXITY PRO НАСТРОЙКИ
# =============================================================================
PERPLEXITY_EMAIL=your-email@example.com
PERPLEXITY_PASSWORD=your-secure-password

# =============================================================================
# TELEGRAM BOT НАСТРОЙКИ  
# =============================================================================
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TG_IT_CHANNEL=-1001234567890
TG_AUTOMATION_CHANNEL=-1001234567891
TG_ROBOTICS_CHANNEL=-1001234567892

# =============================================================================
# СИСТЕМА НАСТРОЙКИ
# =============================================================================
MAX_DAILY_QUERIES=50
MIN_IMPORTANCE_TO_PUBLISH=6
LOG_LEVEL=INFO
DATABASE_PATH=data/perplexity_news.db

# =============================================================================
# ПЛАНИРОВЩИК НАСТРОЙКИ
# =============================================================================
MORNING_SESSION_TIME=09:00
MORNING_SESSION_QUERIES=8
MORNING_SESSION_POSTS=3

AFTERNOON_SESSION_TIME=13:00
AFTERNOON_SESSION_QUERIES=10
AFTERNOON_SESSION_POSTS=4

EVENING_SESSION_TIME=18:00
EVENING_SESSION_QUERIES=12
EVENING_SESSION_POSTS=5

NIGHT_SESSION_TIME=22:00
NIGHT_SESSION_QUERIES=8
NIGHT_SESSION_POSTS=3

# =============================================================================
# БРАУЗЕР НАСТРОЙКИ
# =============================================================================
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=30
BROWSER_WINDOW_SIZE=1920,1080
BROWSER_USER_AGENT=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36

# =============================================================================
# РАСШИРЕННЫЕ НАСТРОЙКИ
# =============================================================================
# Retry настройки
MAX_RETRY_ATTEMPTS=3
RETRY_DELAY_SECONDS=5

# Rate limiting
REQUESTS_PER_MINUTE=2
TELEGRAM_RATE_LIMIT=30

# Мониторинг
HEALTH_CHECK_INTERVAL=300
METRICS_RETENTION_DAYS=30

# Backup
AUTO_BACKUP_ENABLED=true
BACKUP_INTERVAL_HOURS=24
BACKUP_RETENTION_DAYS=7
```

### Проверка конфигурации:
```bash
# Проверка обязательных параметров
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required_vars = [
    'PERPLEXITY_EMAIL', 'PERPLEXITY_PASSWORD',
    'TELEGRAM_BOT_TOKEN', 'TG_IT_CHANNEL'
]

missing = []
for var in required_vars:
    if not os.getenv(var):
        missing.append(var)

if missing:
    print(f'❌ Отсутствуют обязательные переменные: {missing}')
    exit(1)
else:
    print('✅ Все обязательные переменные настроены')
"
```

## 🚀 Первый запуск

### Проверка готовности:
```bash
# 1. Проверка Docker контейнеров
docker-compose ps

# Ожидаемый вывод:
# Name                    Command               State           Ports
# perplexity-news-bot     python src/main.py              Up
# perplexity-dashboard    nginx -g daemon off;            Up      0.0.0.0:8080->80/tcp

# 2. Проверка логов
docker-compose logs perplexity-news-bot

# 3. Проверка веб-интерфейса
curl http://localhost:8080/health
```

### Тестовый запуск:
```bash
# 1. Запуск одного запроса вручную
docker-compose exec perplexity-news-bot python -c "
import asyncio
from src.main import NewsAutomationSystem

async def test_query():
    system = NewsAutomationSystem()
    post = await system.create_news_post_from_query(
        'Последние новости искусственного интеллекта за сегодня'
    )
    if post:
        print(f'✅ Пост создан: {post.title}')
        print(f'Важность: {post.importance}/10')
        print(f'Категория: {post.category}')
    else:
        print('❌ Не удалось создать пост')

asyncio.run(test_query())
"

# 2. Тестовая публикация в Telegram
docker-compose exec perplexity-news-bot python -c "
import asyncio
from telegram import Bot
import os

async def test_telegram():
    bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
    try:
        await bot.send_message(
            chat_id=os.getenv('TG_IT_CHANNEL'),
            text='🧪 Тестовое сообщение от системы автоматизации новостей'
        )
        print('✅ Telegram бот работает')
    except Exception as e:
        print(f'❌ Ошибка Telegram: {e}')

asyncio.run(test_telegram())
"
```

## ✅ Проверка работоспособности

### Веб-интерфейс:
1. Откройте http://localhost:8080
2. Проверьте Dashboard:
   - ✅ Статус системы: "Активна"
   - ✅ Запросы Perplexity: "X/300 сегодня"
   - ✅ Посты созданы: "X сегодня"

### Системные проверки:
```bash
# 1. Проверка базы данных
docker-compose exec perplexity-news-bot sqlite3 data/perplexity_news.db "
SELECT 
    COUNT(*) as total_queries,
    COUNT(CASE WHEN success = 1 THEN 1 END) as successful_queries
FROM perplexity_queries;
"

# 2. Проверка планировщика
docker-compose logs perplexity-news-bot | grep -i "session"

# 3. Проверка использования ресурсов
docker stats perplexity-news-bot

# 4. Проверка файловой системы
du -sh data/
ls -la logs/
```

### Проверка каналов Telegram:
1. Зайдите в каждый из настроенных каналов
2. Убедитесь, что бот добавлен как администратор
3. Проверьте права бота: "Post Messages" должно быть включено
4. Отправьте тестовое сообщение через веб-интерфейс

## 🔧 Устранение проблем

### Perplexity не отвечает:
```bash
# 1. Проверьте учетные данные
echo "Email: $PERPLEXITY_EMAIL"
echo "Password: ***"

# 2. Увеличьте timeout
# В .env файле:
BROWSER_TIMEOUT=45

# 3. Перезапустите контейнер
docker-compose restart perplexity-news-bot

# 4. Проверьте логи
docker-compose logs perplexity-news-bot | grep -i "perplexity"
```

### Ошибки Telegram:
```bash
# 1. Проверьте токен бота
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"

# 2. Проверьте права в канале
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getChatMember?chat_id=$TG_IT_CHANNEL&user_id=BOT_USER_ID"

# 3. Тестовое сообщение
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
     -H "Content-Type: application/json" \
     -d "{\"chat_id\":\"$TG_IT_CHANNEL\",\"text\":\"Test message\"}"
```

### Chrome/Selenium проблемы:
```bash
# 1. Обновление Chrome в контейнере
docker-compose exec perplexity-news-bot apt update
docker-compose exec perplexity-news-bot apt install -y --only-upgrade google-chrome-stable

# 2. Проверка ChromeDriver
docker-compose exec perplexity-news-bot chromedriver --version

# 3. Тестовый запуск браузера
docker-compose exec perplexity-news-bot python -c "
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

try:
    driver = webdriver.Chrome(options=options)
    driver.get('https://google.com')
    print('✅ Chrome работает')
    driver.quit()
except Exception as e:
    print(f'❌ Ошибка Chrome: {e}')
"
```

### Проблемы с ресурсами:
```bash
# 1. Мониторинг использования
docker stats --no-stream

# 2. Очистка логов
docker-compose exec perplexity-news-bot truncate -s 0 logs/perplexity_news.log

# 3. Очистка базы данных (старые записи)
docker-compose exec perplexity-news-bot sqlite3 data/perplexity_news.db "
DELETE FROM perplexity_queries WHERE timestamp < datetime('now', '-7 days');
VACUUM;
"

# 4. Перезапуск с ограничением памяти
docker-compose stop
docker-compose up -d --memory=1g
```

## 📞 Поддержка

Если проблему не удается решить:

1. **Проверьте логи**: `docker-compose logs -f perplexity-news-bot`
2. **Откройте Issue**: [GitHub Issues](https://github.com/your-repo/issues)
3. **Приложите информацию**:
   - Версия системы: `cat VERSION`
   - Конфигурация: `env | grep -E "(PERPLEXITY|TELEGRAM)" | sed 's/PASSWORD=.*/PASSWORD=***/'`
   - Логи ошибок: последние 50 строк из логов
   - Операционная система: `uname -a`

**🎉 Поздравляем! Система автоматизации новостей готова к работе!**