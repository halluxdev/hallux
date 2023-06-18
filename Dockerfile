FROM python:3.8-slim

WORKDIR /worker

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "main.py"]
