# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости и устанавливаем пакеты
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Создаём файлы данных (если их нет в репозитории — создаём пустые)
RUN mkdir -p text_data && \
    touch text_data/messages.txt text_data/faculties.txt \
          text_data/directions.txt text_data/instructors.docx \
          resumes.sql

# Запуск бота
CMD ["python", "main.py"]