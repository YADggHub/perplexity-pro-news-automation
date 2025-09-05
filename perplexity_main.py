
import asyncio
import json
import sqlite3
import time
import schedule
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from telegram import Bot
from telegram.error import TelegramError
import re
import hashlib

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('perplexity_news.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class NewsPost:
    """Структура новостного поста"""
    title: str
    summary: str
    category: str
    importance: int
    keywords: List[str]
    sources: List[str]
    telegram_channels: List[str]
    raw_response: str
    created_at: datetime

class PerplexityAutomation:
    """Главный класс автоматизации Perplexity Pro"""

    def __init__(self, credentials: Dict[str, str]):
        self.email = credentials['email']
        self.password = credentials['password'] 
        self.telegram_token = credentials['telegram_token']
        self.channels = credentials['telegram_channels']

        self.driver = None
        self.session_active = False
        self.queries_used_today = 0
        self.max_daily_queries = 50  # Безопасный лимит

        self.setup_database()
        self.telegram_bot = Bot(token=self.telegram_token)

    def setup_database(self):
        """Инициализация базы данных"""
        self.conn = sqlite3.connect('perplexity_news.db', check_same_thread=False)
        cursor = self.conn.cursor()

        # Таблица для отслеживания запросов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS perplexity_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                response TEXT,
                tokens_estimated INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT FALSE,
                query_hash TEXT UNIQUE
            )
        """)

        # Таблица для постов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                summary TEXT,
                category TEXT,
                importance INTEGER,
                keywords TEXT,
                sources TEXT,
                telegram_channels TEXT,
                telegram_message_ids TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                published_at DATETIME,
                status TEXT DEFAULT 'pending'
            )
        """)

        # Таблица для статистики
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                queries_used INTEGER,
                posts_created INTEGER,
                posts_published INTEGER,
                telegram_messages_sent INTEGER,
                errors_count INTEGER
            )
        """)

        self.conn.commit()

    def setup_driver(self):
        """Настройка Selenium WebDriver"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

        # Отключаем изображения для экономии трафика
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    async def login_to_perplexity(self):
        """Авторизация в Perplexity"""
        try:
            if not self.driver:
                self.setup_driver()

            self.driver.get("https://www.perplexity.ai/")
            await asyncio.sleep(3)

            # Ищем кнопку входа
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign In')]"))
            )
            login_button.click()
            await asyncio.sleep(2)

            # Вводим email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
            )
            email_field.send_keys(self.email)

            # Вводим пароль
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            password_field.send_keys(self.password)

            # Нажимаем войти
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()

            # Ждем загрузки главной страницы
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea, input[placeholder*='Ask']"))
            )

            self.session_active = True
            logger.info("✅ Успешно авторизованы в Perplexity")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка авторизации в Perplexity: {e}")
            return False

    async def execute_perplexity_query(self, query: str) -> Optional[str]:
        """Выполнение запроса в Perplexity"""

        # Проверяем лимиты
        if self.queries_used_today >= self.max_daily_queries:
            logger.warning(f"⚠️ Достигнут дневной лимит запросов: {self.max_daily_queries}")
            return None

        # Проверяем дубликаты
        query_hash = hashlib.md5(query.encode()).hexdigest()
        cursor = self.conn.cursor()
        cursor.execute("SELECT response FROM perplexity_queries WHERE query_hash = ? AND success = TRUE", (query_hash,))
        existing = cursor.fetchone()

        if existing:
            logger.info(f"📋 Найден кэшированный ответ для запроса")
            return existing[0]

        try:
            if not self.session_active:
                await self.login_to_perplexity()

            # Находим поле ввода
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea, input[placeholder*='Ask']"))
            )

            # Очищаем и вводим запрос
            search_input.clear()
            search_input.send_keys(query)
            await asyncio.sleep(1)

            # Отправляем запрос
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button[aria-label*='Submit']")
            submit_button.click()

            # Ждем ответ (может занять до 30 секунд)
            logger.info(f"⏳ Ожидаем ответ от Perplexity на запрос: {query[:50]}...")

            # Ждем появления результата
            response_element = WebDriverWait(self.driver, 45).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='response'], .prose, .answer"))
            )

            # Извлекаем текст ответа
            response_text = response_element.text

            # Извлекаем источники
            try:
                sources_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='source'], .source, .citation")
                sources = [elem.get_attribute('href') or elem.text for elem in sources_elements[:5]]
            except:
                sources = []

            # Сохраняем в БД
            cursor.execute("""
                INSERT OR REPLACE INTO perplexity_queries 
                (query, response, query_hash, success) 
                VALUES (?, ?, ?, TRUE)
            """, (query, response_text, query_hash))
            self.conn.commit()

            self.queries_used_today += 1
            logger.info(f"✅ Получен ответ от Perplexity ({len(response_text)} символов)")

            return response_text

        except TimeoutException:
            logger.error("⏰ Timeout при ожидании ответа от Perplexity")
            return None

        except Exception as e:
            logger.error(f"❌ Ошибка выполнения запроса: {e}")
            return None

    def parse_perplexity_response(self, response: str, query_context: str) -> Optional[NewsPost]:
        """Парсинг ответа Perplexity в структурированный пост"""

        try:
            # Извлекаем основные элементы из ответа
            lines = response.split('\n')

            # Ищем заголовок (обычно первая строка или после маркеров)
            title = ""
            for line in lines[:5]:
                if len(line.strip()) > 20 and not line.startswith('http'):
                    title = line.strip()
                    break

            if not title:
                title = query_context[:60] + "..."

            # Создаем краткое содержание (первые 2-3 предложения)
            sentences = re.split(r'[.!?]', response)
            summary_sentences = []
            for sentence in sentences[:3]:
                if len(sentence.strip()) > 20:
                    summary_sentences.append(sentence.strip())

            summary = '. '.join(summary_sentences)
            if summary and not summary.endswith('.'):
                summary += '.'

            # Определяем категорию на основе ключевых слов
            response_lower = response.lower()
            category = "it"  # По умолчанию

            if any(word in response_lower for word in ['робот', 'robot', 'automation', 'автоматизац']):
                if any(word in response_lower for word in ['промышл', 'industrial', 'manufacturing']):
                    category = "automation"
                else:
                    category = "robotics"
            elif any(word in response_lower for word in ['ai', 'artificial intelligence', 'машинное обучение', 'нейрон']):
                category = "ai"

            # Оцениваем важность (1-10)
            importance = 5  # Базовая важность

            importance_indicators = {
                'breakthrough': +3, 'прорыв': +3,
                'revolutionary': +2, 'революц': +2,
                'major': +2, 'крупн': +2,
                'significant': +1, 'значител': +1,
                'funding': +1, 'финансирован': +1,
                'acquisition': +2, 'поглощен': +2,
                'partnership': +1, 'партнерств': +1
            }

            for keyword, score in importance_indicators.items():
                if keyword in response_lower:
                    importance += score

            importance = min(max(importance, 1), 10)

            # Извлекаем ключевые слова
            keywords = []
            common_tech_terms = [
                'AI', 'ИИ', 'машинное обучение', 'neural networks', 'blockchain',
                'cloud', 'облако', 'automation', 'robotics', 'IoT', 'API',
                'стартап', 'startup', 'инвестиции', 'funding'
            ]

            for term in common_tech_terms:
                if term.lower() in response_lower:
                    keywords.append(term)

            keywords = keywords[:5]  # Ограничиваем количество

            # Определяем целевые каналы
            telegram_channels = []
            if category == "it":
                telegram_channels.append("it_news")
            elif category == "automation": 
                telegram_channels.append("automation")
            elif category == "robotics":
                telegram_channels.append("robotics")
            elif category == "ai":
                telegram_channels.extend(["it_news", "automation"])

            # Если важность высокая, отправляем во все каналы
            if importance >= 8:
                telegram_channels = ["it_news", "automation", "robotics"]

            return NewsPost(
                title=title[:120],  # Ограничиваем длину заголовка
                summary=summary[:500],  # Ограничиваем длину описания
                category=category,
                importance=importance,
                keywords=keywords,
                sources=[],  # Заполнится позже
                telegram_channels=telegram_channels,
                raw_response=response,
                created_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"❌ Ошибка парсинга ответа Perplexity: {e}")
            return None

    async def create_news_post_from_query(self, query: str) -> Optional[NewsPost]:
        """Создание новостного поста из запроса"""

        # Выполняем запрос к Perplexity
        response = await self.execute_perplexity_query(query)
        if not response:
            return None

        # Парсим ответ
        post = self.parse_perplexity_response(response, query)
        if not post:
            return None

        # Сохраняем в БД
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO news_posts 
            (title, summary, category, importance, keywords, sources, telegram_channels, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'ready')
        """, (
            post.title,
            post.summary, 
            post.category,
            post.importance,
            json.dumps(post.keywords),
            json.dumps(post.sources),
            json.dumps(post.telegram_channels)
        ))
        self.conn.commit()

        logger.info(f"📝 Создан пост: {post.title} (важность: {post.importance})")
        return post

    async def publish_to_telegram(self, post: NewsPost):
        """Публикация поста в Telegram каналы"""

        # Форматируем сообщение
        emoji_map = {
            'it': '💻',
            'automation': '🤖',
            'robotics': '⚙️', 
            'ai': '🧠'
        }

        emoji = emoji_map.get(post.category, '📰')

        # Индикатор важности
        importance_emoji = ""
        if post.importance >= 9:
            importance_emoji = "🔥🔥 "
        elif post.importance >= 7:
            importance_emoji = "🔥 "

        # Формируем хештеги
        hashtags = [f"#{keyword.replace(' ', '_')}" for keyword in post.keywords[:3]]
        hashtags.append(f"#{post.category}")

        message = f"""
{emoji} **{importance_emoji}{post.title}**

