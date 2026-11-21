import os, time, uuid, hmac, hashlib, base64, requests

TOKEN = os.environ.get("SB_TOKEN", "").strip()
SECRET = os.environ.get("SB_SECRET", "").strip()
GSHEET_URL = os.environ.get("GSHEET_URL", "").strip()
IDS = [
    os.environ.get("ID_1", "").strip(),
    os.environ.get("ID_2", "").strip(),
    os.environ.get("ID_3", "").strip()
]

BASE_URL = "https://" + "://switch-bot.com" + "/v1.1/devices"

def get_headers():
    t = str(int(round(time.time() * 1000)))
    nonce = str(uuid.uuid4())
    string_to_sign = f"{TOKEN}{t}{nonce}".encode("utf-8")
    sign = base64.b64encode(hmac.new(SECRET.encode("utf-8"), string_to_sign, hashlib.sha256).digest()).decode("utf-8")
    return {
        "Authorization": TOKEN,
        "sign": sign,
        "t": t,
        "nonce": nonce,
        "Content-Type": "application/json; charset=utf8"
    }

payload = {}
for idx, dev_id in enumerate(IDS, start=1):
    time.sleep(1) # 1 sekunda przerwy, aby nie przekroczyć limitu zapytań na sekundę
    try:
        resp = requests.get(f"{BASE_URL}/{dev_id}/status", headers=get_headers())
        res = resp.json()
        print(f"Czujnik {idx} -> HTTP: {resp.status_code}, API: {res.get('statusCode')} ({res.get('message')})")
        if res.get("statusCode") == 100:
            payload[f"t{idx}"] = res["body"].get("temperature")
            payload[f"h{idx}"] = res["body"].get("humidity")
        else:
            payload[f"t{idx}"] = None
            payload[f"h{idx}"] = None
    except Exception as e:
        print(f"Czujnik {idx} -> Błąd: {type(e).__name__}")
        payload[f"t{idx}"] = None
        payload[f"h{idx}"] = None

r = requests.post(GSHEET_URL, json=payload)
print("Status Google Sheets:", r.status_code)
