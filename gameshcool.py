import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Фейковая база данных в памяти
class FakeDB:
    def __init__(self):
        self.users = {}
        self.subjects = [
            {'id': 1, 'name': 'Математика', 'emoji': '➗', 'description': 'Царица наук'},
            {'id': 2, 'name': 'Русский язык', 'emoji': '🔤', 'description': 'Великий и могучий'},
            {'id': 3, 'name': 'География', 'emoji': '🌍', 'description': 'Изучаем мир'},
            {'id': 4, 'name': 'Литература', 'emoji': '📚', 'description': 'Мир книг'}
        ]
        self.questions = {
            1: [
                {'id': 1, 'question': 'Сколько будет 7 × 8?', 'correct': '56', 'wrong': ['54', '58', '64']},
                {'id': 2, 'question': 'Чему равен корень из 169?', 'correct': '13', 'wrong': ['12', '14', '15']},
                {'id': 3, 'question': 'Решите: 45 ÷ 9 = ?', 'correct': '5', 'wrong': ['4', '6', '7']},
            ],
            2: [
                {'id': 1, 'question': 'В каком слове пишется "и" после "ц"?', 'correct': 'Цирк', 'wrong': ['Цыпленок', 'Цыган', 'Огурцы']},
                {'id': 2, 'question': 'Выберите правильный вариант:', 'correct': 'Прийти', 'wrong': ['Придти', 'Прийти', 'Притти']},
            ],
            3: [
                {'id': 1, 'question': 'Столица Австралии?', 'correct': 'Канберра', 'wrong': ['Сидней', 'Мельбурн', 'Перт']},
                {'id': 2, 'question': 'Самая длинная река в мире?', 'correct': 'Нил', 'wrong': ['Амазонка', 'Янцзы', 'Миссисипи']},
            ],
            4: [
                {'id': 1, 'question': 'Кто написал "Евгений Онегин"?', 'correct': 'Пушкин', 'wrong': ['Лермонтов', 'Гоголь', 'Тургенев']},
                {'id': 2, 'question': 'Автор романа "Преступление и наказание"?', 'correct': 'Достоевский', 'wrong': ['Толстой', 'Чехов', 'Гончаров']},
            ]
        }
    
    def get_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = {'rating': 1000, 'grades': [], 'games_played': 0}
        return self.users[user_id]
    
    def add_grade(self, user_id, subject_id, grade):
        user = self.get_user(user_id)
        user['grades'].append({'subject_id': subject_id, 'grade': grade})
        user['rating'] += 10 if grade == 5 else (5 if grade == 4 else (0 if grade == 3 else -5))
        user['games_played'] += 1
    
    def get_user_stats(self, user_id):
        user = self.get_user(user_id)
        stats = {}
        for grade in user['grades']:
            subject_id = grade['subject_id']
            if subject_id not in stats:
                stats[subject_id] = {'total': 0, 'count': 0}
            stats[subject_id]['total'] += grade['grade']
            stats[subject_id]['count'] += 1
        return stats
    
    def get_global_rating(self):
        users_list = []
        for user_id, user_data in self.users.items():
            users_list.append({
                'user_id': user_id,
                'rating': user_data['rating'],
                'games_played': user_data['games_played']
            })
        return sorted(users_list, key=lambda x: x['rating'], reverse=True)

db = FakeDB()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🏫 Начать учебный день", callback_data="start_day")],
        [InlineKeyboardButton("📊 Мой рейтинг", callback_data="my_rating")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"🎒 Добро пожаловать в школу, {user.first_name}!\n\nЗаходите в кабинеты и отвечайте на вопросы!",
        reply_markup=reply_markup
    )

