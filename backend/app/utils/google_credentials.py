import os
import json
from tempfile import NamedTemporaryFile
# =====================================
# Função auxiliar para criar credenciais temporárias
# =====================================
def build_credentials_file():
    creds_dict = {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "project_id": os.getenv("GOOGLE_PROJECT_ID", "sdr-agendamento"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uris": ["http://localhost:8080/"]
        }
    }

    temp_file = NamedTemporaryFile(delete=False, suffix=".json")
    with open(temp_file.name, "w") as f:
        json.dump(creds_dict, f)

    return temp_file.name
