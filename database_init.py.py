# database_init.py
from models import Base, engine, Session, Subject, Schedule
from datetime import datetime

def init_database():
    """Инициализация базы данных с тестовыми данными"""
    
    # Создаем таблицы
    Base.metadata.create_all(engine)
    db_session = Session()

    try:
        # Очищаем существующие данные (для чистого старта)
        db_session.query(Schedule).delete()
        db_session.query(Subject).delete()
        db_session.commit()

        # 1. Создаем предметы со сложностями (от 1 до 5)
        subjects_data = [
            # Легкие предметы (сложность 1-2)
            {"name": "Физкультура", "complexity": 1},
            {"name": "Музыка", "complexity": 1},
            {"name": "ИЗО", "complexity": 1},
            {"name": "Технология", "complexity": 2},
            {"name": "ОБЖ", "complexity": 2},
            
            # Средние предметы (сложность 3)
            {"name": "Русский язык", "complexity": 3},
            {"name": "Литература", "complexity": 3},
            {"name": "История", "complexity": 3},
            {"name": "Обществознание", "complexity": 3},
            {"name": "География", "complexity": 3},
            {"name": "Биология", "complexity": 3},
            {"name": "Английский язык", "complexity": 3},
            
            # Сложные предметы (сложность 4-5)
            {"name": "Алгебра", "complexity": 4},
            {"name": "Геометрия", "complexity": 4},
            {"name": "Физика", "complexity": 5},
            {"name": "Химия", "complexity": 5},
            {"name": "Информатика", "complexity": 4}
        ]

        subjects = {}
        for subj_data in subjects_data:
            subject = Subject(**subj_data)
            db_session.add(subject)
            db_session.flush()  # Получаем ID
            subjects[subj_data["name"]] = subject.id

        db_session.commit()

        # 2. Создаем расписание на 5 дней (Понедельник - Пятница)
        schedule_data = {
            "monday": [
                {"lesson_number": 1, "subject": "Алгебра", "classroom": "201", "teacher": "Иванова А.П."},
                {"lesson_number": 2, "subject": "Русский язык", "classroom": "305", "teacher": "Петрова М.И."},
                {"lesson_number": 3, "subject": "Физика", "classroom": "410", "teacher": "Сидоров В.С."},
                {"lesson_number": 4, "subject": "Английский язык", "classroom": "215", "teacher": "Кузнецова О.Л."},
                {"lesson_number": 5, "subject": "История", "classroom": "104", "teacher": "Николаев Д.К."},
                {"lesson_number": 6, "subject": "Физкультура", "classroom": "спортзал", "teacher": "Волков С.П."}
            ],
            "tuesday": [
                {"lesson_number": 1, "subject": "Геометрия", "classroom": "201", "teacher": "Иванова А.П."},
                {"lesson_number": 2, "subject": "Литература", "classroom": "305", "teacher": "Петрова М.И."},
                {"lesson_number": 3, "subject": "Химия", "classroom": "315", "teacher": "Федорова Л.М."},
                {"lesson_number": 4, "subject": "Биология", "classroom": "210", "teacher": "Громова Т.С."},
                {"lesson_number": 5, "subject": "Английский язык", "classroom": "215", "teacher": "Кузнецова О.Л."},
                {"lesson_number": 6, "subject": "География", "classroom": "108", "teacher": "Орлова Е.В."},
                {"lesson_number": 7, "subject": "Музыка", "classroom": "актовый зал", "teacher": "Соколова И.Р."}
            ],
            "wednesday": [
                {"lesson_number": 1, "subject": "Русский язык", "classroom": "305", "teacher": "Петрова М.И."},
                {"lesson_number": 2, "subject": "Алгебра", "classroom": "201", "teacher": "Иванова А.П."},
                {"lesson_number": 3, "subject": "Информатика", "classroom": "компьютерный класс", "teacher": "Тихонов А.Б."},
                {"lesson_number": 4, "subject": "История", "classroom": "104", "teacher": "Николаев Д.К."},
                {"lesson_number": 5, "subject": "Физкультура", "classroom": "спортзал", "teacher": "Волков С.П."},
                {"lesson_number": 6, "subject": "ОБЖ", "classroom": "112", "teacher": "Морозов П.Д."}
            ],
            "thursday": [
                {"lesson_number": 1, "subject": "Физика", "classroom": "410", "teacher": "Сидоров В.С."},
                {"lesson_number": 2, "subject": "Литература", "classroom": "305", "teacher": "Петрова М.И."},
                {"lesson_number": 3, "subject": "Химия", "classroom": "315", "teacher": "Федорова Л.М."},
                {"lesson_number": 4, "subject": "Обществознание", "classroom": "105", "teacher": "Зайцева Н.В."},
                {"lesson_number": 5, "subject": "Английский язык", "classroom": "215", "teacher": "Кузнецова О.Л."},
                {"lesson_number": 6, "subject": "Геометрия", "classroom": "201", "teacher": "Иванова А.П."}
            ],
            "friday": [
                {"lesson_number": 1, "subject": "Биология", "classroom": "210", "teacher": "Громова Т.С."},
                {"lesson_number": 2, "subject": "Русский язык", "classroom": "305", "teacher": "Петрова М.И."},
                {"lesson_number": 3, "subject": "География", "classroom": "108", "teacher": "Орлова Е.В."},
                {"lesson_number": 4, "subject": "Алгебра", "classroom": "201", "teacher": "Иванова А.П."},
                {"lesson_number": 5, "subject": "Технология", "classroom": "мастерская", "teacher": "Ковалев М.С."},
                {"lesson_number": 6, "subject": "ИЗО", "classroom": "художественный класс", "teacher": "Белова Л.К."},
                {"lesson_number": 7, "subject": "Классный час", "classroom": "305", "teacher": "Петрова М.И."}
            ]
        }

        # Добавляем расписание в БД
        for day, lessons in schedule_data.items():
            for lesson in lessons:
                schedule = Schedule(
                    day_of_week=day,
                    lesson_number=lesson["lesson_number"],
                    subject_id=subjects[lesson["subject"]],
                    classroom=lesson["classroom"],
                    teacher=lesson["teacher"],
                    is_active=True
                )
                db_session.add(schedule)

        db_session.commit()
        print("✅ База данных успешно инициализирована!")
        print("📚 Добавлено предметов:", len(subjects_data))
        
        total_lessons = sum(len(lessons) for lessons in schedule_data.values())
        print("📅 Добавлено уроков в расписание:", total_lessons)
        
        # Выводим статистику по дням
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
            day_lessons = len(schedule_data[day])
            print(f"   {day.capitalize()}: {day_lessons} уроков")

    except Exception as e:
        db_session.rollback()
        print(f"❌ Ошибка при инициализации БД: {e}")
    finally:
        db_session.close()

def check_database():
    """Проверка содержимого базы данных"""
    db_session = Session()
    
    try:
        print("\n" + "="*50)
        print("ПРОВЕРКА БАЗЫ ДАННЫХ")
        print("="*50)
        
        # Проверяем предметы
        subjects = db_session.query(Subject).all()
        print("\n📚 ПРЕДМЕТЫ (сложность):")
        for subject in subjects:
            print(f"   {subject.name}: {subject.complexity}/5")
        
        # Проверяем расписание по дням
        days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        print("\n📅 РАСПИСАНИЕ:")
        for day in days:
            lessons = db_session.query(Schedule).filter(Schedule.day_of_week == day).order_by(Schedule.lesson_number).all()
            print(f"\n   {day.upper()}:")
            for lesson in lessons:
                subject = db_session.query(Subject).get(lesson.subject_id)
                print(f"      {lesson.lesson_number}. {subject.name} - каб. {lesson.classroom} ({lesson.teacher})")
                
    except Exception as e:
        print(f"❌ Ошибка при проверке БД: {e}")
    finally:
        db_session.close()

if __name__ == "__main__":
    # Инициализируем базу данных
    init_database()
    
    # Проверяем результат
    check_database()