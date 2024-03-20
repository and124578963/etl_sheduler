FROM python:3.10-slim-bookworm
# Locale
RUN apt-get update && apt-get install -y locales vim less net-tools

RUN sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU:ru
ENV LC_LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8
ENV TZ "Europe/Moscow"


COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

COPY . /app
WORKDIR /app

ENTRYPOINT ["python", "main.py"]
