FROM python:3.8

# Install CMake for gqlalchemy
RUN apt-get update && \
  apt-get --yes install cmake && \
  rm -rf /var/lib/apt/lists/*

# Install packages
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY stream.py /app/stream.py

COPY RNA_tweets_hashed_2013-2019.csv /app/RNA_tweets_hashed_2013-2019.csv
COPY RNA_0621_tweets_csv_hashed_2017.csv /app/RNA_0621_tweets_csv_hashed_2017.csv

WORKDIR /app
