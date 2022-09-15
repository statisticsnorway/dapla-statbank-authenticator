export CIPHER_KEY=$1
poetry run gunicorn app.main:app -b 127.0.0.1:8080 -w 1 -k uvicorn.workers.UvicornWorker -t 0 --log-config app/logging.config --log-level debug
