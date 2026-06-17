FROM astral/uv:python3.14-trixie-slim
LABEL maintainer="Gergő Csókás <gergo.csokas@gmail.com>"

WORKDIR /code
COPY /app /code/app
COPY pyproject.toml /code/
COPY uv.lock /code/

RUN ["uv", "sync"]

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--no-access-log"]