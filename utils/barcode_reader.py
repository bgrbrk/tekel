import json, base64, urllib.parse
def isleme_al(s): return s.strip()
def fatura_qr_coz(payload):
    s=payload.strip()
    try:
        if s.startswith("{") and s.endswith("}"): return json.loads(s)
        if s.startswith("http"):
            qs=urllib.parse.urlparse(s).query; params=urllib.parse.parse_qs(qs)
            if "data" in params:
                raw=base64.urlsafe_b64decode(params["data"][0]+"===")
                return json.loads(raw.decode("utf-8"))
        if "items=" in s: return {"items": json.loads(s.split("items=",1)[1])}
    except Exception: pass
    return {"items":[]}
