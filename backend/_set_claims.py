import sys
sys.path.insert(0, ".")
from app.core import firebase
from firebase_admin import auth
import datetime as dt

UID = "8sUfJgLES3ZXzmgKOxjaIY0KKFC3"

# Claims a establecer
claims = {
    "admin": True,
    "premium": True,
    "premium_until": (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=3650)).isoformat(),
}

auth.set_custom_user_claims(UID, claims, app=firebase.get_app())
print(f"Claims actualizados para {UID}:")
print(f"  admin: {claims['admin']}")
print(f"  premium: {claims['premium']}")
print(f"  premium_until: {claims['premium_until']}")

# Verificar
user = auth.get_user(UID, app=firebase.get_app())
print(f"\nVerificacion - claims actuales: {user.custom_claims}")
