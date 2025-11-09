import sqlite3, os, hashlib, datetime, json
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def baglan(): 
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def sifrele(pw): 
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def kurulum():
    c = baglan(); cur=c.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT, role TEXT CHECK(role IN ('admin','kasiyer')) NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT, barcode TEXT UNIQUE, name TEXT, purchase_price_tl REAL DEFAULT 0, sale_price_tl REAL DEFAULT 0, kdv INTEGER DEFAULT 20, stock INTEGER DEFAULT 0, expiry_date TEXT, category TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS suppliers(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, address TEXT, balance_tl REAL DEFAULT 0)")
    cur.execute("CREATE TABLE IF NOT EXISTS purchases(id INTEGER PRIMARY KEY AUTOINCREMENT, supplier_id INTEGER, date TEXT, total_tl REAL, items_json TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS sales(id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, total_tl REAL, payment_type TEXT CHECK(payment_type IN ('cash','card')), cashier_id INTEGER, items_json TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS supplier_ledger(id INTEGER PRIMARY KEY AUTOINCREMENT, supplier_id INTEGER, date TEXT, type TEXT CHECK(type IN ('purchase','payment','refund')), amount_tl REAL, note TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS cash_register(id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT UNIQUE, opening_balance_tl REAL, closing_balance_tl REAL, sales_total_tl REAL, expenses_tl REAL, note TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS currency_rates(id INTEGER PRIMARY KEY AUTOINCREMENT, currency TEXT, rate_to_tl REAL, last_update TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS stock_movements(id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, date TEXT, type TEXT CHECK(type IN ('in','out','adjust')), qty INTEGER, ref TEXT, note TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS cash_movements(id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT CHECK(type IN ('income','expense')), amount_tl REAL, note TEXT NOT NULL)")
    c.commit()
    # tohum
    if cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]==0:
        cur.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)", ("admin", sifrele("admin"), "admin"))
    if cur.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0]==0:
        cur.execute("INSERT INTO suppliers(name,phone,address,balance_tl) VALUES('Toptancı A','+90 555 111 11 11','İstanbul',1500)")
        cur.execute("INSERT INTO suppliers(name,phone,address,balance_tl) VALUES('Toptancı B','+90 555 222 22 22','Ankara',-250)")
    if cur.execute("SELECT COUNT(*) FROM products").fetchone()[0]==0:
        cur.execute("INSERT INTO products(barcode,name,purchase_price_tl,sale_price_tl,kdv,stock,category) VALUES(?,?,?,?,?,?,?)",("8691234567890","Marlboro Red 20",52,60,20,20,"Sigara"))
        cur.execute("INSERT INTO products(barcode,name,purchase_price_tl,sale_price_tl,kdv,stock,category) VALUES(?,?,?,?,?,?,?)",("8699876543210","Camel Soft 20",50,58,20,12,"Sigara"))
        cur.execute("INSERT INTO products(barcode,name,purchase_price_tl,sale_price_tl,kdv,stock,category) VALUES(?,?,?,?,?,?,?)",("8690001112223","Efes Pilsen 50cl",25,35,20,30,"Alkollü"))
    if cur.execute("SELECT COUNT(*) FROM stock_movements").fetchone()[0]==0:
        now = datetime.datetime.now().isoformat(timespec='seconds')
        for bc,t,qty in [("8691234567890","in",10),("8691234567890","out",2),("8699876543210","in",8),("8699876543210","out",1),("8690001112223","in",20)]:
            pid = cur.execute("SELECT id FROM products WHERE barcode=?", (bc,)).fetchone()[0]
            cur.execute("INSERT INTO stock_movements(product_id,date,type,qty,ref,note) VALUES(?,?,?,?,?,?)",(pid,now,t,qty,"seed",""))
    c.commit(); c.close()

def giris(u, p):
    c=baglan(); cur=c.cursor(); cur.execute("SELECT id,role,password_hash FROM users WHERE username=?",(u,)); r=cur.fetchone(); c.close()
    if not r: return None
    return {"id":r[0],"username":u,"role":r[1]} if r[2]==sifrele(p) else None

def urun_barkod(barcode):
    c=baglan(); cur=c.cursor(); cur.execute("SELECT id,barcode,name,sale_price_tl,kdv,stock FROM products WHERE barcode=?",(barcode,)); r=cur.fetchone(); c.close()
    if not r: return None
    return {"id":r[0],"barcode":r[1],"name":r[2],"sale_price_tl":r[3],"kdv":r[4],"stock":r[5]}

def urun_kaydet_veya_guncelle(barcode,name,sale_price_tl,kdv=20,category=None):
    c=baglan(); cur=c.cursor(); r=cur.execute("SELECT id FROM products WHERE barcode=?",(barcode,)).fetchone()
    if r:
        cur.execute("UPDATE products SET name=?, sale_price_tl=?, kdv=?, category=COALESCE(?,category) WHERE id=?", (name,sale_price_tl,kdv,category,r[0])); pid=r[0]
    else:
        cur.execute("INSERT INTO products(barcode,name,sale_price_tl,kdv,stock,category) VALUES(?,?,?,?,0,?)",(barcode,name,sale_price_tl,kdv,category)); pid=cur.lastrowid
    c.commit(); c.close(); return pid

def stok_degistir(product_id, delta, mov_type, ref="manuel", note=""):
    c=baglan(); cur=c.cursor()
    cur.execute("UPDATE products SET stock=CAST(COALESCE(stock,0) AS INTEGER)+CAST(? AS INTEGER) WHERE id=?", (int(delta), product_id))
    cur.execute("INSERT INTO stock_movements(product_id,date,type,qty,ref,note) VALUES(?,?,?,?,?,?)", (product_id, datetime.datetime.now().isoformat(timespec='seconds'), mov_type, int(abs(delta)), ref, note))
    c.commit(); c.close()

def satis_kaydet(cashier_id, items, total_tl, payment_type):
    c=baglan(); cur=c.cursor(); now=datetime.datetime.now().isoformat(timespec='seconds')
    cur.execute("INSERT INTO sales(date,total_tl,payment_type,cashier_id,items_json) VALUES(?,?,?,?,?)",(now,total_tl,payment_type,cashier_id,json.dumps(items,ensure_ascii=False)))
    sale_id=cur.lastrowid
    for it in items:
        cur.execute("UPDATE products SET stock = CAST(COALESCE(stock,0) AS INTEGER) - CAST(? AS INTEGER) WHERE id=?", (int(it['qty']), it['product_id']))
        cur.execute("INSERT INTO stock_movements(product_id,date,type,qty,ref,note) VALUES(?,?,?,?,?,?)", (it['product_id'], now, "out", int(it['qty']), f"satis:{sale_id}", it['name']))
    c.commit(); c.close(); return sale_id
