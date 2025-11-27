# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime, timedelta
import json

from models import Session, Schedule, ScheduleChange, Subject
from gigachat_integration import GigaChatHelper, SCHEDULE_QUERY_PROMPT, CHANGE_DETECTION_PROMPT, LOAD_ANALYSIS_PROMPT

# Конфигурация
BOT_TOKEN = "7743746871:AAGy0h63RtGbrf9JnTk9ymFm_PP7HjRKvSQ"
GIGACHAT_CREDENTIALS = {
    "client_id": "019abc45-e032-76bf-a9bf-5de09acd1c4e",
    "secret": "GIGACHAT_API_PERS"
}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
giga = GigaChatHelper(GIGACHAT_CREDENTIALS)

# Клавиатура с быстрыми командами
def get_main_keyboard():
    keyboard = [
        [types.KeyboardButton(text="Следующий урок"), types.KeyboardButton(text="Расписание на завтра")],
        [types.KeyboardButton(text="Что задали?"), types.KeyboardButton(text="Отправить замену 📷")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я твой школьный помощник. 🤖\n"
        "Спроси меня о расписании, заменах или учебной нагрузке!",
        reply_markup=get_main_keyboard()
    )

# Обработка текстовых запросов (основная логика)
@dp.message(F.text)
async def handle_text_message(message: Message):
    user_question = message.text
    db_session = Session()

    try:
        # 1. Получаем актуальные данные из БД
        today = datetime.now().strftime("%A").lower() # 'monday'
        schedule_data = get_formatted_schedule(db_session, today)
        changes_data = get_todays_changes(db_session)

        # 2. Формируем промпт для GigaChat
        system_prompt = SCHEDULE_QUERY_PROMPT.format(
            schedule_data=schedule_data,
            changes_data=changes_data,
            user_question=user_question
        )

        # 3. Получаем ответ от GigaChat
        response = giga.get_completion(system_prompt, user_question)
        await message.answer(response)

    except Exception as e:
        logging.error(f"Error: {e}")
        await message.answer("Произошла ошибка. Попробуй еще раз.")
    finally:
        db_session.close()

# Обработка фотографий (замены из чатов)
@dp.message(F.photo)
async def handle_photo_message(message: Message):
    # 1. Скачиваем фото
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    # 2. Сохраняем и обрабатываем OCR (Tesseract/EasyOCR)
    # ... (код для OCR)
    extracted_text = "Текст, распознанный с картинки"

    if not extracted_text.strip():
        await message.answer("Не удалось распознать текст на фото.")
        return

    # 3. Анализируем текст через GigaChat на предмет замен
    change_json = giga.get_completion("", CHANGE_DETECTION_PROMPT.format(message_text=extracted_text))
    
    try:
        change_data = json.loads(change_json)
        # 4. Сохраняем замену в БД
        save_schedule_change(change_data)
        await message.answer("✅ Замена в расписании учтена! Спасибо.")
    except:
        # 5. Если GigaChat не нашел замену, пересылаем текст в общий обработчик
        await handle_text_message(types.Message(text=extracted_text))

# Функция для анализа нагрузки (Блок "Анти-выгорание")
@dp.message(F.text == "Что задали?")
async def handle_homework_planning(message: Message):
    db_session = Session()
    try:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%A").lower()
        schedule_data = get_formatted_schedule(db_session, tomorrow)
        
        # Получаем сложности предметов
        subjects = db_session.query(Subject).all()
        complexity_map = {subj.name: subj.complexity for subj in subjects}
        
        advice = giga.get_completion("", LOAD_ANALYSIS_PROMPT.format(
            schedule_data=schedule_data,
            subjects_complexity=str(complexity_map)
        ))
        await message.answer(advice)
    finally:
        db_session.close()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())