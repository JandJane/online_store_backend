FROM jaredv/rq-docker:0.0.2
COPY . /app
WORKDIR /app
CMD rq worker -u redis://redis:6379
