FROM python:3.10

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем ВСЕ файлы из текущей папки в контейнер
COPY . .

# Устанавливаем зависимости (из requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем приложение
CMD ["python", "main.py"]
