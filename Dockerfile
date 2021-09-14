FROM python:3.7

COPY ./shotgrid_leecher /app/shotgrid_leecher
COPY ./poetry.toml /app/
COPY ./pyproject.toml /app/

WORKDIR /app



RUN pip install "poetry==1.1.8"\

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

CMD ["uvicorn", "--reload", "--host=0.0.0.0", "--port=9001", "shotgrid_leecher.main:app"]
