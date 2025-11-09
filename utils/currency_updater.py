import json, datetime, urllib.request
from database import baglan
API_URL = "https://open.er-api.com/v6/latest/TRY"

def kurlari_guncelle(api_url=API_URL):
    try:
        with urllib.request.urlopen(api_url, timeout=10) as r:
            data=json.loads(r.read().decode("utf-8"))
        if data.get("result")!="success":
            return False
        now=datetime.datetime.now().isoformat(timespec='seconds')
        conn=baglan(); c=conn.cursor()
        for cur in ("USD","EUR","GBP"):
            rate=data["rates"].get(cur)
            if rate:
                c.execute("INSERT INTO currency_rates(currency,rate_to_tl,last_update) VALUES(?,?,?)",(cur,float(rate),now))
        conn.commit(); conn.close(); return True
    except Exception:
        return False

def son_kurlar():
    conn=baglan(); rows=conn.execute("SELECT currency,rate_to_tl,last_update FROM currency_rates WHERE id IN (SELECT MAX(id) FROM currency_rates GROUP BY currency)").fetchall(); conn.close()
    d={cur:(rate,lu) for cur,rate,lu in rows}
    return d
