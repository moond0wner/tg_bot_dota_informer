FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Создаем и активируем виртуальное окружение (опционально, но рекомендуется)
RUN python -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения
COPY . .

# Команда для запуска приложения
CMD ["python", "app/main.py"]