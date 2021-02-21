FROM python:3.9

ENV FLASK_APP fuel_logger/fuel_logger.py
COPY boot.sh boot.sh

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt 

COPY fuel_logger fuel_logger

EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]