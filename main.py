#!/usr/bin/env python3
"""
Perplexity Pro News Automation System
=====================================

Главный модуль системы автоматизации новостей с интеграцией Perplexity Pro.
Обеспечивает полный цикл от сбора новостей до публикации в Telegram каналы.

Автор: News Automation Team
Версия: 1.0.0
Лицензия: MIT
"""

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config, load_config
from src.automation import PerplexityAutomation
from src.scheduler import NewsScheduler
from src.telegram_publisher import TelegramPublisher
from src.database import DatabaseManager

# Настройка логирования
def setup_logging():
    """Настройка системы логирования"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Основной логгер
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler(log_dir / "perplexity_news.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Отдельные логгеры для компонентов
    loggers = {
        'selenium': logging.WARNING,
        'urllib3': logging.WARNING,
        'telegram': logging.INFO,
        'asyncio': logging.WARNING
    }

    for logger_name, level in loggers.items():
        logging.getLogger(logger_name).setLevel(level)

class NewsAutomationSystem:
    """Главный класс системы автоматизации новостей"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = DatabaseManager(Config.DATABASE_PATH)
        self.automation = PerplexityAutomation(Config.get_perplexity_credentials())
        self.telegram = TelegramPublisher(Config.get_telegram_config())
        self.scheduler = NewsScheduler(self, Config.get_schedule_config())

        self.running = False
        self.stats = {
            'queries_today': 0,
            'posts_created_today': 0,
            'posts_published_today': 0,
            'errors_today': 0,
            'start_time': datetime.now()
        }

        # Настройка обработчиков сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self.logger.info("🚀 Система автоматизации новостей инициализирована")

    def signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        self.logger.info(f"📡 Получен сигнал {signum}. Завершение работы...")
        self.running = False

    async def health_check(self) -> Dict[str, bool]:
        """Проверка состояния всех компонентов системы"""
        health_status = {
            'database': False,
            'perplexity': False,
            'telegram': False,
            'browser': False
        }

        try:
            # Проверка базы данных
            self.db.get_daily_stats(datetime.now().date())
            health_status['database'] = True
        except Exception as e:
            self.logger.error(f"❌ Ошибка БД: {e}")

        try:
            # Проверка Perplexity (без реального запроса)
            if await self.automation.check_session():
                health_status['perplexity'] = True
        except Exception as e:
            self.logger.error(f"❌ Ошибка Perplexity: {e}")

        try:
            # Проверка Telegram
            if await self.telegram.check_connection():
                health_status['telegram'] = True
        except Exception as e:
            self.logger.error(f"❌ Ошибка Telegram: {e}")

        try:
            # Проверка браузера
            if await self.automation.check_browser():
                health_status['browser'] = True
        except Exception as e:
            self.logger.error(f"❌ Ошибка браузера: {e}")

        overall_health = all(health_status.values())
        status_emoji = "✅" if overall_health else "⚠️"

        self.logger.info(f"{status_emoji} Проверка здоровья: {health_status}")
        return health_status

    async def create_news_post_from_query(self, query: str) -> Optional['NewsPost']:
        """Создание поста из запроса к Perplexity"""

        try:
            # Проверка лимитов
            if self.stats['queries_today'] >= Config.MAX_DAILY_QUERIES:
                self.logger.warning(f"⚠️ Достигнут дневной лимит запросов: {Config.MAX_DAILY_QUERIES}")
                return None

            self.logger.info(f"🔍 Выполняем запрос: {query[:50]}...")

            # Выполнение запроса через Perplexity
            response = await self.automation.execute_query(query)
            if not response:
                self.stats['errors_today'] += 1
                return None

            self.stats['queries_today'] += 1

            # Обработка ответа
            post = await self.automation.process_response(response, query)
            if not post:
                self.stats['errors_today'] += 1
                return None

            # Сохранение в БД
            self.db.save_news_post(post)
            self.stats['posts_created_today'] += 1

            self.logger.info(f"📝 Создан пост: {post.title} (важность: {post.importance})")
            return post

        except Exception as e:
            self.logger.error(f"❌ Ошибка создания поста: {e}")
            self.stats['errors_today'] += 1
            return None

    async def publish_post(self, post: 'NewsPost') -> bool:
        """Публикация поста в Telegram каналы"""

        try:
            # Проверка важности
            if post.importance < Config.MIN_IMPORTANCE_TO_PUBLISH:
                self.logger.debug(f"⏭️ Пост пропущен (важность {post.importance} < {Config.MIN_IMPORTANCE_TO_PUBLISH})")
                return False

            # Публикация в каналы
            success = await self.telegram.publish_post(post)

            if success:
                self.stats['posts_published_today'] += 1
                self.db.update_post_status(post.id, 'published')
                self.logger.info(f"📤 Пост опубликован: {post.title}")
                return True
            else:
                self.stats['errors_today'] += 1
                return False

        except Exception as e:
            self.logger.error(f"❌ Ошибка публикации: {e}")
            self.stats['errors_today'] += 1
            return False

    async def run_manual_session(self, session_name: str = "manual") -> Dict[str, int]:
        """Запуск ручной сессии обработки новостей"""

        self.logger.info(f"🎯 Запуск ручной сессии: {session_name}")

        results = {
            'posts_created': 0,
            'posts_published': 0,
            'queries_used': 0,
            'errors': 0
        }

        # Получаем список запросов для сессии
        queries = Config.get_session_queries(session_name)

        for query in queries[:Config.MAX_QUERIES_PER_SESSION]:
            try:
                # Создание поста
                post = await self.create_news_post_from_query(query)
                if post:
                    results['posts_created'] += 1
                    results['queries_used'] += 1

                    # Публикация если важность достаточная
                    if post.importance >= Config.MIN_IMPORTANCE_TO_PUBLISH:
                        if await self.publish_post(post):
                            results['posts_published'] += 1

                # Пауза между запросами
                await asyncio.sleep(Config.QUERY_DELAY_SECONDS)

            except Exception as e:
                self.logger.error(f"❌ Ошибка в ручной сессии: {e}")
                results['errors'] += 1

        self.logger.info(f"✅ Ручная сессия завершена: {results}")
        return results

    async def run_scheduled_sessions(self):
        """Запуск планировщика автоматических сессий"""

        self.logger.info("📅 Запуск планировщика сессий")

        while self.running:
            try:
                # Проверяем расписание
                await self.scheduler.check_and_run_sessions()

                # Пауза перед следующей проверкой
                await asyncio.sleep(60)  # Проверяем каждую минуту

            except Exception as e:
                self.logger.error(f"❌ Ошибка в планировщике: {e}")
                await asyncio.sleep(300)  # 5 минут при ошибке

    async def update_daily_stats(self):
        """Обновление дневной статистики"""

        today = datetime.now().date()
        stats_data = {
            'date': today.isoformat(),
            'queries_used': self.stats['queries_today'],
            'posts_created': self.stats['posts_created_today'],
            'posts_published': self.stats['posts_published_today'],
            'errors_count': self.stats['errors_today']
        }

        self.db.update_daily_stats(stats_data)

        # Сброс счетчиков в полночь
        now = datetime.now()
        if now.hour == 0 and now.minute < 2:
            self.reset_daily_counters()

    def reset_daily_counters(self):
        """Сброс дневных счетчиков"""
        self.stats.update({
            'queries_today': 0,
            'posts_created_today': 0,
            'posts_published_today': 0,
            'errors_today': 0
        })
        self.logger.info("🔄 Дневные счетчики сброшены")

    def get_system_status(self) -> Dict:
        """Получение статуса системы"""

        uptime = datetime.now() - self.stats['start_time']

        return {
            'status': 'running' if self.running else 'stopped',
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_human': str(uptime).split('.')[0],
            'stats': self.stats,
            'config': {
                'max_daily_queries': Config.MAX_DAILY_QUERIES,
                'min_importance': Config.MIN_IMPORTANCE_TO_PUBLISH,
                'channels_count': len(Config.TELEGRAM_CHANNELS)
            }
        }

    async def start(self):
        """Запуск основного цикла системы"""

        self.logger.info("🚀 Запуск системы автоматизации новостей")
        self.running = True

        try:
            # Проверка здоровья перед стартом
            health = await self.health_check()
            if not all(health.values()):
                self.logger.warning("⚠️ Не все компоненты готовы к работе")
                for component, status in health.items():
                    if not status:
                        self.logger.error(f"❌ Компонент '{component}' недоступен")

            # Инициализация компонентов
            await self.automation.initialize()
            await self.telegram.initialize()

            # Запуск фоновых задач
            tasks = [
                asyncio.create_task(self.run_scheduled_sessions()),
                asyncio.create_task(self.periodic_health_check()),
                asyncio.create_task(self.periodic_stats_update())
            ]

            self.logger.info("✅ Система запущена и готова к работе")

            # Ожидание завершения
            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            self.logger.error(f"❌ Критическая ошибка системы: {e}")
        finally:
            await self.shutdown()

    async def periodic_health_check(self):
        """Периодическая проверка здоровья системы"""

        while self.running:
            try:
                await asyncio.sleep(Config.HEALTH_CHECK_INTERVAL)
                await self.health_check()
            except Exception as e:
                self.logger.error(f"❌ Ошибка проверки здоровья: {e}")

    async def periodic_stats_update(self):
        """Периодическое обновление статистики"""

        while self.running:
            try:
                await asyncio.sleep(300)  # Каждые 5 минут
                await self.update_daily_stats()
            except Exception as e:
                self.logger.error(f"❌ Ошибка обновления статистики: {e}")

    async def shutdown(self):
        """Корректное завершение работы системы"""

        self.logger.info("🛑 Завершение работы системы...")

        try:
            # Завершение компонентов
            if hasattr(self.automation, 'cleanup'):
                await self.automation.cleanup()

            if hasattr(self.telegram, 'cleanup'):
                await self.telegram.cleanup()

            # Сохранение финальной статистики
            await self.update_daily_stats()

            # Закрытие соединений
            if hasattr(self.db, 'close'):
                self.db.close()

            self.logger.info("✅ Система корректно завершена")

        except Exception as e:
            self.logger.error(f"❌ Ошибка при завершении: {e}")

