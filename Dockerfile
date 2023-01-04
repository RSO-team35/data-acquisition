
FROM python:3.8-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

ENV DATA_KEEPING_IP 127.0.0.1:8000

EXPOSE 8000

ENTRYPOINT ["python3"]

CMD ["-m", "uvicorn", "scraper_app.main:app", "--host", "0.0.0.0","--root-path","/scraper"]
