# gigachat_integration.py
import requests
import json

class GigaChatHelper:
    def __init__(self, credentials):
        self.auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        self.credentials = credentials # client_id, secret
        self.access_token = None

    def _get_auth_token(self):
        # Получение JWT токена (упрощенно)
        data = {'scope': 'GIGACHAT_API_PERS'}
        r = requests.post(self.auth_url, data=data, auth=(self.credentials['client_id'], self.credentials['secret']), verify=False)
        return r.json()['access_token']

    def get_completion(self, system_prompt, user_prompt, temperature=0.1):
        # Системный промпт - КРИТИЧЕСКИ ВАЖЕН для предотвращения галлюцинаций
        if not self.access_token:
            self.access_token = self._get_auth_token()

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature, # Низкая температура для точности
            "max_tokens": 1024
        }

        response = requests.post(self.api_url, headers=headers, json=payload, verify=False)
        return response.json()['choices'][0]['message']['content']

# СИСТЕМНЫЕ ПРОМПТЫ (Основа точности бота)
SCHEDULE_QUERY_PROMPT = """
Ты - умный помощник для школьника. Ты отвечаешь на вопросы о расписании уроков.
Ты должен отвечать ТОЛЬКО на основе предоставленных данных. Если в данных нет информации для ответа, скажи "В расписании на этот вопрос нет информации".

Данные для ответа:
{schedule_data}

Правила:
1. Отвечай кратко, дружелюбно, по-деловому.
2. Не придумывай никакие уроки, кабинеты, времена.
3. Если урок отменен, сообщи об этом.
4. Учитывай замены: {changes_data}

Вопрос пользователя: {user_question}
"""

CHANGE_DETECTION_PROMPT = """
Ты анализируешь сообщение об изменении школьного расписания.
Извлеки из текста следующую информацию в формате JSON:
{{
  "date": "дата в формате YYYY-MM-DD (завтра, послезавтра, конкретная дата)",
  "original_subject": "название отменяемого/меняемого предмета",
  "action": "cancel|replace|move_classroom",
  "new_subject": "название нового предмета (если замена)",
  "new_classroom": "новый кабинет (если указан)"
}}

Если какую-то информацию извлечь нельзя, поставь null.
Текст сообщения: {message_text}
"""

LOAD_ANALYSIS_PROMPT = """
Проанализируй расписание ученика на завтра и дай рекомендацию по тайм-менеджменту.
Расписание: {schedule_data}
Сложность предметов: {subjects_complexity}

Рассчитай общую нагрузку (сумма сложностей всех уроков) и дай совет:
- Когда начать делать домашку.
- Когда лучше отдохнуть.
- Предупреди о сложных днях.

Будь дружелюбным и заботливым, как старший товарищ.
"""