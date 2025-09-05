#!/usr/bin/env python3
"""
Configuration Module for Perplexity Pro News Automation System
==============================================================

Централизованная система конфигурации с валидацией параметров
и управлением настройками различных компонентов системы.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class PerplexityCredentials:
    """Учетные данные для Perplexity Pro"""
    email: str
    password: str

@dataclass
class TelegramConfig:
    """Конфигурация Telegram бота и каналов"""
    bot_token: str
    channels: Dict[str, str]

@dataclass
class SessionConfig:
    """Конфигурация сессии обработки новостей"""
    name: str
    time: str
    target_posts: int
    queries_budget: int
    enabled: bool = True

class Config:
    """Главный класс конфигурации системы"""

    # =============================================================================
    # ОСНОВНЫЕ ПАРАМЕТРЫ
    # =============================================================================

    # Perplexity Pro настройки
    PERPLEXITY_EMAIL = os.getenv("PERPLEXITY_EMAIL", "")
    PERPLEXITY_PASSWORD = os.getenv("PERPLEXITY_PASSWORD", "")

    # Telegram настройки
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHANNELS = {
        "it_news": os.getenv("TG_IT_CHANNEL", ""),
        "automation": os.getenv("TG_AUTOMATION_CHANNEL", ""),
        "robotics": os.getenv("TG_ROBOTICS_CHANNEL", "")
    }

    # Системные лимиты
    MAX_DAILY_QUERIES = int(os.getenv("MAX_DAILY_QUERIES", "50"))
    MIN_IMPORTANCE_TO_PUBLISH = int(os.getenv("MIN_IMPORTANCE_TO_PUBLISH", "6"))
    MAX_QUERIES_PER_SESSION = int(os.getenv("MAX_QUERIES_PER_SESSION", "15"))

    # =============================================================================
    # ПЛАНИРОВЩИК НАСТРОЙКИ
    # =============================================================================

    SESSIONS_CONFIG = {
        "morning": SessionConfig(
            name="morning",
            time=os.getenv("MORNING_SESSION_TIME", "09:00"),
            target_posts=int(os.getenv("MORNING_SESSION_POSTS", "3")),
            queries_budget=int(os.getenv("MORNING_SESSION_QUERIES", "8"))
        ),
        "afternoon": SessionConfig(
            name="afternoon", 
            time=os.getenv("AFTERNOON_SESSION_TIME", "13:00"),
            target_posts=int(os.getenv("AFTERNOON_SESSION_POSTS", "4")),
            queries_budget=int(os.getenv("AFTERNOON_SESSION_QUERIES", "10"))
        ),
        "evening": SessionConfig(
            name="evening",
            time=os.getenv("EVENING_SESSION_TIME", "18:00"),
            target_posts=int(os.getenv("EVENING_SESSION_POSTS", "5")),
            queries_budget=int(os.getenv("EVENING_SESSION_QUERIES", "12"))
        ),
        "night": SessionConfig(
            name="night",
            time=os.getenv("NIGHT_SESSION_TIME", "22:00"),
            target_posts=int(os.getenv("NIGHT_SESSION_POSTS", "3")),
            queries_budget=int(os.getenv("NIGHT_SESSION_QUERIES", "8"))
        )
    }

    # =============================================================================
    # БРАУЗЕР НАСТРОЙКИ
    # =============================================================================

    BROWSER_CONFIG = {
        "headless": os.getenv("BROWSER_HEADLESS", "true").lower() == "true",
        "timeout": int(os.getenv("BROWSER_TIMEOUT", "30")),
        "window_size": os.getenv("BROWSER_WINDOW_SIZE", "1920,1080"),
        "user_agent": os.getenv("BROWSER_USER_AGENT", 
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    }

    # =============================================================================
    # ПРОИЗВОДИТЕЛЬНОСТЬ И НАДЕЖНОСТЬ
    # =============================================================================

    # Retry настройки
    MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
    RETRY_DELAY_SECONDS = int(os.getenv("RETRY_DELAY_SECONDS", "5"))
    QUERY_DELAY_SECONDS = int(os.getenv("QUERY_DELAY_SECONDS", "30"))

    # Rate limiting
    REQUESTS_PER_MINUTE = int(os.getenv("REQUESTS_PER_MINUTE", "2"))
    TELEGRAM_RATE_LIMIT = int(os.getenv("TELEGRAM_RATE_LIMIT", "30"))

    # Мониторинг
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "300"))
    METRICS_RETENTION_DAYS = int(os.getenv("METRICS_RETENTION_DAYS", "30"))

    # =============================================================================
    # ПУТИ И ЛОГИРОВАНИЕ
    # =============================================================================

    # База данных
    DATABASE_PATH = os.getenv("DATABASE_PATH", "data/perplexity_news.db")

    # Логирование
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/perplexity_news.log")

    # Резервное копирование
    AUTO_BACKUP_ENABLED = os.getenv("AUTO_BACKUP_ENABLED", "true").lower() == "true"
    BACKUP_INTERVAL_HOURS = int(os.getenv("BACKUP_INTERVAL_HOURS", "24"))
    BACKUP_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "7"))

    # =============================================================================
    # ШАБЛОНЫ ЗАПРОСОВ
    # =============================================================================

    QUERY_TEMPLATES = {
        "trending": [
            "Какие технологии сейчас на пике популярности? Обзор главных трендов за сегодня",
            "Топ-5 важнейших новостей IT-индустрии за последние 24 часа с анализом",
            "Что активно обсуждает международное tech-сообщество прямо сейчас?",
            "Горячие темы в области технологий: что происходит сегодня",
            "Trending технологические новости с подробным анализом важности"
        ],

        "business": [
            "Крупные инвестиции в технологические стартапы за последние 24 часа",
            "Слияния и поглощения в IT-секторе: свежие сделки и их анализ",
            "IPO и раунды финансирования технологических компаний сегодня",
            "Бизнес-новости из мира технологий: инвестиции, сделки, партнерства",
            "Венчурное финансирование и стартап-экосистема: события дня"
        ],

        "products": [
            "Новые продукты и важные релизы от технологических гигантов за день",
            "Значимые обновления популярных IT-сервисов и платформ",
            "Анонсы и презентации новых технологий за последние сутки",
            "Product launches в tech-индустрии: что нового представили компании",
            "Обзор новых IT-продуктов и сервисов, запущенных сегодня"
        ],

        "research": [
            "Прорывы в области искусственного интеллекта за последние 24 часа",
            "Новые научные исследования в области компьютерных наук и технологий",
            "Breakthrough открытия и инновации в tech-сфере за сегодня",
            "Исследовательские достижения в области машинного обучения и ИИ",
            "Научные новости из мира технологий: открытия и эксперименты"
        ],

        "automation": [
            "Новости промышленной автоматизации и роботизации производства",
            "IoT и умные технологии: последние разработки и внедрения",
            "Автоматизация бизнес-процессов: новые решения и кейсы",
            "Робототехника и промышленные роботы: новости и тренды дня",
            "Smart city и городские технологии: проекты и реализации"
        ],

        "security": [
            "Важные события в области кибербезопасности за день",
            "Новые угрозы и методы защиты в информационной безопасности",
            "Data breaches и инциденты безопасности в tech-компаниях",
            "Обновления и патчи безопасности от крупных вендоров",
            "Тренды в области cybersecurity и защиты данных"
        ]
    }

    # =============================================================================
    # КАТЕГОРИЗАЦИЯ КОНТЕНТА  
    # =============================================================================

    CATEGORY_KEYWORDS = {
        "ai": {
            "keywords": [
                "artificial intelligence", "машинное обучение", "neural network", "нейронная сеть",
                "deep learning", "GPT", "ChatGPT", "Claude", "LLM", "ИИ", "AI", "ML",
                "computer vision", "NLP", "natural language", "генеративный"
            ],
            "weight": 1.0
        },

        "robotics": {
            "keywords": [
                "robot", "робот", "robotics", "робототехника", "automation", "автоматизация",
                "drone", "дрон", "autonomous", "автономный", "industrial robot",
                "промышленный робот", "humanoid", "гуманоид", "Boston Dynamics"
            ],
            "weight": 1.0
        },

        "blockchain": {
            "keywords": [
                "blockchain", "блокчейн", "cryptocurrency", "криптовалюта", "bitcoin", "биткойн",
                "ethereum", "эфир", "NFT", "DeFi", "web3", "decentralized", "децентрализованный",
                "smart contract", "умный контракт", "mining", "майнинг"
            ],
            "weight": 0.8
        },

        "cloud": {
            "keywords": [
                "cloud", "облако", "AWS", "Azure", "Google Cloud", "serverless",
                "containers", "контейнеры", "docker", "kubernetes", "microservices",
                "микросервисы", "SaaS", "PaaS", "IaaS", "облачные вычисления"
            ],
            "weight": 0.9
        },

        "mobile": {
            "keywords": [
                "mobile", "мобильный", "iOS", "Android", "app", "приложение", "мобильное приложение",
                "smartphone", "смартфон", "tablet", "планшет", "Apple", "Google Play",
                "mobile development", "мобильная разработка", "React Native", "Flutter"
            ],
            "weight": 0.7
        },

        "startup": {
            "keywords": [
                "startup", "стартап", "venture capital", "венчурный капитал", "funding", "финансирование",
                "seed", "Series A", "IPO", "unicorn", "единорог", "Y Combinator",
                "accelerator", "акселератор", "pitch", "инвестор", "investor"
            ],
            "weight": 0.8
        }
    }

    # =============================================================================
    # ИНДИКАТОРЫ ВАЖНОСТИ
    # =============================================================================

    IMPORTANCE_INDICATORS = {
        "breakthrough": {
            "keywords": [
                "breakthrough", "прорыв", "revolutionary", "революционный", "groundbreaking",
                "first ever", "впервые в мире", "historic", "исторический", "unprecedented", "беспрецедентный"
            ],
            "score": 4,
            "description": "Прорывные технологии и открытия"
        },

        "major_announcement": {
            "keywords": [
                "announces", "объявляет", "launches", "запускает", "unveils", "представляет",
                "reveals", "раскрывает", "introduces", "внедряет", "major update", "крупное обновление"
            ],
            "score": 2,
            "description": "Крупные анонсы и запуски"
        },

        "financial": {
            "keywords": [
                "billion", "миллиард", "million", "миллион", "funding", "финансирование",
                "investment", "инвестиции", "IPO", "acquisition", "поглощение", "merger", "слияние",
                "valuation", "оценка", "raised", "привлек", "invested", "инвестировал"
            ],
            "score": 3,
            "description": "Финансовые события и сделки"
        },

        "security_critical": {
            "keywords": [
                "vulnerability", "уязвимость", "security breach", "утечка данных", "hack", "взлом",
                "critical update", "критическое обновление", "zero-day", "emergency patch",
                "экстренный патч", "data breach", "нарушение безопасности"
            ],
            "score": 3,
            "description": "Критические вопросы безопасности"
        },

        "market_impact": {
            "keywords": [
                "stock", "акции", "market cap", "капитализация", "shares", "падение",
                "surge", "рост", "trading", "торги", "nasdaq", "NYSE",
                "analyst", "аналитик", "forecast", "прогноз", "outlook", "перспективы"
            ],
            "score": 2,
            "description": "Влияние на рынок"
        },

        "regulatory": {
            "keywords": [
                "regulation", "регулирование", "government", "правительство", "policy", "политика",
                "law", "закон", "compliance", "соответствие", "fine", "штраф",
                "investigation", "расследование", "antitrust", "антимонопольный"
            ],
            "score": 2,
            "description": "Регулятивные вопросы"
        },

        "tech_giants": {
            "keywords": [
                "Apple", "Google", "Microsoft", "Amazon", "Meta", "Facebook",
                "Tesla", "OpenAI", "NVIDIA", "Intel", "AMD", "Samsung",
                "Яндекс", "Сбер", "VK", "Kaspersky", "Tinkoff"
            ],
            "score": 1,
            "description": "Новости от крупных компаний"
        }
    }

    # =============================================================================
    # НАСТРОЙКИ ФОРМАТИРОВАНИЯ TELEGRAM
    # =============================================================================

    TELEGRAM_FORMATTING = {
        "emoji_map": {
            "ai": "🧠",
            "it": "💻", 
            "automation": "🤖",
            "robotics": "⚙️",
            "blockchain": "⛓️",
            "cloud": "☁️",
            "mobile": "📱",
            "security": "🔒",
            "startup": "🚀",
            "general": "📰"
        },

        "importance_indicators": {
            9: "🔥🔥🔥 ПРОРЫВ: ",
            8: "🔥🔥 ВАЖНО: ",
            7: "🔥 ЗНАЧИМО: ",
            6: "📢 ",
            5: "",
            4: "",
            3: "",
            2: "",
            1: ""
        },

        "hashtag_limits": {
            "max_hashtags": 5,
            "min_hashtags": 2,
            "max_length": 20
        }
    }

    # =============================================================================
    # МЕТОДЫ КЛАССА
    # =============================================================================

    @classmethod
    def get_perplexity_credentials(cls) -> PerplexityCredentials:
        """Получение учетных данных Perplexity"""
        return PerplexityCredentials(
            email=cls.PERPLEXITY_EMAIL,
            password=cls.PERPLEXITY_PASSWORD
        )

    @classmethod
    def get_telegram_config(cls) -> TelegramConfig:
        """Получение конфигурации Telegram"""
        return TelegramConfig(
            bot_token=cls.TELEGRAM_BOT_TOKEN,
            channels=cls.TELEGRAM_CHANNELS
        )

    @classmethod
    def get_schedule_config(cls) -> Dict[str, SessionConfig]:
        """Получение конфигурации планировщика"""
        return cls.SESSIONS_CONFIG

    @classmethod
    def get_session_queries(cls, session_name: str, category: str = None) -> List[str]:
        """Получение запросов для сессии"""

        if session_name not in cls.QUERY_TEMPLATES:
            # Используем микс категорий для неизвестных сессий
            all_queries = []
            for cat_queries in cls.QUERY_TEMPLATES.values():
                all_queries.extend(cat_queries)
            return all_queries[:10]

        queries = cls.QUERY_TEMPLATES[session_name].copy()

        # Добавляем специфичные запросы для времени суток
        time_specific = {
            "morning": [
                "Главные технологические новости за ночь: что произошло пока мы спали",
                "Morning digest: ключевые события в IT-мире за последние 12 часов"
            ],
            "afternoon": [
                "Дневной обзор: что обсуждают в tech-индустрии прямо сейчас",
                "Полуденная сводка важнейших технологических событий"
            ],
            "evening": [
                "Вечерний дайджест: итоги дня в мире высоких технологий",
                "What happened today: главные tech-события дня"
            ],
            "night": [
                "Международные технологические новости: обзор событий из США и Азии",
                "Overnight tech news: что происходит в других часовых поясах"
            ]
        }

        if session_name in time_specific:
            queries.extend(time_specific[session_name])

        return queries

    @classmethod
    def validate_config(cls) -> bool:
        """Валидация конфигурации системы"""

        errors = []

        # Проверка обязательных параметров
        required_params = [
            ("PERPLEXITY_EMAIL", cls.PERPLEXITY_EMAIL),
            ("PERPLEXITY_PASSWORD", cls.PERPLEXITY_PASSWORD),
            ("TELEGRAM_BOT_TOKEN", cls.TELEGRAM_BOT_TOKEN)
        ]

        for param_name, param_value in required_params:
            if not param_value:
                errors.append(f"Отсутствует обязательный параметр: {param_name}")

        # Проверка каналов Telegram
        for channel_name, channel_id in cls.TELEGRAM_CHANNELS.items():
            if not channel_id:
                errors.append(f"Не настроен канал: {channel_name}")
            elif not (channel_id.startswith("@") or channel_id.startswith("-")):
                errors.append(f"Неверный формат ID канала {channel_name}: {channel_id}")

        # Проверка числовых параметров
        if cls.MAX_DAILY_QUERIES <= 0 or cls.MAX_DAILY_QUERIES > 300:
            errors.append(f"Неверное значение MAX_DAILY_QUERIES: {cls.MAX_DAILY_QUERIES}")

        if cls.MIN_IMPORTANCE_TO_PUBLISH < 1 or cls.MIN_IMPORTANCE_TO_PUBLISH > 10:
            errors.append(f"Неверное значение MIN_IMPORTANCE_TO_PUBLISH: {cls.MIN_IMPORTANCE_TO_PUBLISH}")

        # Проверка временных параметров сессий
        import re
        time_pattern = re.compile(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')

        for session_name, session_config in cls.SESSIONS_CONFIG.items():
            if not time_pattern.match(session_config.time):
                errors.append(f"Неверный формат времени для сессии {session_name}: {session_config.time}")

        # Вывод ошибок
        if errors:
            logger.error("❌ Найдены ошибки конфигурации:")
            for error in errors:
                logger.error(f"  • {error}")
            return False

        logger.info("✅ Конфигурация прошла валидацию")
        return True

    @classmethod
    def get_browser_options(cls) -> List[str]:
        """Получение опций для браузера"""

        options = [
            "--no-sandbox",
            "--disable-dev-shm-usage", 
            "--disable-gpu",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-images",  # Экономия трафика
            "--disable-javascript",  # Для некоторых сайтов
            f"--window-size={cls.BROWSER_CONFIG['window_size']}",
            f"--user-agent={cls.BROWSER_CONFIG['user_agent']}"
        ]

        if cls.BROWSER_CONFIG["headless"]:
            options.append("--headless")

        return options

    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Получение конфигурации базы данных"""

        db_path = Path(cls.DATABASE_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        return {
            "path": str(db_path),
            "backup_enabled": cls.AUTO_BACKUP_ENABLED,
            "backup_interval": cls.BACKUP_INTERVAL_HOURS,
            "retention_days": cls.METRICS_RETENTION_DAYS
        }

    @classmethod
    def export_config(cls) -> Dict[str, Any]:
        """Экспорт конфигурации для API/веб-интерфейса"""

        return {
            "system": {
                "max_daily_queries": cls.MAX_DAILY_QUERIES,
                "min_importance": cls.MIN_IMPORTANCE_TO_PUBLISH,
                "max_queries_per_session": cls.MAX_QUERIES_PER_SESSION
            },
            "sessions": {
                name: {
                    "time": config.time,
                    "target_posts": config.target_posts,
                    "queries_budget": config.queries_budget,
                    "enabled": config.enabled
                }
                for name, config in cls.SESSIONS_CONFIG.items()
            },
            "channels": {
                name: {"id": channel_id, "enabled": bool(channel_id)}
                for name, channel_id in cls.TELEGRAM_CHANNELS.items()
            },
            "browser": cls.BROWSER_CONFIG,
            "performance": {
                "max_retry_attempts": cls.MAX_RETRY_ATTEMPTS,
                "query_delay": cls.QUERY_DELAY_SECONDS,
                "health_check_interval": cls.HEALTH_CHECK_INTERVAL
            }
        }

def load_config() -> Dict[str, Any]:
    """Загрузка и возврат конфигурации"""
    return Config.export_config()

# Проверка конфигурации при импорте
if __name__ == "__main__":
    Config.validate_config()
else:
    # При импорте модуля проводим базовую проверку
    if not Config.PERPLEXITY_EMAIL or not Config.TELEGRAM_BOT_TOKEN:
        logger.warning("⚠️ Не все обязательные параметры конфигурации настроены")
