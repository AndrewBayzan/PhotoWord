import os

class Config:
    # Application configuration
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'SOME_KEY')
    
    # Supabase configuration
    SUPABASE_USERS_URL = os.environ.get('SUPABASE_USERS_URL', 'jygxlexanqgjjaefdale')
    SUPABASE_USERS_KEY = os.environ.get('SUPABASE_USERS_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp5Z3hsZXhhbnFnamphZWZkYWxlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY3MjI3MTMsImV4cCI6MjA3MjI5ODcxM30.UefBS0u7CmYIYO8GRyWIJP5WVlv302_vBYx_bTtIz_U')
    
    SUPABASE_DICT_URL = os.environ.get('SUPABASE_DICT_URL', 'pbctfoaejfliglkftmba')
    SUPABASE_DICT_KEY = os.environ.get('SUPABASE_DICT_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBiY3Rmb2FlamZsaWdsa2Z0bWJhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1MzY1NzUsImV4cCI6MjA3MzExMjU3NX0.ckHP1AamrJrSnDR1e3lOkpzG_pz3pzXkqsAKjj4AnTo')