async def show_corridor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for subject in db.subjects:
        keyboard.append([InlineKeyboardButton(f"{subject['emoji']} {subject['name']}", callback_data=f"class_{subject['id']}")])
    keyboard.append([InlineKeyboardButton("📊 Мой прогресс", callback_data="my_rating")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text("🏫 Вы в школьном коридоре. Выберите кабинет:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("🏫 Вы в школьном коридоре. Выберите кабинет:", reply_markup=reply_markup)

async def enter_classroom(update: Update, context: ContextTypes.DEFAULT_TYPE, subject_id: int):
    subject = next((s for s in db.subjects if s['id'] == subject_id), None)
    keyboard = [
        [InlineKeyboardButton("✏️ Начать урок", callback_data=f"start_lesson_{subject_id}")],
        [InlineKeyboardButton("🚪 В коридор", callback_data="corridor")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        f"{subject['emoji']} Кабинет {subject['name']}\n\n{subject['description']}",
        reply_markup=reply_markup
    )

async def start_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE, subject_id: int):
    questions = db.questions.get(subject_id, [])
    if not questions:
        await update.callback_query.edit_message_text("Вопросы пока не готовы!")
        return
    question = random.choice(questions)
    context.user_data['current_question'] = {'correct': question['correct'], 'subject_id': subject_id}
    answers = [question['correct']] + question['wrong']
    random.shuffle(answers)
    keyboard = [[InlineKeyboardButton(answer, callback_data=f"answer_{answer}")] for answer in answers]
    reply_markup = InlineKeyboardMarkup(keyboard)
    subject = next((s for s in db.subjects if s['id'] == subject_id), None)
    await update.callback_query.edit_message_text(f"{subject['emoji']} {subject['name']}\n\n📝 {question['question']}", reply_markup=reply_markup)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_answer = query.data.replace('answer_', '')
    if 'current_question' not in context.user_data:
        await query.edit_message_text("Ошибка!")
        return
    current_question = context.user_data['current_question']
    is_correct = user_answer == current_question['correct']
    grade = random.choice([4, 5, 5]) if is_correct else random.choice([2, 3, 3])
    user_id = query.from_user.id
    db.add_grade(user_id, current_question['subject_id'], grade)
    subject = next((s for s in db.subjects if s['id'] == current_question['subject_id']), None)
    grade_emoji = "🎉" if grade == 5 else "👍" if grade == 4 else "😐" if grade == 3 else "😔"
    message = f"{subject['emoji']} {subject['name']}\n\n{grade_emoji} Оценка: {grade}\n💡 Правильно: {current_question['correct']}"
    keyboard = [
        [InlineKeyboardButton("➡️ Следующий вопрос", callback_data=f"start_lesson_{current_question['subject_id']}")],
        [InlineKeyboardButton("🚪 В коридор", callback_data="corridor")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)

async def show_my_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    stats = db.get_user_stats(user_id)
    message = f"📊 Рейтинг: {user['rating']:.0f}\n🎮 Уроков: {user['games_played']}\n\n"
    for subject in db.subjects:
        if subject['id'] in stats:
            avg_grade = stats[subject['id']]['total'] / stats[subject['id']]['count']
            message += f"{subject['emoji']} {subject['name']}: {avg_grade:.1f}\n"
        else:
            message += f"{subject['emoji']} {subject['name']}: —\n"
    keyboard = [[InlineKeyboardButton("🏫 В коридор", callback_data="corridor")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "start_day" or data == "corridor":
        await show_corridor(update, context)
    elif data == "my_rating":
        await show_my_rating(update, context)
    elif data.startswith("class_"):
        subject_id = int(data.split("_")[1])
        await enter_classroom(update, context, subject_id)
    elif data.startswith("start_lesson_"):
        subject_id = int(data.split("_")[2])
        await start_lesson(update, context, subject_id)
    elif data.startswith("answer_"):
        await handle_answer(update, context)

def main():
    # ⚠️ ЗАМЕНИТЕ НА ВАШ РЕАЛЬНЫЙ ТОКЕН ⚠️
    TOKEN = "6963633234:AAHopvLbIRREhKyZgZAL6pFP9FwDhvSF3VM"
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("🚀 Бот запускается...")
    application.run_polling()

if __name__ == '__main__':
    main()