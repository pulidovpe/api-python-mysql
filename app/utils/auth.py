from passlib.apps import custom_app_context as pwd_context

def generate_password(password):
    return pwd_context.hash(password)

def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)
