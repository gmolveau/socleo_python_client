import hashlib
import hmac
import json
import os
import urllib.parse
from collections import namedtuple

import requests


class ApiClient:
    def __init__(self, base_url=None, version=None, api_key=None):
        self.api_key = api_key or os.environ["API_KEY"]
        self.base_url = base_url or os.environ["BASE_URL"]
        self.version = version or os.environ["VERSION"]
        self.user_api = version or os.environ["USER_API"]

    def calculate_sceau(self, params, param_order):
        # Concatenate the parameter values in the specified order with a "*"
        param_values = "*".join(params.get(param, "") for param in param_order)
        # Calculate the HMAC-SHA1
        sceau = hmac.new(
            self.api_key.encode(), param_values.encode(), hashlib.sha1
        ).hexdigest()
        return sceau

    def send_request(self, params, param_order):
        sceau = self.calculate_sceau(params, param_order)
        params["SCEAU"] = sceau
        encoded_params = urllib.parse.urlencode(params)
        print(encoded_params)
        response = requests.post(
            self.base_url,
            data=encoded_params,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        return response

    def get_produits(self, date, adresse_mail, date_livraison=""):
        params = {
            "VERSION": self.version,
            "USER_API": self.user_api,
            "DATE": date,
            "ACTION": "GET_PRODUITS",
            "ADRESSE_MAIL": adresse_mail,
        }
        if date_livraison:
            params["DATE_LIVRAISON"] = date_livraison

        param_order = [
            "VERSION",
            "USER_API",
            "DATE",
            "ACTION",
            "DATE_LIVRAISON",
            "ADRESSE_MAIL",
        ]

        response = self.send_request(params, param_order)
        response_data = urllib.parse.parse_qs(response.text)
        ProduitsResponse = namedtuple(
            "ProduitsResponse", ["CODE_RETOUR", "PRODUITS", "FOURNISSEURS", "SCEAU"]
        )
        produits_response = ProduitsResponse(
            CODE_RETOUR=response_data.get("CODE_RETOUR", [None])[0],
            PRODUITS=json.loads(response_data.get("PRODUITS", [None])[0])
            if response_data.get("PRODUITS")
            else None,
            FOURNISSEURS=json.loads(response_data.get("FOURNISSEURS", [None])[0])
            if response_data.get("FOURNISSEURS")
            else None,
            SCEAU=response_data.get("SCEAU", [None])[0],
        )

        return produits_response


# Example usage
if __name__ == "__main__":
    client = ApiClient()
    date = "31/03/2025"
    mail = "abc@example.com"
    response = client.get_produits(date, mail)
    print(response)
