FROM python:3.9
ENV .env
WORKDIR app/
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY bot .
CMD [ "python", "-m", "bot" ]
