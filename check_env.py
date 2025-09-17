import os

def check_env_vars():
    required_vars = {
        'DEBUG': os.environ.get('DEBUG', 'False'),
        'SECRET_KEY': os.environ.get('SECRET_KEY', None),
        'SUPABASE_USERS_URL': os.environ.get('SUPABASE_USERS_URL', None),
        'SUPABASE_USERS_KEY': os.environ.get('SUPABASE_USERS_KEY', None),
        'SUPABASE_DICT_URL': os.environ.get('SUPABASE_DICT_URL', None),
        'SUPABASE_DICT_KEY': os.environ.get('SUPABASE_DICT_KEY', None)
    }

    missing_vars = []
    using_defaults = []

    print("\n=== Environment Variables Check ===\n")

    for var_name, var_value in required_vars.items():
        if var_name in os.environ:
            print(f"✅ {var_name}: установлена")
        else:
            if var_value is None:
                missing_vars.append(var_name)
                print(f"❌ {var_name}: отсутствует")
            else:
                using_defaults.append(var_name)
                print(f"⚠️ {var_name}: используется значение по умолчанию")

    if missing_vars:
        print("\n⚠️ Отсутствующие переменные окружения:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nУстановите эти переменные окружения на Render в разделе Environment Variables")

    if using_defaults:
        print("\n⚠️ Переменные, использующие значения по умолчанию:")
        for var in using_defaults:
            print(f"   - {var}")
        print("\nРекомендуется установить эти переменные для production окружения")

if __name__ == "__main__":
    check_env_vars()