FROM ubuntu

RUN apt-get update
RUN apt-get install -y python-pip python-dev
RUN apt-get install -y python3-bs4
RUN apt-get install -y mongodb

WORKDIR /app

RUN pip install Flask
RUN pip install flask-cors
RUN pip install requests
RUN pip install BeautifulSoup4
RUN pip install lxml
RUN pip install pymongo

RUN mkdir -p /data/db

COPY app.py /app
COPY search.py /app
COPY app.sh /app

EXPOSE 5000
EXPOSE 27017

CMD ["bash", "app.sh"]