{post.summary}

{' '.join(hashtags)}
📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}

#технологии #новости
        """.strip()

        published_channels = []

        # Публикуем в каналы
        for channel_key in post.telegram_channels:
            if channel_key in self.channels:
                try:
                    chat_id = self.channels[channel_key]
                    result = await self.telegram_bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode='Markdown'
                    )

                    published_channels.append(f"{channel_key}:{result.message_id}")
                    logger.info(f"📤 Опубликовано в {channel_key}")

                    # Пауза между отправками
                    await asyncio.sleep(2)

                except TelegramError as e:
                    logger.error(f"❌ Ошибка отправки в {channel_key}: {e}")

        # Обновляем статус в БД
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE news_posts 
            SET status = 'published', published_at = ?, telegram_message_ids = ?
            WHERE title = ? AND created_at = ?
        """, (datetime.now(), json.dumps(published_channels), post.title, post.created_at))
        self.conn.commit()

        return len(published_channels) > 0

# Предопределенные запросы для разных сессий
NEWS_QUERIES = {
    "morning": [
        "Последние новости в области искусственного интеллекта за сегодня на русском языке",
        "Какие важные события произошли в IT-индустрии за последние 24 часа?",
        "Новости про стартапы и технологии за сегодня, краткий обзор",
        "Что нового в области робототехники и автоматизации сегодня?",
        "Крупные инвестиции и сделки в IT-секторе за последний день",
        "Breakthrough технологии и научные открытия за сегодня",
        "Новые продукты и анонсы от крупных IT-компаний",
        "Тренды и события в области облачных технологий за день"
    ],

    "afternoon": [
        "Анализ важнейших технологических новостей дня с пояснениями",
        "Что обсуждают в IT-сообществе сегодня: главные темы",
        "Новости про автоматизацию производства и промышленные технологии",
        "События в области кибербезопасности и data science за сегодня",
        "Обновления и релизы популярных IT-продуктов за день",
        "Новости про cryptocurrency и blockchain технологии сегодня",
        "Важные события в области DevOps и cloud computing",
        "Тренды в области машинного обучения и нейронных сетей",
        "Новости про IoT и smart city технологии за сегодня",
        "События в области quantum computing и advanced technologies"
    ],

    "evening": [
        "Итоги дня в мире технологий: самое важное за сегодня",
        "Обзор международных технологических новостей за день",
        "Что произошло в Silicon Valley и других IT-хабах сегодня",
        "Новости про разработку ПО и programming languages за день",
        "События в области электронной коммерции и fintech сегодня",
        "Тренды в области mobile technologies и app development",
        "Новости про gaming industry и VR/AR технологии",
        "Важные события в области телекоммуникаций и 5G",
        "Обзор IPO, слияний и поглощений в IT-секторе за день",
        "Тенденции в области green tech и sustainable technologies",
        "События в области медицинских технологий и healthtech",
        "Новости про образовательные технологии и edtech за сегодня"
    ],

    "night": [
        "Важные технологические новости из США и Европы за день",
        "Overnight новости из азиатских IT-рынков и технологических компаний",
        "События в области космических технологий и SpaceX за сегодня",
        "Новости про Tesla и электротранспорт за день",
        "Важные релизы и обновления от Microsoft, Google, Apple сегодня",
        "События в области социальных сетей и digital платформ",
        "Тренды в области data privacy и digital rights",
        "Новости про clean energy и renewable technology за день"
    ]
}

