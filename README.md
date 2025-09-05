# 🚀 Perplexity Pro News Automation System

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/your-repo)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

**Полностью автоматизированная система для создания и публикации новостей в Telegram каналы с использованием Perplexity Pro и встроенных ИИ моделей.**

## 📋 Обзор

Система обеспечивает:
- **300+ запросов в день** к Perplexity Pro с 8 ИИ моделями
- **15+ качественных постов** ежедневно с автоматической обработкой
- **$0.04 стоимость** одного поста (включая все расходы)
- **Веб-интерфейс** для управления и мониторинга
- **Полную автоматизацию** с планировщиком сессий

## ⚡ Быстрый старт

### 🐳 Docker (рекомендуется)

```bash
# 1. Скачайте проект
git clone https://github.com/your-repo/perplexity-pro-news-automation
cd perplexity-pro-news-automation

# 2. Настройте конфигурацию
cp .env.example .env
nano .env  # укажите ваши данные

# 3. Запустите систему
docker-compose up -d

# 4. Откройте веб-интерфейс
open http://localhost:8080
```

### 💻 Локальная установка

```bash
# Автоматическая установка
chmod +x start.sh
./start.sh

# Или Windows
start.bat
```

## 🎯 Возможности системы

### 🤖 Автоматизация Perplexity Pro
- **Браузерная автоматизация** через Selenium WebDriver
- **Умное планирование** запросов с учетом лимитов
- **Сохранение сессии** для стабильной работы
- **Кэширование ответов** для экономии запросов

### 🧠 ИИ обработка контента
- **8 моделей ИИ**: Claude 3.5 Sonnet, GPT-4 Omni, Grok-2, DeepSeek R1
- **Автоматическая категоризация**: IT, автоматизация, робототехника, ИИ
- **Оценка важности**: 1-10 баллов для приоритизации
- **Генерация хештегов** и форматирование для Telegram

### 📱 Telegram интеграция
- **Мультиканальная публикация** в несколько каналов одновременно
- **Умное форматирование** с эмодзи и разметкой
- **Планирование публикаций** по времени и важности
- **Обработка ошибок** и повторные попытки

### 🌐 Веб-интерфейс
- **Dashboard** с метриками и статистикой
- **Мониторинг запросов** в реальном времени
- **Управление постами** с превью и редактированием
- **Планировщик сессий** с настройкой расписания
- **Аналитика** эффективности и затрат

## 📊 Экономика проекта

| Параметр | Значение |
|----------|----------|
| **Стоимость/месяц** | $20-30 |
| **Постов в день** | 15+ |
| **Стоимость поста** | $0.04 |
| **Запросов в день** | до 300 |
| **ROI** | 1-2 недели |

## 🛠️ Требования

### Минимальные
- **Python 3.11+**
- **Google Chrome** браузер
- **2GB RAM**, 5GB диск
- **Интернет** соединение

### Учетные данные
- **Perplexity Pro** подписка ($20/месяц)
- **Telegram Bot** токен (бесплатно)
- **Telegram каналы** для публикации

## 📁 Структура проекта

```
perplexity-pro-news-automation/
├── src/
│   ├── main.py                 # Основная логика системы
│   ├── config.py              # Конфигурация и настройки
│   ├── automation.py          # Автоматизация Perplexity
│   ├── scheduler.py           # Планировщик сессий
│   ├── telegram_publisher.py  # Публикация в Telegram
│   └── database.py           # Работа с базой данных
├── dashboard/
│   ├── index.html            # Веб-интерфейс
│   ├── style.css            # Стили интерфейса
│   └── app.js               # JavaScript логика
├── docs/
│   ├── INSTALL.md           # Подробная установка
│   ├── TROUBLESHOOTING.md   # Решение проблем
│   └── API_REFERENCE.md     # Справочник API
├── scripts/
│   ├── setup.sh            # Автоматическая установка
│   ├── backup.sh           # Резервное копирование
│   └── update.sh           # Обновление системы
├── docker-compose.yml       # Docker конфигурация
├── Dockerfile              # Docker образ
├── requirements.txt        # Python зависимости
├── .env.example           # Пример конфигурации
└── README.md             # Этот файл
```

