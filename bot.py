import os
import telebot
import google.generativeai as genai
import time

# =============================
# 🔐 ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ (Render)
# =============================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise RuntimeError("❌ Нет TELEGRAM_TOKEN или GEMINI_API_KEY")

# =============================
# ⚙️ GEMINI
# =============================
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# =============================
# 🤖 TELEGRAM BOT
# =============================
bot = telebot.TeleBot(TELEGRAM_TOKEN)

SYSTEM_PROMPT = """
Ты — профессиональный фрилансер и HR-копирайтер.

На основе вакансии напиши ПРОДАЮЩИЙ отклик:
- 6–8 предложений
- уверенный стиль
- без воды и клише
- фокус на выгоде заказчика

В конце — призыв к диалогу.
"""

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет!\n\n"
        "Пришли текст вакансии — я напишу продающий отклик.\n\n"
        "📌 Просто скопируй вакансию и отправь сюда."
    )

@bot.message_handler(content_types=["text"])
def generate_reply(message):
    vacancy = message.text.strip()

    if len(vacancy) < 40:
        bot.reply_to(message, "❌ Слишком короткий текст вакансии.")
        return

    status = bot.reply_to(message, "⏳ Пишу отклик...")

    try:
        prompt = f"{SYSTEM_PROMPT}\n\nВакансия:\n{vacancy}"
        response = model.generate_content(prompt)

        if not response or not response.text:
            raise Exception("Пустой ответ от AI")

        bot.edit_message_text(
            response.text,
            message.chat.id,
            status.message_id
        )

    except Exception as e:
        bot.edit_message_text(
            f"❌ Ошибка:\n{e}",
            message.chat.id,
            status.message_id
        )

print("✅ Бот запущен")

while True:
    try:
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print("Ошибка, перезапуск через 5 сек:", e)
        time.sleep(5)
