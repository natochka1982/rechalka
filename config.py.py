# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('7743746871:AAGy0h63RtGbrf9JnTk9ymFm_PP7HjRKvSQ')
    GIGACHAT_CLIENT_ID = os.getenv('019abc45-e032-76bf-a9bf-5de09acd1c4e')
    GIGACHAT_SECRET = os.getenv('GIGACHAT_API_PERS')
    
    # Проверяем, что токены загружены
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не установлен в .env файле")