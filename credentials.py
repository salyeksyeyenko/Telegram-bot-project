from dotenv import load_dotenv # Библиотека для работы с переменными окружения
import os

load_dotenv() # Загружаем переменные из .env

ChatGPT_TOKEN = os.getenv("CHATGPT_TOKEN")
BOT_TOKEN = os.getenv("BOT_TOKEN")
