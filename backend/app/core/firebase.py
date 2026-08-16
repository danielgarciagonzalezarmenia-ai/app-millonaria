"""Cliente de Firebase Admin SDK para Firestore y Auth.

Solo se usa desde el backend (nunca desde el navegador).
Requiere configurar GOOGLE_APPLICATION_CREDENTIALS con el path del archivo
JSON del service account (descargado desde la consola de Firebase).
"""

from __future__ import annotations

import base64
import json
import os
import tempfile

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Carga backend/.env (si existe) para que os.environ tenga las credenciales
# aunque el proceso no haya recibido las variables por el entorno.
load_dotenv()

_initialized = False


def _service_account_path() -> str:
    """Devuelve un path usable del service account, sea por archivo o base64."""
    path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH") or os.environ.get(
        "GOOGLE_APPLICATION_CREDENTIALS"
    )
    if path:
        return path
    b64 = os.environ.get("FIREBASE_SERVICE_ACCOUNT_BASE64")
    if b64:
        try:
            data = base64.b64decode(b64).decode("utf-8")
        except Exception:
            data = b64  # quizá ya vino en texto plano
        fd, tmp_path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(json.loads(data), f, ensure_ascii=False)
        return tmp_path
    return ""


def _ensure_initialized() -> None:
    global _initialized
    if _initialized:
        return
    path = _service_account_path()
    if path:
        cred = credentials.Certificate(path)
    else:
        raise RuntimeError(
            "Falta credenciales Firebase. Define FIREBASE_SERVICE_ACCOUNT_PATH, "
            "FIREBASE_SERVICE_ACCOUNT_BASE64 o GOOGLE_APPLICATION_CREDENTIALS "
            "con el JSON del service account."
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