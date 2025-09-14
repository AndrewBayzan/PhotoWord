from werkzeug.security import check_password_hash, generate_password_hash

# Этот файл больше не определяет модели SQLAlchemy, так как мы используем Supabase REST API
# Оставляем только вспомогательные функции для работы с паролями

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)
    