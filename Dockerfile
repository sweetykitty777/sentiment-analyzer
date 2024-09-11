FROM python:3.12
ARG DATABASE_URL
ENV DATABASE_URL=$DB_URL
WORKDIR /code
RUN pip3 install poetry
COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock
RUN poetry install
COPY ./app /code/app
CMD ["poetry", "run", "fastapi", "run", "app/main.py", "--port", "8000"]