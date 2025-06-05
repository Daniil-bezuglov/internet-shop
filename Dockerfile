# Используем официальный Python-образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости
RUN pip install --upgrade pip && \
    pip install -r requirements.txt


# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["gunicorn", "shop.wsgi", "--bind", "0.0.0.0:8000"] 