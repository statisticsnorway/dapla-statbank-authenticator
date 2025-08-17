FROM python:3.14.0rc2-alpine

# Setup env
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=on

# Setup user & workspace
ENV UID="1000"
ENV USERNAME="statbank-authenticator"
ENV GROUPNAME="statbank-auth"
ENV HOME="/home/$USERNAME"

RUN addgroup -S $GROUPNAME && \
    adduser -S $USERNAME -G $GROUPNAME -u $UID

RUN apk update && apk upgrade && \
    apk add gcc git curl linux-headers musl-dev libffi-dev

# The user needs to be able to write to this directory so that
# poetry can create a venv cache here
RUN mkdir -m 777 "$HOME/.cache" || chmod 777 "$HOME/.cache"

USER $UID
WORKDIR "/home/$USERNAME"

RUN pip install --upgrade pip && \
    pip install poetry

ENV PATH="$HOME/.local/bin:$PATH"

COPY . .

RUN poetry install --no-interaction --only main

EXPOSE 8080

ENTRYPOINT [ "poetry", "run", "gunicorn", "app.main:app", "-b", "0.0.0.0:8080", "-w", "1","-k", "uvicorn.workers.UvicornWorker", "-t", "0", "--log-config", "app/logging.config", "--log-level", "info"]
