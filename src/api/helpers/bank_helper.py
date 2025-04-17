import requests
from datetime import datetime
import api.settings


class BankHelper:
    def __init__(self):
        self.base_url = "https://bankaccountdata.gocardless.com/api/v2"
        self.client_id = api.settings.CLIENT_ID
        self.client_secret = api.settings.CLIENT_SECRET
        self.access_token = None
        self.allowed_banks = [
            "PKO_BPKOPLPW",
            "SANDBOX-MBANK",
            "INGB_PLINGB22",
            "PKOB_PLPPKEPWW",
            "WBKP_PLWBKPLPP",
            "ALBP_PLALBPPLPW",
            "PPAB_PLPPABPLPK",
            "BIGB_PLBIGBPLPW",
            "AGRIPLPR",
            "CITBPLCXXXX",
            "EBOSPLPW",
            "NESBPLPW",
            "POCZPLP4",
        ]

    def get_token(self):
        token_url = f"{self.base_url}/token/new/"
        response = requests.post(
            token_url,
            json={"secret_id": self.client_id, "secret_key": self.client_secret},
        )

        if response.status_code == 200:
            self.access_token = response.json()["access"]
            return self.access_token
        else:
            raise Exception("Nie udało się uzyskać access tokenu.")

    def get_headers(self):
        if not self.access_token:
            self.get_token()

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def create_requisition(
        self,
        institution_id: str,
        uid: int,
        redirect_url: str = "https://harmoney.app/bank-connected",
    ):
        url = f"{self.base_url}/requisitions/"

        payload = {
            "redirect": redirect_url,
            "institution_id": institution_id,
            "reference": f"user-{uid}-{int(datetime.utcnow().timestamp())}",
            "user_language": "PL",
        }

        response = requests.post(url, headers=self.get_headers(), json=payload)

        if response.status_code == 201:
            data = response.json()
            return {"requisition_id": data["id"], "link": data["link"]}
        else:
            raise Exception("Błąd przy tworzeniu requisition.")

    def check_requisition_status(self, requisition_id: str):
        url = f"{self.base_url}/requisitions/{requisition_id}/"
        response = requests.get(url, headers=self.get_headers())

        if response.status_code == 200:
            return response.json()["status"]
        else:
            raise Exception("Błąd przy sprawdzaniu statusu requisition.")