# Команды CLI
async def run_single_query(query: str):
    """CLI команда для выполнения одного запроса"""

    system = NewsAutomationSystem()
    post = await system.create_news_post_from_query(query)

    if post:
        print(f"✅ Пост создан:")
        print(f"Заголовок: {post.title}")
        print(f"Важность: {post.importance}/10")
        print(f"Категория: {post.category}")
        print(f"Каналы: {', '.join(post.telegram_channels)}")

        if post.importance >= Config.MIN_IMPORTANCE_TO_PUBLISH:
            if await system.publish_post(post):
                print("📤 Пост опубликован в Telegram")
            else:
                print("❌ Ошибка публикации в Telegram")
        else:
            print(f"⏭️ Пост не опубликован (важность < {Config.MIN_IMPORTANCE_TO_PUBLISH})")
    else:
        print("❌ Не удалось создать пост")

    await system.shutdown()

async def run_manual_session_cmd(session_name: str = "manual"):
    """CLI команда для запуска ручной сессии"""

    system = NewsAutomationSystem()
    results = await system.run_manual_session(session_name)

    print(f"✅ Сессия '{session_name}' завершена:")
    print(f"Создано постов: {results['posts_created']}")
    print(f"Опубликовано: {results['posts_published']}")
    print(f"Использовано запросов: {results['queries_used']}")

    if results['errors'] > 0:
        print(f"❌ Ошибок: {results['errors']}")

    await system.shutdown()

