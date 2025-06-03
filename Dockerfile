FROM python:3.13-slim

RUN pip install poetry

COPY pyproject.toml poetry.lock /src/  

WORKDIR /src

RUN poetry config virtualenvs.create false && poetry install --no-root 

COPY . /src 

CMD ["poetry", "run", "python", "src/main.py"]