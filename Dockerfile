FROM python:3.10-alpine3.18
WORKDIR /bots/new_students_bot
RUN pip install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip install aiogram==3.3.0
RUN pip install geopy==2.4.1
RUN pip install requests==2.31.0
RUN pip install beautifulsoup4==4.12.3
EXPOSE 5000
RUN chmod -R 755 .
COPY . .