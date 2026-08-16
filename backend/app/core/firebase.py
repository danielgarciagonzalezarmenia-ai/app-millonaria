"""Cliente de Firebase Admin SDK para Firestore y Auth.

Solo se usa desde el backend (nunca desde el navegador).
Requiere configurar GOOGLE_APPLICATION_CREDENTIALS con el path del archivo
JSON del service account (descargado desde la consola de Firebase).
"""

from __future__ import annotations

import os

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Carga backend/.env (si existe) para que os.environ tenga las credenciales
# aunque el proceso no haya recibido las variables por el entorno.
load_dotenv()

_initialized = False


def _ensure_initialized() -> None:
    global _initialized
    if _initialized:
        return
    if os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH"):
        cred = credentials.Certificate(
            os.environ["FIREBASE_SERVICE_ACCOUNT_PATH"]
        )
    elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        cred = credentials.ApplicationDefault()
    else:
        raise RuntimeError(
            "Falta credenciales Firebase. Define FIREBASE_SERVICE_ACCOUNT_PATH "
            "(recomendado) o GOOGLE_APPLICATION_CREDENTIALS con el JSON del "
            "service account."
        )
    firebase_admin.initialize_app(
        cred,
        options={"projectId": os.environ.get("FIREBASE_PROJECT_ID", "")} or None,
    )
    _initialized = True


def get_app() -> firebase_admin.App:
    _ensure_initialized()
    return firebase_admin.get_app()


def db() -> firestore.Client:
    return firestore.client(app=get_app())