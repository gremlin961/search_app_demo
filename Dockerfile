FROM python:3.10-slim
WORKDIR /usr/src/app
COPY requirements.txt  ./
RUN pip install -r requirements.txt
RUN pip install --upgrade google-cloud-aiplatform
COPY . .
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
