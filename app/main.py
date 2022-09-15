import logging.config
import os

from fastapi import FastAPI, HTTPException
from pythonjsonlogger import jsonlogger
from prometheus_fastapi_instrumentator import Instrumentator
from app import __version__
from app.types import EncryptionRequest, EncryptionResponse
from aes_pkcs5.algorithms.aes_ecb_pkcs5_padding import AESECBPKCS5Padding

app = FastAPI()

# Logging
# Get the loghandler and rename the field "levelname" to severity
# for correct display of log level in Google Logging
logger = logging.getLogger()
handler = logger.handlers[0]
formatter = jsonlogger.JsonFormatter(
    "%(asctime)s %(levelname)s %(threadName) %(module) %(funcName)s %(lineno)d  %(message)s",
    rename_fields={"levelname": "severity"},
)
logger.handlers[0].setFormatter(formatter)

# Metrics
Instrumentator(excluded_handlers=["/health/.*", "/metrics"]).instrument(app).expose(app)


@app.get("/health/ready", status_code=200)
def ready():
    """Tells whether or not the app is ready to receive requests"""
    return "Ready!"


@app.get("/health/alive", status_code=200)
def alive():
    """Tells whether or not the app is alive"""
    return "Alive!"


@app.post("/encrypt", status_code=200, response_model=EncryptionResponse)
def encrypt(request: EncryptionRequest):
    """Encrypts a message with a given key. Uses AES with CBC/ECB mode and padding scheme PKCS5."""
    if 'CIPHER_KEY' not in os.environ:
        error_msg = 'Missing environment variable: CIPHER_KEY'
        logger.exception("Error occurred: %s", error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

    key = os.environ['CIPHER_KEY']
    if len(key) != 16:
        error_msg = 'CIPHER_KEY must be of length 16'
        logger.exception("Error occurred: %s", error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    cipher = AESECBPKCS5Padding(key, "b64")
    return {
        "message": cipher.encrypt(request.message)
    }


@app.on_event("startup")
def app_startup():
    """Does some initial startup stuff"""
    logger.info(f"Starting Statbank Authenticator version {__version__} ...")
