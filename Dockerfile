FROM python:3.12.0a1-alpine

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PIP_DISABLE_PIP_VERSION_CHECK=on

RUN apk update && apk upgrade && \
    apk add gcc git curl linux-headers musl-dev libffi-dev

RUN pip install --upgrade pip && \
    pip install poetry

COPY . ./

RUN poetry install --no-interaction --no-dev

EXPOSE 8080
ENTRYPOINT [ "poetry", "run", "gunicorn", "app.main:app", "-b", "0.0.0.0:8080", "-w", "1","-k", "uvicorn.workers.UvicornWorker", "-t", "0", "--log-config", "app/logging.config", "--log-level", "info"]
