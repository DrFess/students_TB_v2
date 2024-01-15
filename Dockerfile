FROM python:3.10-alpine3.18
WORKDIR /bots/new_students_bot
RUN pip install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip install aiogram==3.3.0
RUN pip install geopy==2.4.1
RUN chmod 755 .
COPY . .