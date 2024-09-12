FROM python:3.12-slim
WORKDIR /code
RUN pip3 install poetry
COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock
RUN poetry install
COPY ./app /code/app
CMD ["poetry", "run", "python3", "-m", "fastapi", "run", "app/main.py", "--port", "8000"]