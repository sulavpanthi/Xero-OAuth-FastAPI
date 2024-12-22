FROM python:3.11-alpine

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

RUN dos2unix /usr/src/app/entrypoint.sh

RUN chmod +x /usr/src/app/entrypoint.sh

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
