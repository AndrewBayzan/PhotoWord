import os
from app import create_app

try:
    if os.environ.get('CHECK_ENV', 'False') == 'True':
        from check_env import check_env_vars
        check_env_vars()
except Exception as e:
    print(f"Warning: Environment check failed: {e}")

app = create_app()

if __name__ == "__main__":
    app.run()