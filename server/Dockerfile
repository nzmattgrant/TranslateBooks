FROM python:3.10

COPY . /app
WORKDIR /app

ENV PORT 5000

RUN pip install --upgrade pip &&\
    pip install -r requirements.txt

CMD gunicorn --bind 0.0.0.0:$PORT app:app