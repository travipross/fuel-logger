FROM python:3.6

ENV FLASK_APP fuel_logger/fuel_logger.py

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt 

COPY fuel_logger fuel_logger
COPY boot.sh boot.sh

EXPOSE 8000
ENTRYPOINT [ "./boot.sh" ]