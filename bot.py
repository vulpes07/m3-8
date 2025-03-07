import os
import asyncio
import re
import httpx
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")  

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def escape_markdown_v2(text: str) -> str:
    escape_chars = r"_*[\]()~`>#+-=|{}.!"
    return re.sub(f"([{escape_chars}])", r"\\\1", text)

async def ask_mistral(prompt: str):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-small",  
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 150
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            answer = response.json()["choices"][0]["message"]["content"].strip()
            return escape_markdown_v2(answer)
        except Exception as e:
            return escape_markdown_v2(f"Ошибка при получении ответа от Mistral: {e}")

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот с поддержкой Mistral AI. Напишите мне что-нибудь, и я попробую ответить.")

@dp.message()
async def handle_message(message: Message):
    user_text = message.text
    await message.answer("Подождите, я думаю...")
    answer = await ask_mistral(user_text)
    await message.answer(answer, parse_mode="MarkdownV2")

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())