FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения
COPY . .

# Устанавливаем PYTHONPATH
ENV PYTHONPATH="/app${PYTHONPATH:+:$PYTHONPATH}"

# Команда для запуска приложения
CMD ["python", "app/app/main.py"]