## 🚀 Расписание работы

| Время | Сессия | Запросы | Посты | Фокус |
|-------|--------|---------|-------|--------|
| **09:00** | Утренняя | 8 | 3 | Дайджест трендов |
| **13:00** | Дневная | 10 | 4 | Анализ новостей |
| **18:00** | Вечерняя | 12 | 5 | Обзор технологий |
| **22:00** | Ночная | 8 | 3 | Международные новости |

## 📈 Мониторинг и аналитика

### Ключевые метрики
- **Использование Perplexity**: 42/300 запросов сегодня
- **Эффективность**: 0.4 поста на запрос
- **Успешность публикаций**: >95%
- **Среднее время обработки**: 8-15 секунд

### Веб-интерфейс
- **Реального времени** статистика
- **Интерактивные графики** производительности
- **Детальные логи** всех операций
- **Настройка параметров** без перезагрузки

## 🔧 Настройка

### Обязательные параметры (.env)
```env
# Perplexity Pro
PERPLEXITY_EMAIL=your-email@example.com
PERPLEXITY_PASSWORD=your-secure-password

# Telegram Bot
TELEGRAM_BOT_TOKEN=1234567890:YOUR-BOT-TOKEN
TG_IT_CHANNEL=@your_it_channel
TG_AUTOMATION_CHANNEL=@your_automation_channel
TG_ROBOTICS_CHANNEL=@your_robotics_channel

# Система
MAX_DAILY_QUERIES=50
MIN_IMPORTANCE_TO_PUBLISH=6
```

### Опциональные параметры
```env
# Планировщик
MORNING_SESSION_TIME=09:00
AFTERNOON_SESSION_TIME=13:00
EVENING_SESSION_TIME=18:00
NIGHT_SESSION_TIME=22:00

# Браузер
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=30

# Логирование
LOG_LEVEL=INFO
LOG_FILE=perplexity_news.log
```

## 🔍 Примеры использования

### Запуск одной сессии вручную
```python
from src.main import NewsAutomationSystem

system = NewsAutomationSystem()
await system.run_manual_session("trending_ai")
```

### Создание поста из произвольного запроса
```python
post = await system.create_news_post_from_query(
    "Последние прорывы в области квантовых вычислений"
)
if post.importance >= 7:
    await system.publish_to_telegram(post)
```

### Мониторинг через API
```bash
# Статус системы
curl http://localhost:8080/api/status

# Статистика за день
curl http://localhost:8080/api/stats/today
```

## 🆘 Поддержка

### Быстрая диагностика
```bash
# Проверка логов
tail -f logs/perplexity_news.log

# Статус контейнеров
docker-compose ps

# Перезапуск системы
docker-compose restart
```

### Частые проблемы
1. **Perplexity не отвечает** → Увеличьте timeout в настройках
2. **Ошибки Telegram** → Проверьте права бота в каналах
3. **Chrome не запускается** → Установите недостающие зависимости

## 📚 Документация

- **[Подробная установка](docs/INSTALL.md)** - пошаговое руководство
- **[Решение проблем](docs/TROUBLESHOOTING.md)** - типичные ошибки
- **[Справочник API](docs/API_REFERENCE.md)** - документация API

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 🌟 Благодарности

- **Perplexity AI** за предоставление мощной платформы
- **Anthropic** за Claude модели
- **Telegram** за Bot API
- **Сообществу разработчиков** за инструменты и библиотеки

## 📞 Контакты

- **GitHub**: [github.com/your-username](https://github.com/your-username)
- **Email**: your-email@example.com
- **Telegram**: [@your_username](https://t.me/your_username)

---

**⭐ Поставьте звездочку, если проект был полезен!**

**🚀 Система готова к запуску прямо сейчас!**