async def show_system_status():
    """CLI команда для показа статуса системы"""

    system = NewsAutomationSystem()
    status = system.get_system_status()

    print(f"📊 Статус системы: {status['status']}")
    print(f"⏱️ Время работы: {status['uptime_human']}")
    print(f"📈 Запросов сегодня: {status['stats']['queries_today']}")
    print(f"📝 Постов создано: {status['stats']['posts_created_today']}")
    print(f"📤 Постов опубликовано: {status['stats']['posts_published_today']}")

    if status['stats']['errors_today'] > 0:
        print(f"❌ Ошибок сегодня: {status['stats']['errors_today']}")

def main():
    """Главная функция запуска"""

    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)

    # Создание директорий
    for dir_name in ['data', 'logs', 'temp']:
        Path(dir_name).mkdir(exist_ok=True)

    # Проверка конфигурации
    if not Config.validate_config():
        logger.error("❌ Ошибки в конфигурации. Завершение работы.")
        sys.exit(1)

    # CLI команды
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "query" and len(sys.argv) > 2:
            query = " ".join(sys.argv[2:])
            asyncio.run(run_single_query(query))

        elif command == "session" and len(sys.argv) > 2:
            session_name = sys.argv[2]
            asyncio.run(run_manual_session_cmd(session_name))

        elif command == "status":
            asyncio.run(show_system_status())

        elif command == "health":
            async def check_health():
                system = NewsAutomationSystem()
                health = await system.health_check()
                for component, status in health.items():
                    emoji = "✅" if status else "❌"
                    print(f"{emoji} {component}: {'OK' if status else 'FAIL'}")

            asyncio.run(check_health())

        else:
            print("Доступные команды:")
            print("  python src/main.py query 'ваш запрос'")
            print("  python src/main.py session morning|afternoon|evening|night")
            print("  python src/main.py status")
            print("  python src/main.py health")
            sys.exit(1)
    else:
        # Основной режим работы
        try:
            system = NewsAutomationSystem()
            asyncio.run(system.start())
        except KeyboardInterrupt:
            logger.info("👋 Получено прерывание пользователя")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
