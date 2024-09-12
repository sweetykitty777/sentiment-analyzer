FROM python:3.12-slim
WORKDIR /code
COPY ./requirements-docker.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app

COPY ./run.sh /code/run.sh
RUN chmod +x /code/run.sh

EXPOSE 8000

CMD ["/code/run.sh"]
