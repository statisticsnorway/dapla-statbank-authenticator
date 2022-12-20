import logging.config
import os

from fastapi import Depends, FastAPI, HTTPException
from pythonjsonlogger import jsonlogger
from prometheus_fastapi_instrumentator import Instrumentator
from app import __version__
from app.types import EncryptionRequest, EncryptionResponse
from aes_pkcs5.algorithms.aes_ecb_pkcs5_padding import AESECBPKCS5Padding
from google.cloud.secretmanager import SecretManagerServiceClient

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


def get_sm_client() -> SecretManagerServiceClient:
    try:
        return SecretManagerServiceClient()
    except:
        logger.info("Secret Manager Client is not available")


@app.post("/encrypt", status_code=200, response_model=EncryptionResponse)
def encrypt(request: EncryptionRequest, sm_client: SecretManagerServiceClient = Depends(get_sm_client)):
    """Encrypts a message with a given key. Uses AES with CBC/ECB mode and padding scheme PKCS5."""
    if 'CIPHER_KEY' not in os.environ:
        error_msg = 'Missing environment variable: CIPHER_KEY'
        logger.exception("Error occurred: %s", error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

    cipher_key = os.environ['CIPHER_KEY']
    # The cipher key can either be stored directly in the environment variable, or via Secret Manager
    if cipher_key.startswith(SECRET_MANAGER_PREFIX):
        project_id, secret_id, version = get_project_and_name(cipher_key)
        # Build the resource name of the secret version.
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
        # Access the secret version.
        response = sm_client.access_secret_version(request={"name": name})
        cipher_key = response.payload.data.decode("UTF-8")

    if len(cipher_key) != 16:
        error_msg = 'CIPHER_KEY must be of length 16'
        logger.exception("Error occurred: %s", error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    cipher = AESECBPKCS5Padding(cipher_key, "b64")
    return {
        "message": cipher.encrypt(request.message)
    }


@app.on_event("startup")
def app_startup():
    """Does some initial startup stuff"""
    logger.info(f"Starting Statbank Authenticator version {__version__} ...")


def get_project_and_name(env_var_value: str) -> (str, str, str):
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

    # Split [PROJECT]/[NAME]#[VERSION]
    splitted = without_prefix.split("/", 1)

    if splitted[1] == "":
        log_msg = f"No name defined in {env_var_value}"
        logging.error(log_msg)
        raise EnvironmentError(log_msg)

    # Split optional VERSION part
    if "#" in splitted[1]:
        return splitted[0], *splitted[1].split("#", 1)
    else:
        return splitted[0], splitted[1], 'latest'
