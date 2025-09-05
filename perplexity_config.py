
import os
from typing import Dict, List

class Config:
    """Конфигурация системы"""

    # Настройки Perplexity
    PERPLEXITY_EMAIL = os.getenv("PERPLEXITY_EMAIL", "")
    PERPLEXITY_PASSWORD = os.getenv("PERPLEXITY_PASSWORD", "")

    # Настройки Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHANNELS = {
        "it_news": os.getenv("TG_IT_CHANNEL", ""),
        "automation": os.getenv("TG_AUTOMATION_CHANNEL", ""),
        "robotics": os.getenv("TG_ROBOTICS_CHANNEL", "")
    }

    # Лимиты системы
    MAX_DAILY_QUERIES = int(os.getenv("MAX_DAILY_QUERIES", "50"))
    MIN_IMPORTANCE_TO_PUBLISH = int(os.getenv("MIN_IMPORTANCE", "6"))

    # Настройки расписания
    SCHEDULE_CONFIG = {
        "morning": {
            "time": "09:00",
            "target_posts": 3,
            "queries_budget": 8
        },
        "afternoon": {
            "time": "13:00", 
            "target_posts": 4,
            "queries_budget": 10
        },
        "evening": {
            "time": "18:00",
            "target_posts": 5, 
            "queries_budget": 12
        },
        "night": {
            "time": "22:00",
            "target_posts": 3,
            "queries_budget": 8
        }
    }

    # Браузер настройки
    BROWSER_CONFIG = {
        "headless": True,
        "window_size": "1920,1080",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "timeout": 30
    }

    # База данных
    DATABASE_PATH = os.getenv("DATABASE_PATH", "perplexity_news.db")

    # Логирование
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "perplexity_news.log")

# Шаблоны запросов по категориям
QUERY_TEMPLATES = {
    "trending": [
        "Какие технологии сейчас на пике популярности? Обзор трендов {date}",
        "Топ новости IT-индустрии за сегодня с анализом важности",
        "Что обсуждает tech-сообщество прямо сейчас? Горячие темы"
    ],

    "business": [
        "Крупные инвестиции в технологические стартапы за последний день",
        "Слияния и поглощения в IT-секторе: последние сделки {date}",
        "IPO и финансирование технологических компаний сегодня"
    ],

    "products": [
        "Новые продукты и релизы от технологических гигантов за день",
        "Важные обновления популярных IT-сервисов и платформ",
        "Анонсы и презентации в мире технологий за {date}"
    ],

    "research": [
        "Прорывы в области искусственного интеллекта за последние сутки", 
        "Новые исследования в области компьютерных наук и технологий",
        "Breakthrough открытия в tech-сфере за сегодня"
    ],

    "automation": [
        "Новости промышленной автоматизации и роботизации за день",
        "IoT и smart technologies: последние разработки {date}",
        "Автоматизация бизнес-процессов: новые решения и тренды"
    ]
}

# Категоризация по ключевым словам
CATEGORY_KEYWORDS = {
    "ai": [
        "artificial intelligence", "машинное обучение", "neural network", 
        "deep learning", "GPT", "ChatGPT", "нейронная сеть", "AI", "ИИ"
    ],

    "robotics": [
        "robot", "робот", "automation", "автоматизация", "drone", "дрон",
        "robotics", "робототехника", "autonomous", "автономный"
    ],

    "blockchain": [
        "blockchain", "блокчейн", "cryptocurrency", "криптовалюта", 
        "bitcoin", "ethereum", "NFT", "DeFi", "web3"
    ],

    "cloud": [
        "cloud", "облако", "AWS", "Azure", "Google Cloud", "serverless",
        "containers", "docker", "kubernetes", "microservices"
    ],

    "mobile": [
        "mobile", "мобильный", "iOS", "Android", "app", "приложение",
        "smartphone", "смартфон", "tablet", "планшет"
    ]
}

# Индикаторы важности новости
IMPORTANCE_INDICATORS = {
    "high": {
        "keywords": ["breakthrough", "прорыв", "revolutionary", "революционный", 
                    "first ever", "впервые", "record", "рекорд"],
        "score": 3
    },
    "medium": {
        "keywords": ["significant", "значительный", "major", "крупный",
                    "important", "важный", "notable", "заметный"],
        "score": 2  
    },
    "financial": {
        "keywords": ["billion", "миллиард", "funding", "финансирование",
                    "IPO", "acquisition", "поглощение", "investment"],
        "score": 2
    },
    "companies": {
        "keywords": ["Google", "Apple", "Microsoft", "Amazon", "Meta",
                    "OpenAI", "Tesla", "NVIDIA", "Яндекс", "Сбер"],
        "score": 1
    }
}
