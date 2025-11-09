# -*- coding: utf-8 -*-
import json, urllib.parse

def fatura_qr_coz(payload: str):
    payload = payload.strip()
    items = []
    try:
        obj = json.loads(payload)
        items = obj.get("items", [])
    except Exception:
        q = urllib.parse.urlparse(payload).query or payload
        qs = urllib.parse.parse_qs(q)
        raw = qs.get("items", [])
        if raw:
            try:
                items = json.loads(raw[0])
            except Exception:
                items = []
    norm = []
    for it in items:
        norm.append({
            "barcode": str(it.get("barcode","000000000000")),
            "name": it.get("name","Ürün"),
            "qty": float(it.get("qty",1)),
            "price": float(it.get("price",0)),
            "kdv": int(it.get("kdv", 20)),
            "category": it.get("category","Market")
        })
    return norm
