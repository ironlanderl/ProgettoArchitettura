FROM alpine:3.22.0

WORKDIR /app
COPY ../software /app

RUN apk add --no-cache python3 py3-pip
RUN pip3 install -r requirements.txt --break-system-packages

ENTRYPOINT ["python3", "-u", "test.py"]
