# -*- coding: utf-8 -*-
import json, urllib.request, ssl
import database
API = "https://open.er-api.com/v6/latest/TRY"
def guncelle():
    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(API, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        rates = data.get("rates", {})
        out = {"USD": float(rates.get("USD", 0.0)),
               "EUR": float(rates.get("EUR", 0.0)),
               "GBP": float(rates.get("GBP", 0.0))}
        out = {k:v for k,v in out.items() if v>0}
        if out: database.kurlari_kaydet(out)
        return out
    except Exception:
        return {}
