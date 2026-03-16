FROM python:3.13
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./core ./core
COPY ./models ./models
COPY ./database ./database
COPY ./main.py .
CMD ["python", "main.py"]