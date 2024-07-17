FROM python:3-alpine

WORKDIR /app

ENV PYTHONUNBUFFERED=1

VOLUME /maildir
VOLUME /faildir

COPY mailqueue.py ./

CMD ["./mailqueue.py"]

