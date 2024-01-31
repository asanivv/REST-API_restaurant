FROM python:3.10-slim

WORKDIR /home/app/restaurant

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /home/app/restaurant
RUN pip install --upgrade pip && python -m pip install -r requirements.txt

COPY .. /home/app/restaurant