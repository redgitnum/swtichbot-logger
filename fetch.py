import os, time, uuid, hmac, hashlib, base64, requests

TOKEN = os.environ["SB_TOKEN"]
SECRET = os.environ["SB_SECRET"]
GSHEET_URL = os.environ.get("GSHEET_URL", "")
IDS = [os.environ.get("ID_1"), os.environ.get("ID_2"), os.environ.get("ID_3")]

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

# Wypisz listę urządzeń w logach (pomocne przy pierwszym uruchomieniu)
devs = requests.get("https://switch-bot.com", headers=get_headers()).json()
if devs.get("statusCode") == 100:
    for d in devs["body"]["deviceList"]:
        print(f"Urządzenie: {d.get('deviceName')} | Typ: {d.get('deviceType')} | ID: {d.get('deviceId')}")

# Pobierz odczyty z 3 czujników i wyślij do Google Sheets
if all(IDS) and GSHEET_URL:
    payload = {}
    for idx, dev_id in enumerate(IDS, start=1):
        res = requests.get(f"https://switch-bot.com/{dev_id}/status", headers=get_headers()).json()
        if res.get("statusCode") == 100:
            payload[f"t{idx}"] = res["body"].get("temperature")
            payload[f"h{idx}"] = res["body"].get("humidity")
        else:
            payload[f"t{idx}"] = None
            payload[f"h{idx}"] = None
    r = requests.post(GSHEET_URL, json=payload)
    print("Status wysyłki do Google Sheets:", r.status_code, r.text)
