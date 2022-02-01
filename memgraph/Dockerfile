FROM memgraph/memgraph-mage:1.1-dev

USER root

# Install pip packages
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# Copy the local query modules and data import files
COPY transformations/ /usr/lib/memgraph/query_modules
COPY query_modules/ /usr/lib/memgraph/query_modules

COPY import-data/RNA_tweets_hashed_2012.csv /usr/lib/memgraph/import-data/RNA_tweets_hashed_2012.csv
USER memgraph
