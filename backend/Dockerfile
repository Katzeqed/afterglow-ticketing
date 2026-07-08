FROM python:3.12-slim

WORKDIR /app

# Зависимости ставим отдельным слоем — Docker кэширует его,
# пока requirements.txt не менялся (быстрая пересборка).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
