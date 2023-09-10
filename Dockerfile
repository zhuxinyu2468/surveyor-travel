# Dockerfile
FROM python:3.9

WORKDIR /usr/src/app

COPY surveyor-travel-algorithm/requirements.txt .

RUN pip install -r requirements.txt

COPY surveyor-travel-algorithm/ .

CMD ["python","optimise_travel.py"]

