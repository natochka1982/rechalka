# models.py
from sqlalchemy import Column, Integer, String, Date, Time, Boolean, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Subject(Base):
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False) # "Математика"
    complexity = Column(Integer, default=3) # Сложность от 1 до 5

class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(Integer, primary_key=True)
    day_of_week = Column(String, nullable=False) # "monday", "tuesday"
    lesson_number = Column(Integer, nullable=False) # 1, 2, 3...
    subject_id = Column(Integer, nullable=False) # Ссылка на Subject
    classroom = Column(String) # "205"
    teacher = Column(String) # "Иванова М.И."
    is_active = Column(Boolean, default=True) # Активен ли урок (не отменен)

class ScheduleChange(Base):
    __tablename__ = 'schedule_changes'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False) # Дата, на которую действует замена
    original_lesson_id = Column(Integer) # Ссылка на Schedule.id
    new_subject_id = Column(Integer, nullable=True) # Если subject поменялся
    new_classroom = Column(String, nullable=True) # Если кабинет поменялся
    is_cancelled = Column(Boolean, default=False) # Если урок отменен
    source_text = Column(String) # Исходный текст, из которого извлекли замену

# Инициализация БД
engine = create_engine('sqlite:///school_bot.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)