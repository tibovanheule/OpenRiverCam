FROM python:3.11.12-slim-bookworm

COPY requirements.txt /app/
WORKDIR /app

RUN apt-get -y update && apt-get -y install git
RUN pip install --upgrade pip \
    &&  pip install --trusted-host pypi.python.org --requirement requirements.txt

CMD ["python", "-u", "main.py"]
# Use empty entry point to prevent container restarts while developing.
#ENTRYPOINT ["tail", "-f", "/dev/null"]
