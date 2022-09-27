import logging.config
import os

from fastapi import FastAPI, HTTPException
from pythonjsonlogger import jsonlogger
from prometheus_fastapi_instrumentator import Instrumentator
from app import __version__
from app.types import EncryptionRequest, EncryptionResponse
from aes_pkcs5.algorithms.aes_ecb_pkcs5_padding import AESECBPKCS5Padding
from google.cloud import secretmanager
import google_crc32c

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

SECRET_MANAGER_PREFIX = "sm://"

@app.get("/health/liveness", status_code=200)
def health_liveness():
    """Tells whether or not the app is alive"""
    return {
        "name": "dapla-statbank-authenticator",
        "status": "UP"
    }


@app.get("/health/readiness", status_code=200)
def health_readiness():
    """Tells whether or not the app is ready to receive requests"""
    return {
        "name": "dapla-statbank-authenticator",
        "status": "UP"
    }


@app.post("/encrypt", status_code=200, response_model=EncryptionResponse)
def encrypt(request: EncryptionRequest):
    """Encrypts a message with a given key. Uses AES with CBC/ECB mode and padding scheme PKCS5."""
    if 'CIPHER_KEY' not in os.environ:
        error_msg = 'Missing environment variable: CIPHER_KEY'
        logger.exception("Error occurred: %s", error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

    if len(os.environ['CIPHER_KEY']) != 16:
        error_msg = 'CIPHER_KEY must be of length 16'
        logger.exception("Error occurred: %s", error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    cipher = AESECBPKCS5Padding(os.environ['CIPHER_KEY'], "b64")
    return {
        "message": cipher.encrypt(request.message)
    }


@app.on_event("startup")
def app_startup():
    """Does some initial startup stuff"""
    logger.info(f"Starting Statbank Authenticator version {__version__} ...")
    if 'CIPHER_KEY' not in os.environ:
        raise EnvironmentError('Missing environment variable: CIPHER_KEY')

    if os.environ['CIPHER_KEY'].startswith(SECRET_MANAGER_PREFIX):
        client = secretmanager.SecretManagerServiceClient()

        project_id, secret_id, version = _get_project_and_name(os.environ['CIPHER_KEY'])
        # Build the resource name of the secret version.
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"

        # Access the secret version.
        response = client.access_secret_version(request={"name": name})

        # Verify payload checksum.
        crc32c = google_crc32c.Checksum()
        crc32c.update(response.payload.data)
        if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
            logger.error("Data corruption detected. Invalid checksum.")
        else:
            logger.info(f"Replacing CIPHER_KEY from Secret Manager")
            os.environ['CIPHER_KEY'] = response.payload.data.decode("UTF-8")


def _get_project_and_name(env_var_value: str) -> (str, str, str):
    """
    Split the env_var_value into project ID, name and version, where env_var_value should match the
    Secret Manager pattern from Berglas environment variable reference syntax (see
    https://github.com/GoogleCloudPlatform/berglas/blob/main/doc/reference-syntax.md).
    :param env_var_value: should respect this pattern sm://[PROJECT]/[NAME]#[VERSION], <VERSION> is optional
    :return: the project ID, the name and the version
    :exception: When PROJECT and/or NAME is missing (pattern not respected)
    """

    without_prefix = env_var_value[len(SECRET_MANAGER_PREFIX):]
    if without_prefix == "":
        log_msg = f"No project ID and name defined in {env_var_value}"
        logging.error(log_msg)
        raise EnvironmentError(log_msg)

    splitted = without_prefix.split("/", 1)

    if splitted[1] == "":
        log_msg = f"No name defined in {env_var_value}"
        logging.error(log_msg)
        raise EnvironmentError(log_msg)

    if "#" in splitted[1]:
        return splitted[0], *splitted[1].split("#", 1)
    else:
        return splitted[0], splitted[1], 'latest'
