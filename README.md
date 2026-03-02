# 🏦 WebSocket Чат та Валютний Інформер ПриватБанку

Інтерактивний WebSocket-чат реального часу з вбудованим фінансовим ботом.  
Бот отримує актуальні та архівні курси готівкових валют через відкритий API ПриватБанку.

Проєкт також містить консольну утиліту (CLI) для швидкого отримання курсів прямо в терміналі.

---

## ✨ Основні можливості

### 💬 WebSocket-чат

- Обмін повідомленнями у реальному часі
- Підтримка декількох користувачів
- Автоматична генерація українських імен (Faker)

### 🤖 Фінансовий бот

- Команда `exchange`
- Отримання курсу за N днів (до 10)
- Вивід результату прямо в чат

### 🖥 Консольна утиліта (CLI)

- Отримання курсів через `cli.py`
- Підтримка вибору валют (`EUR`, `USD`, `PLN`, `CHF`)

### ⚡ Архітектура

- Асинхронні запити (`aiohttp`, `asyncio`)
- Неблокуюча робота сервера
- Логування у файл `exchange_commands.log`

---

## 🛠 Встановлення

### 1️⃣ Клонування репозиторію

```bash
git clone https://github.com/Hrigoriu/webSocket_chat-exchange_pivatbank_bot.git
cd webSocket_chat-exchange_pivatbank_bot
```

---

### 2️⃣ Створення віртуального середовища (обов’язково)

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Mac / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Після активації віртуального середовища у терміналі з’явиться позначка `(venv)`.

---

### 3️⃣ Встановлення залежностей

```bash
python -m pip install aiohttp websockets faker aiofile aiopath
```

---

### 4️⃣ Запуск сервера🚀 Використання

Проєкт має два незалежні режими роботи.

---

#### 🔹 Варіант A — Запуск WebSocket-чату

##### Запуск сервера

```bash
python server.py
```

Сервер стартує на порту `8080`.

Далі:

- Відкрийте `index.html` у браузері
- Для тесту відкрийте кілька вкладок

##### Команди в чаті

| Команда | Опис |

|----------|--------|`

| `exchange` | курс за поточний день |

| `exchange 3` | курс за 3 останні дні |

| `exchange N` | максимум 10 днів |

---

#### 🔹 Варіант B — Консольна утиліта (CLI)

##### Отримати курс за 2 дні

```bash
python cli.py 2
```

##### Отримати курс за 4 дні для конкретних валют

```bash
python cli.py 4 -c EUR USD PLN CHF
```

---

### 5️⃣📝 Логування

Кожен виклик команди `exchange` записується у файл:

`exchange_commands.log`

Файл автоматично створюється в корені проєкту.

---

## 🧩 Технології

- Python 3
- asyncio
- aiohttp
- websockets
- faker

---

## 📌 Автор

**Hrigoriu Programmer**  
GitHub: `https://github.com/Hrigoriu`

---

## 📄 Ліцензія

MIT License.

Copyright (c) 2023 Hrigoriu Programmer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