class NewsScheduler:
    """Планировщик новостных сессий"""

    def __init__(self, automation: PerplexityAutomation):
        self.automation = automation
        self.setup_schedule()

    def setup_schedule(self):
        """Настройка расписания"""

        # Утренняя сессия - 09:00
        schedule.every().day.at("09:00").do(
            lambda: asyncio.create_task(self.run_session("morning", 3))
        )

        # Дневная сессия - 13:00
        schedule.every().day.at("13:00").do(
            lambda: asyncio.create_task(self.run_session("afternoon", 4))
        )

        # Вечерняя сессия - 18:00
        schedule.every().day.at("18:00").do(
            lambda: asyncio.create_task(self.run_session("evening", 5))
        )

        # Ночная сессия - 22:00
        schedule.every().day.at("22:00").do(
            lambda: asyncio.create_task(self.run_session("night", 3))
        )

    async def run_session(self, session_name: str, target_posts: int):
        """Запуск новостной сессии"""

        logger.info(f"🚀 Запуск сессии '{session_name}' (цель: {target_posts} постов)")

        queries = NEWS_QUERIES.get(session_name, [])
        posts_created = 0
        posts_published = 0

        # Перемешиваем запросы для разнообразия
        import random
        selected_queries = random.sample(queries, min(len(queries), target_posts * 3))

        for query in selected_queries[:target_posts * 2]:  # Берем с запасом
            if posts_created >= target_posts:
                break

            try:
                # Создаем пост
                post = await self.automation.create_news_post_from_query(query)
                if not post:
                    continue

                posts_created += 1

                # Публикуем если важность достаточная
                if post.importance >= 6:
                    success = await self.automation.publish_to_telegram(post)
                    if success:
                        posts_published += 1

                # Пауза между запросами
                await asyncio.sleep(30)  # 30 секунд между запросами

            except Exception as e:
                logger.error(f"❌ Ошибка в сессии {session_name}: {e}")

        logger.info(f"✅ Сессия '{session_name}' завершена: создано {posts_created}, опубликовано {posts_published}")

        # Обновляем статистику
        self.update_daily_stats(posts_created, posts_published)

    def update_daily_stats(self, posts_created: int, posts_published: int):
        """Обновление дневной статистики"""

        today = datetime.now().date().isoformat()
        cursor = self.automation.conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO daily_stats 
            (date, queries_used, posts_created, posts_published)
            VALUES (?, 
                    COALESCE((SELECT queries_used FROM daily_stats WHERE date = ?), 0) + ?,
                    COALESCE((SELECT posts_created FROM daily_stats WHERE date = ?), 0) + ?,
                    COALESCE((SELECT posts_published FROM daily_stats WHERE date = ?), 0) + ?)
        """, (today, today, self.automation.queries_used_today, today, posts_created, today, posts_published))

        self.automation.conn.commit()

async def main():
    """Главная функция запуска системы"""

    # Конфигурация (в реальности из переменных окружения)
    credentials = {
        'email': 'your-perplexity-email@example.com',
        'password': 'your-perplexity-password',
        'telegram_token': 'YOUR_TELEGRAM_BOT_TOKEN',
        'telegram_channels': {
            'it_news': '@your_it_channel',
            'automation': '@your_automation_channel', 
            'robotics': '@your_robotics_channel'
        }
    }

    # Создаем и запускаем систему
    automation = PerplexityAutomation(credentials)
    scheduler = NewsScheduler(automation)

    logger.info("🚀 Система автоматизации новостей запущена")

    # Тестовый запуск (можно убрать в продакшене)
    test_post = await automation.create_news_post_from_query(
        "Последние новости искусственного интеллекта за сегодня"
    )

    if test_post and test_post.importance >= 6:
        await automation.publish_to_telegram(test_post)
        logger.info("✅ Тестовый пост успешно создан и опубликован")

    # Основной цикл планировщика
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)  # Проверяем каждую минуту

if __name__ == "__main__":
    asyncio.run(main())
