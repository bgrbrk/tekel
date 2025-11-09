# -*- coding: utf-8 -*-
import sqlite3, json, hashlib, datetime, os

DB_NAME = os.path.join(os.path.dirname(__file__), "turcotekel.db")

def _conn():
    return sqlite3.connect(DB_NAME)

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def kurulum():
    con = _conn(); cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT CHECK(role IN ('admin','kasiyer')) NOT NULL
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS suppliers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        address TEXT,
        balance_tl REAL DEFAULT 0
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        purchase_price_tl REAL DEFAULT 0,
        sale_price_tl REAL DEFAULT 0,
        kdv INTEGER DEFAULT 0,
        stock REAL DEFAULT 0,
        expiry_date TEXT,
        category TEXT,
        supplier_id INTEGER
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS purchases(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER,
        date TEXT NOT NULL,
        total_tl REAL NOT NULL,
        items_json TEXT NOT NULL
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS sales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        total_tl REAL NOT NULL,
        payment_type TEXT CHECK(payment_type IN ('cash','card')) NOT NULL,
        cashier_id INTEGER,
        items_json TEXT NOT NULL
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS supplier_ledger(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        type TEXT CHECK(type IN ('purchase','payment','refund')) NOT NULL,
        amount_tl REAL NOT NULL,
        note TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS cash_register(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT UNIQUE NOT NULL,
        opening_balance_tl REAL DEFAULT 0,
        closing_balance_tl REAL DEFAULT 0,
        sales_total_tl REAL DEFAULT 0,
        expenses_tl REAL DEFAULT 0,
        note TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS currency_rates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        currency TEXT NOT NULL,
        rate_to_tl REAL NOT NULL,
        last_update TEXT NOT NULL
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS stock_movements(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        type TEXT CHECK(type IN ('in','out','adjust')) NOT NULL,
        qty REAL NOT NULL,
        ref TEXT,
        note TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS cash_movements(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        type TEXT CHECK(type IN ('income','expense')) NOT NULL,
        amount_tl REAL NOT NULL,
        note TEXT NOT NULL
    )""")

    # seeds
    cur.execute("SELECT COUNT(*) FROM users"); 
    if cur.fetchone()[0]==0:
        cur.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)", ("admin", _sha256("admin"), "admin"))
        cur.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)", ("kasiyer", _sha256("1234"), "kasiyer"))

    cur.execute("SELECT COUNT(*) FROM suppliers")
    if cur.fetchone()[0]==0:
        cur.execute("INSERT INTO suppliers(name,phone,address,balance_tl) VALUES(?,?,?,?)", ("Örnek Tedarik", "555-000-11-22", "İstanbul", 0))

    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0]==0:
        demo = [
            ("869000000001", "Aqua Su 0.5L", 5.0, 10.0, 10, 100, None, "Alkolsüz", 1),
            ("869000000002", "Kola 1L", 10.0, 25.0, 10, 50, None, "Alkolsüz", 1),
            ("869000000003", "Marlboro Kutu", 70.0, 90.0, 20, 200, None, "Sigara", 1),
            ("869000000004", "Bira 50cl", 25.0, 45.0, 20, 80, None, "Alkollü", 1),
            ("869000000005", "Cips 100g", 8.0, 18.0, 10, 60, None, "Market", 1),
        ]
        for b,name,pp,sp,kdv,st,exp,cat,sup in demo:
            cur.execute("""INSERT INTO products(barcode,name,purchase_price_tl,sale_price_tl,kdv,stock,expiry_date,category,supplier_id)
                           VALUES(?,?,?,?,?,?,?,?,?)""", (b,name,pp,sp,kdv,st,exp,cat,sup))
        cur.execute("SELECT id, stock FROM products")
        for pid, st in cur.fetchall():
            if st>0:
                cur.execute("""INSERT INTO stock_movements(product_id,date,type,qty,ref,note)
                               VALUES(?,?,?,?,?,?)""", (pid, datetime.datetime.now().isoformat(timespec="seconds"), "in", st, "tohum", "İlk stok"))

    con.commit(); con.close()

def giris(username, password):
    con = _conn(); cur = con.cursor()
    cur.execute("SELECT id, username, role, password_hash FROM users WHERE username=?", (username,))
    row = cur.fetchone(); con.close()
    if not row: return None
    uid, uname, role, pwh = row
    return {"id": uid, "username": uname, "role": role} if hashlib.sha256(password.encode()).hexdigest()==pwh else None

def urun_barkod(barcode):
    con = _conn(); cur = con.cursor()
    cur.execute("""SELECT id, barcode, name, sale_price_tl, kdv, stock, supplier_id FROM products WHERE barcode=?""",(barcode,))
    r = cur.fetchone(); con.close()
    if not r: return None
    return {"id": r[0], "barcode": r[1], "name": r[2], "sale_price_tl": r[3], "kdv": r[4], "stock": r[5], "supplier_id": r[6]}

def urun_kaydet_veya_guncelle(barcode, name, sale_price_tl, kdv, category, purchase_price_tl=None, expiry_date=None, supplier_id=None):
    con = _conn(); cur = con.cursor()
    cur.execute("SELECT id FROM products WHERE barcode=?", (barcode,))
    row = cur.fetchone()
    if row:
        cur.execute("""UPDATE products SET name=?, sale_price_tl=?, kdv=?, category=?, purchase_price_tl=COALESCE(?,purchase_price_tl),
                       expiry_date=?, supplier_id=COALESCE(?, supplier_id) WHERE barcode=?""",
                    (name, sale_price_tl, kdv, category, purchase_price_tl, expiry_date, supplier_id, barcode))
        pid = row[0]
    else:
        cur.execute("""INSERT INTO products(barcode,name,purchase_price_tl,sale_price_tl,kdv,stock,expiry_date,category,supplier_id)
                       VALUES(?,?,?,?,?,?,?,?,?)""",
                    (barcode, name, purchase_price_tl or 0, sale_price_tl, kdv, 0, expiry_date, category, supplier_id))
        pid = cur.lastrowid
    con.commit(); con.close(); return pid

def stok_degistir(product_id, delta, mov_type, ref="manuel", note=""):
    con = _conn(); cur = con.cursor()
    cur.execute("UPDATE products SET stock=COALESCE(stock,0)+? WHERE id=?", (delta, product_id))
    cur.execute("""INSERT INTO stock_movements(product_id,date,type,qty,ref,note) VALUES(?,?,?,?,?,?)""",
                (product_id, datetime.datetime.now().isoformat(timespec="seconds"), mov_type, abs(delta), ref, note))
    con.commit(); con.close()

def satis_kaydet(cashier_id, items, total_tl, payment_type, fis_yaz=False):
    con = _conn(); cur = con.cursor()
    for it in items:
        cur.execute("UPDATE products SET stock=COALESCE(stock,0)-? WHERE id=?", (it["qty"], it["product_id"]))
        cur.execute("""INSERT INTO stock_movements(product_id,date,type,qty,ref,note) VALUES(?,?,?,?,?,?)""",
                    (it["product_id"], datetime.datetime.now().isoformat(timespec="seconds"), "out", it["qty"], "satis", f'Barkod:{it["barcode"]}'))
    items_json = json.dumps(items, ensure_ascii=False)
    cur.execute("""INSERT INTO sales(date,total_tl,payment_type,cashier_id,items_json) VALUES(?,?,?,?,?)""",
                (datetime.datetime.now().isoformat(timespec="seconds"), total_tl, payment_type, cashier_id, items_json))
    sale_id = cur.lastrowid
    con.commit(); con.close()
    if fis_yaz:
        path = os.path.join(os.path.dirname(__file__), f"fis_{sale_id}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("TURCO TEKEL - SATIŞ FİŞİ\n")
            f.write(f"İşlem No: {sale_id}\n")
            f.write("-"*32+"\n")
            for it in items:
                f.write(f'{it["name"]} x{it["qty"]} = {it["toplam"]:.2f} TL\n')
            f.write("-"*32+"\n")
            f.write(f"TOPLAM: {total_tl:.2f} TL\n")
    return sale_id

def kurlari_kaydet(rate_dict):
    now = datetime.datetime.now().isoformat(timespec="seconds")
    con = _conn(); cur = con.cursor()
    for ccy, rate in rate_dict.items():
        cur.execute("""INSERT INTO currency_rates(currency, rate_to_tl, last_update) VALUES(?,?,?)""", (ccy, rate, now))
    con.commit(); con.close()

def son_kurlar():
    con = _conn(); cur = con.cursor()
    out = {}
    for c in ("USD","EUR","GBP"):
        cur.execute("SELECT rate_to_tl,last_update FROM currency_rates WHERE currency=? ORDER BY id DESC LIMIT 1", (c,))
        r = cur.fetchone()
        if r: out[c] = {"rate_to_tl": r[0], "last_update": r[1]}
    con.close(); return out

def satınalma_kaydet_ve_cari_guncelle(supplier_id, items, total_tl):
    con = _conn(); cur = con.cursor()
    items_json = json.dumps(items, ensure_ascii=False)
    now = datetime.datetime.now().isoformat(timespec="seconds")
    cur.execute("INSERT INTO purchases(supplier_id,date,total_tl,items_json) VALUES(?,?,?,?)", (supplier_id, now, total_tl, items_json))
    pid = cur.lastrowid
    # ürün güncelle + stok hareketi
    for it in items:
        cur.execute("SELECT id FROM products WHERE barcode=?", (it["barcode"],))
        r = cur.fetchone()
        if r:
            pr_id = r[0]
            cur.execute("""UPDATE products SET name=?, purchase_price_tl=?, kdv=?, category=?, supplier_id=COALESCE(?,supplier_id) WHERE id=?""",
                        (it["name"], it["price"], it["kdv"], it.get("category","Market"), supplier_id, pr_id))
        else:
            cur.execute("""INSERT INTO products(barcode,name,purchase_price_tl,sale_price_tl,kdv,stock,category,supplier_id)
                           VALUES(?,?,?,?,?,?,?,?)""",
                        (it["barcode"], it["name"], it["price"], it["price"]*1.2, it["kdv"], 0, it.get("category","Market"), supplier_id))
            pr_id = cur.lastrowid
        cur.execute("UPDATE products SET stock=COALESCE(stock,0)+? WHERE id=?", (it["qty"], pr_id))
        cur.execute("""INSERT INTO stock_movements(product_id,date,type,qty,ref,note) VALUES(?,?,?,?,?,?)""",
                    (pr_id, now, "in", it["qty"], f"purchase#{pid}", f"Fatura/QR girişi - Tedarikçi:{supplier_id}"))
    # cari
    cur.execute("""INSERT INTO supplier_ledger(supplier_id,date,type,amount_tl,note) VALUES(?,?,?,?,?)""",
                (supplier_id, now, "purchase", total_tl, f"Fatura #{pid}"))
    cur.execute("UPDATE suppliers SET balance_tl = COALESCE(balance_tl,0)+? WHERE id=?", (total_tl, supplier_id))
    con.commit(); con.close()
    return pid

def tedarikci_listesi():
    con = _conn(); cur = con.cursor()
    cur.execute("SELECT id,name,balance_tl FROM suppliers ORDER BY name")
    rows = cur.fetchall(); con.close(); return rows

def ledger_for_supplier(supplier_id, start=None, end=None):
    con = _conn(); cur = con.cursor()
    q = "SELECT date,type,amount_tl,note FROM supplier_ledger WHERE supplier_id=?"
    params = [supplier_id]
    if start: q += " AND date>=?"; params.append(start)
    if end: q += " AND date<=?"; params.append(end)
    q += " ORDER BY id DESC"
    cur.execute(q, tuple(params)); rows = cur.fetchall(); con.close(); return rows

def cari_odeme_ekle(supplier_id, amount_tl, note):
    now = datetime.datetime.now().isoformat(timespec="seconds")
    con = _conn(); cur = con.cursor()
    cur.execute("INSERT INTO supplier_ledger(supplier_id,date,type,amount_tl,note) VALUES(?,?,?,?,?)",
                (supplier_id, now, "payment", -abs(amount_tl), note))
    cur.execute("UPDATE suppliers SET balance_tl = COALESCE(balance_tl,0)-? WHERE id=?", (abs(amount_tl), supplier_id))
    con.commit(); con.close()

def kasa_hareket_ekle(tip, tutar, note):
    now = datetime.datetime.now().isoformat(timespec="seconds")
    con = _conn(); cur = con.cursor()
    cur.execute("INSERT INTO cash_movements(date,type,amount_tl,note) VALUES(?,?,?,?)", (now, tip, tutar, note))
    con.commit(); con.close()

def kasa_raporu(start=None, end=None):
    con = _conn(); cur = con.cursor()
    q = "SELECT date,type,amount_tl,note FROM cash_movements WHERE 1=1"
    params = []
    if start: q += " AND date>=?"; params.append(start)
    if end: q += " AND date<=?"; params.append(end)
    q += " ORDER BY id DESC"
    cur.execute(q, tuple(params)); rows = cur.fetchall()
    gelir = sum(r[2] for r in rows if r[1]=='income')
    gider = sum(-r[2] for r in rows if r[1]=='expense')
    con.close(); return rows, gelir, gider, (gelir - gider)

def z_raporu_yaz():
    con = _conn(); cur = con.cursor()
    today = datetime.date.today().isoformat()
    cur.execute("SELECT total_tl FROM sales WHERE date LIKE ?", (today+"%",))
    toplam = sum(r[0] for r in cur.fetchall())
    yol = os.path.join(os.path.dirname(__file__), f"z_raporu_{today}.txt")
    with open(yol, "w", encoding="utf-8") as f:
        f.write(f"Z RAPORU - {today}\nToplam Satış: {toplam:.2f} TL\n")
    con.close(); return yol

def tree_rows_for_stock():
    con = _conn(); cur = con.cursor()
    cur.execute("""
        SELECT p.barcode, p.name, p.stock, p.sale_price_tl, p.id, COALESCE(s.name,'') as supplier_name
        FROM products p LEFT JOIN suppliers s ON s.id=p.supplier_id ORDER BY p.name
    """)
    rows = cur.fetchall(); con.close(); return rows

def stok_raporu(barcode, start=None, end=None):
    con = _conn(); cur = con.cursor()
    cur.execute("SELECT id FROM products WHERE barcode=?", (barcode,))
    r = cur.fetchone()
    if not r: con.close(); return []
    pid = r[0]
    q = "SELECT date,type,qty,ref,note FROM stock_movements WHERE product_id=?"
    params = [pid]
    if start: q += " AND date>=?"; params.append(start)
    if end: q += " AND date<=?"; params.append(end)
    q += " ORDER BY id DESC"
    cur.execute(q, tuple(params)); rows = cur.fetchall(); con.close(); return rows
