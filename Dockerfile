FROM python:3.12-slim
WORKDIR /code
COPY ./requirements-docker.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
CMD ["fastapi", "run", "app/main.py", "--port", "8000", "--workers", "3"]