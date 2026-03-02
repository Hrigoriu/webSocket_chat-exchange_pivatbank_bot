import argparse
import json
import logging
import asyncio
from datetime import datetime, timedelta
import sys
import aiohttp

# Налаштовуємо логування: виводимо тільки помилки
logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")


class PrivatBankAPI:
    """Створимо клас, який відповідає виключно за запити до API ПриватБанку."""

    BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates"

    async def fetch_rates(self, session: aiohttp.ClientSession, date: str) -> dict:
        """Створимо функцію, яка виконує асинхронний GET запит та повертає JSON."""
        url = f"{self.BASE_URL}?date={date}"
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                logging.error(f"Помилка API за {date}: Статус {response.status}")
                return None
        except Exception as e:
            logging.error(f"Мережева помилка при запиті за {date}: {e}")
            return None


class RateParser:
    """Створимо клас для фільтрації та структурування отриманих від банку даних."""

    def __init__(self, target_currencies: list):
        # Отримуємо список валют і переводимо у верхній регістр (eur -> EUR)
        self.target_currencies = [c.upper() for c in target_currencies]

    def parse(self, raw_data: dict) -> dict:
        """Створимо функцію, яка фільтрує та структурує отримані від банку дані."""
        if not raw_data or "exchangeRate" not in raw_data:
            return {}

        date = raw_data.get("date")
        result = {date: {}}

        for rate in raw_data["exchangeRate"]:
            currency = rate.get("currency")
            if currency in self.target_currencies:
                # Отримуємо значення, віддаючи перевагу готівковому курсу
                sale = rate.get("saleRate") or rate.get("saleRateNB")
                purchase = rate.get("purchaseRate") or rate.get("purchaseRateNB")
                result[date][currency] = {"sale": sale, "purchase": purchase}

        return result


class CurrencyApp:
    """Створимо клас Оркестратор: керує процесом отримання та обробки даних."""

    def __init__(self, api_client: PrivatBankAPI, parser: RateParser):
        self.api_client = api_client
        self.parser = parser

    def _generate_dates(self, days: int) -> list[str]:
        """Створимо функцію, яка генерує дати у потрібному банку форматі (ДД.ММ.РРРР)."""
        return [
            (datetime.today() - timedelta(days=i)).strftime("%d.%m.%Y")
            for i in range(days)
        ]

    async def get_rates_for_days(self, days: int) -> list[dict]:
        """Створимо функцію, яка паралельно виконує запити за всі дні та парсить їх."""
        dates = self._generate_dates(days)
        final_result = []

        async with aiohttp.ClientSession() as session:
            # Формуємо список корутин для паралельного виконання
            tasks = [self.api_client.fetch_rates(session, date) for date in dates]
            raw_responses = await asyncio.gather(*tasks)

            # Обробляємо отримані результати
            for raw_data in raw_responses:
                if raw_data:
                    parsed_data = self.parser.parse(raw_data)
                    if parsed_data:
                        final_result.append(parsed_data)
        return final_result


async def main():
    """Створимо функцію, яка є точкою входу для консольної утиліти."""

    # Використовуємо argparse для обробки параметрів з терміналу
    parser = argparse.ArgumentParser(description="Отримання курсу валют ПриватБанку.")

    # Аргумент кількості днів (за замовчуванням 1)
    parser.add_argument(
        "days", type=int, nargs="?", default=1, help="Кількість днів (від 1 до 10)"
    )

    # Додатковий аргумент -c або --currencies для списку валют (наприклад: -c EUR USD PLN)
    parser.add_argument(
        "-c",
        "--currencies",
        nargs="+",
        default=["EUR", "USD"],
        help="Список цільових валют",
    )

    args = parser.parse_args()

    # Перевірка обмеження на дні
    if args.days < 1 or args.days > 10:
        print("❌ Помилка: Можна дізнатися курс лише за останні 1-10 днів.")
        return

    # Ініціалізація залежностей
    api = PrivatBankAPI()
    rate_parser = RateParser(target_currencies=args.currencies)
    app = CurrencyApp(api_client=api, parser=rate_parser)

    print(f"🔄 Отримуємо курси {args.currencies} за останні {args.days} днів...")

    # Отримання та вивід результату
    results = await app.get_rates_for_days(args.days)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
