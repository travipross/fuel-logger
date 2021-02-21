FROM python:3.6

# Create non-root user
RUN adduser --disabled-password fuel_logger --group --system
WORKDIR /home/fuel_logger/

# Copy requirements list and install
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt 

# Copy applictation code and boot script
COPY fuel_logger fuel_logger 
COPY boot.sh boot.sh 

# Own files and assume user
RUN chown -R fuel_logger:fuel_logger ./
USER fuel_logger

# Set environment variables
ENV FLASK_APP fuel_logger/fuel_logger.py
ENV PATH="/home/fuel_logger/.local/bin:${PATH}"

# Indicate default port
EXPOSE 8000

CMD [ "./boot.sh" ]
