# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем директорию для загружаемых изображений
RUN mkdir -p /app/recipe_images

# Открываем порт
EXPOSE 65432

# Команда для запуска приложения
CMD ["python", "app.py"]