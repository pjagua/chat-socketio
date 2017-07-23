FROM python:3

WORKDIR /usr/src/app
COPY requirements.txt ./
COPY . .
RUN pip install --no-cache-dir -r requirements.txt -e ChatApp
ENV FLASK_APP=chatapp
CMD ["flask", "run", "--host=0.0.0.0"]
