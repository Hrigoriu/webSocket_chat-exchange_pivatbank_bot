import asyncio
import logging
import websockets
import names
from faker import Faker
from datetime import datetime, timedelta
import aiohttp
from websockets.server import ServerConnection, WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

# Пакети для асинхронної роботи з файлами
from aiopath import AsyncPath
from aiofile import async_open

# Налаштуємо базове логування в консоль для відстеження подій сервера
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Ініціалізуємо генератор фейкових даних з українською локалізацією
fake = Faker("uk_UA")


class ExchangeService:
    """Створимо клас для отримання курсів валют від API ПриватБанку та їх форматування для чату."""

    BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates"

    async def fetch_rates(self, session: aiohttp.ClientSession, date: str) -> dict:
        """Створимо функцію, яка асинхронно виконує GET запит та отримує сирі дані (JSON) за конкретну дату."""
        url = f"{self.BASE_URL}?date={date}"
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            logging.error(f"Помилка отримання курсу за {date}: {e}")
        return None

    def format_chat_response(self, raw_responses: list) -> str:
        """Створимо функцію, яка форматує отриманий JSON у зручний для читання багаторядковий текст."""
        if not raw_responses:
            return "Не вдалося отримати дані про курси валют."

        text_lines = ["\n📊 **Курс валют (ПриватБанк):**"]
        target_currencies = ["EUR", "USD"]  # Базові валюти для чату

        # Перебираємо дані за кожен день
        for data in raw_responses:
            if not data or "exchangeRate" not in data:
                continue

            date = data.get("date")
            text_lines.append(f"\n📅 Дата: {date}")

            # Шукаємо потрібні валюти в списку
            for rate in data["exchangeRate"]:
                currency = rate.get("currency")
                if currency in target_currencies:
                    # Отримуємо курс продажу/купівлі. Якщо немає готівкового, беремо курс НБУ.
                    sale = rate.get("saleRate") or rate.get("saleRateNB", 0)
                    purchase = rate.get("purchaseRate") or rate.get("purchaseRateNB", 0)
                    text_lines.append(
                        f" 🔹 {currency} - Купівля: {purchase:.2f} | Продаж: {sale:.2f}"
                    )

        # З'єднуємо всі рядки символом переносу рядка
        return "\n".join(text_lines)

    async def get_exchange_for_chat(self, days: int) -> str:
        """Створимо функцію-Оркестратор для чату: генерує дати, робить паралельні запити і повертає текст."""
        # Генеруємо список дат
        dates = [
            (datetime.today() - timedelta(days=i)).strftime("%d.%m.%Y")
            for i in range(days)
        ]

        # Створюємо одну HTTP сесію для ефективності
        async with aiohttp.ClientSession() as session:
            # Створюємо завдання і запускаємо їх паралельно
            tasks = [self.fetch_rates(session, date) for date in dates]
            raw_responses = await asyncio.gather(*tasks)

        return self.format_chat_response(raw_responses)


class Server:
    """Створимо головний клас WebSocket-сервера, який керувати підключеннями та повідомленнями."""

    clients = set()
    exchange_service = ExchangeService()

    # Вказуємо шлях до файлу логів за допомогою aiopath
    log_file_path = AsyncPath("exchange_commands.log")

    async def log_exchange_command(self, user_name: str, days: int):
        """Створимо функцію , яка буде асинхронно записувати інформацію про виклик команди exchange у файл."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] Користувач '{user_name}' викликав команду exchange за {days} дн.\n"

        # Відкриваємо файл у режимі 'a' (append - дозапис у кінець файлу)
        async with async_open(self.log_file_path, "a") as afp:
            await afp.write(log_message)

    async def register(self, ws: ServerConnection):
        """Створимо функцію, яка реєструє нового клієнта при підключенні та дає йому випадкове ім'я."""
        ws.name = fake.name()
        self.clients.add(ws)
        logging.info(f"{ws.remote_address} підключився як {ws.name}")
        await self.send_to_clients(f"👋 {ws.name} приєднався до чату.")

    async def unregister(self, ws: ServerConnection):
        """Створимо функцію, яка видаляє клієнта зі списку при відключенні."""
        self.clients.remove(ws)
        logging.info(f"{ws.remote_address} відключився")
        await self.send_to_clients(f"🚪 {ws.name} покинув чат.")

    async def send_to_clients(self, message: str):
        """Створимо функцію, яка розсилає повідомлення абсолютно всім підключеним клієнтам."""
        if self.clients:
            await asyncio.gather(*(client.send(message) for client in self.clients))

    async def process_exchange_command(self, ws: ServerConnection, message: str):
        """Створимо функцію, яка містить логіку обробки спеціальної команди exchange від користувача."""
        parts = message.split()
        days = 1  # Кількість днів за замовчуванням

        # Якщо користувач ввів параметр, наприклад 'exchange 3'
        if len(parts) > 1:
            try:
                days = int(parts[1])
            except ValueError:
                await ws.send(
                    "🤖 Бот: Невірний формат. Використовуйте: exchange або exchange <число>"
                )
                return

        # Перевірка обмежень
        if days > 10 or days < 1:
            await ws.send("🤖 Бот: Можна отримати курс лише за останні 1-10 днів.")
            return

        # 1. Показуємо усім в чаті сам запит користувача
        await self.send_to_clients(f"💬 {ws.name}: {message}")

        # 2. Асинхронно записуємо цей факт у файл логів (Завдання 3)
        await self.log_exchange_command(ws.name, days)

        # 3. Звертаємось до API ПриватБанку
        exchange_response = await self.exchange_service.get_exchange_for_chat(days)

        # 4. Відправляємо результат у чат від імені Бота
        await self.send_to_clients(f"🤖 Бот (на запит {ws.name}): {exchange_response}")

    async def distrubute(self, ws: ServerConnection):
        """Створимо функцію, яка слухає вхідні повідомлення та перевіряє, чи не є вони командами."""
        async for message in ws:
            # Перевірка на команду 'exchange'
            if message.lower().startswith("exchange"):
                await self.process_exchange_command(ws, message)
            else:
                # Це звичайне текстове повідомлення
                await self.send_to_clients(f"💬 {ws.name}: {message}")

    async def ws_handler(self, ws: ServerConnection):
        """Створимо функцію, яка визначає життєвий цикл підключення одного клієнта."""
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass  # Клієнт коректно відключився
        finally:
            await self.unregister(ws)


async def main():
    """Створимо функцію, яка є точкою входу для запуску сервера."""
    server = Server()
    print("🚀 Сервер чату запущено на ws://localhost:8080")
    print("ℹ️ Доступні команди в чаті: exchange, exchange <дні>")

    # Підняття сервера на localhost:8080
    async with websockets.serve(server.ws_handler, "localhost", 8080):
        await asyncio.Future()  # Сервер працюватиме безкінечно


if __name__ == "__main__":
    import sys

    # Спеціальне налаштування для Windows (щоб не було помилок EventLoop)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
