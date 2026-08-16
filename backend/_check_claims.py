import sys
sys.path.insert(0, ".")
from app.core import firebase
from firebase_admin import auth

UID = "8sUfJgLES3ZXzmgKOxjaIY0KKFC3"
user = auth.get_user(UID, app=firebase.get_app())
print(f"Email: {user.email}")
print(f"Claims: {user.custom_claims}")
