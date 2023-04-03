FROM python:3-alpine3.10
WORKDIR /app
COPY . /app
RUN p install -r requirements.txt
EXPOSE 5000
CMD python ./app.py
