# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('7743746871:AAGy0h63RtGbrf9JnTk9ymFm_PP7HjRKvSQ')
    GIGACHAT_CLIENT_ID = os.getenv('GIGACHAT_CLIENT_ID')
    GIGACHAT_SECRET = os.getenv('MDE5YWJjNDUtZTAzMi03NmJmLWE5YmYtNWRlMDlhY2QxYzRlOmRjOTk0NmUyLTNjYmUtNDdlYy04OGE4LTFhMzc3OGQxZTg4Mw==')
    
    # Проверяем, что токены загружены
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не установлен в .env файле")