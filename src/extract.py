from dotenv import load_dotenv
import os
import http.client

load_dotenv()

def extract():
    conn = http.client.HTTPSConnection("api.collectapi.com")

    api_key = os.getenv("API_KEY")

    headers = {
        'content-type': "application/json",
        'authorization': f"apikey {api_key}"
        }

    conn.request("GET", "/gasPrice/stateUsaPrice?state=WA", headers=headers)

    res = conn.getresponse()
    data = res.read()
    return data