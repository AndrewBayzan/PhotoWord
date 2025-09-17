import requests

class SupabaseAPI:
    def __init__(self, project_id, api_key):
        self.base_url = f"https://{project_id}.supabase.co"
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    def get(self, table, params=None):
        url = f"{self.base_url}/rest/v1/{table}"
        response = requests.get(url, headers=self.headers, params=params, verify=True)
        response.raise_for_status()
        return response.json()

    def post(self, table, data):
        url = f"{self.base_url}/rest/v1/{table}"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

# Настройки для users_db
users_db = SupabaseAPI(
    project_id="jygxlexanqgjjaefdale",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp5Z3hsZXhhbnFnamphZWZkYWxlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY3MjI3MTMsImV4cCI6MjA3MjI5ODcxM30.UefBS0u7CmYIYO8GRyWIJP5WVlv302_vBYx_bTtIz_U"
)

# Настройки для dictionary_db
dictionary_db = SupabaseAPI(
    project_id="pbctfoaejfliglkftmba",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBiY3Rmb2FlamZsaWdsa2Z0bWJhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1MzY1NzUsImV4cCI6MjA3MzExMjU3NX0.ckHP1AamrJrSnDR1e3lOkpzG_pz3pzXkqsAKjj4AnTo"
)
