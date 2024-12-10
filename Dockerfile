# Используем базовый образ Python 3.11
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы
COPY . .

# Устанавливаем дополнительные зависимости
RUN pip install matplotlib seaborn

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1

# Устанавливаем команду для запуска приложения
CMD ["python", "plot.py"]
